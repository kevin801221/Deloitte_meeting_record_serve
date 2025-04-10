FROM python:3.10-slim AS backend

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    portaudio19-dev \
    python3-pyaudio \
    python3-dev \
    build-essential \
    curl \
    nginx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Python 依賴
RUN pip install --no-cache-dir \
    fastapi==0.95.0 \
    uvicorn==0.21.1 \
    gunicorn==20.1.0 \
    python-multipart==0.0.6 \
    openai==0.27.4 \
    pydantic==1.10.7 \
    python-dotenv==1.0.0 \
    numpy==1.24.0 \
    pydub==0.25.1 \
    SpeechRecognition==3.10.0 \
    requests==2.28.2 \
    gradio==3.50.2 \
    whisper==1.1.10

# 創建必要的目錄
RUN mkdir -p /app/uploads /app/temp /app/AI_meeting_by_Gradio/exports /app/AI_meeting_by_Gradio/uploads /app/data /app/meeting_exports

# 複製 API 文件
COPY . /app

# 複製前端文件
COPY ./frontend /app/frontend

# 配置 Nginx
RUN echo 'server { \
    listen       8080; \
    server_name  localhost; \
    client_max_body_size 100M; \
    location / { \
        root   /app/frontend; \
        index  index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
    location /api/ { \
        proxy_pass http://localhost:3000; \
        proxy_http_version 1.1; \
        proxy_set_header Upgrade $http_upgrade; \
        proxy_set_header Connection "upgrade"; \
        proxy_set_header Host $host; \
        proxy_cache_bypass $http_upgrade; \
        proxy_read_timeout 300s; \
        proxy_connect_timeout 300s; \
        proxy_send_timeout 300s; \
    } \
    location ~ ^/(docs|openapi.json|redoc) { \
        proxy_pass http://localhost:3000; \
        proxy_http_version 1.1; \
        proxy_set_header Upgrade $http_upgrade; \
        proxy_set_header Connection "upgrade"; \
        proxy_set_header Host $host; \
        proxy_cache_bypass $http_upgrade; \
    } \
    location /health { \
        return 200 "healthy\\n"; \
    } \
}' > /etc/nginx/conf.d/default.conf

# 設置環境變量 (部署時需要設置 OPENAI_API_KEY 環境變量)
# 請勿在此處直接填寫 API 密鑰，而是在部署時通過環境變量提供
# ENV OPENAI_API_KEY="YOUR_DEFAULT_API_KEY_HERE"

# 創建啟動腳本
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo '# 啟動 API 服務 (使用 gunicorn 替代 uvicorn，並指定每個工作進程只用 1 個線程)' >> /app/start.sh && \
    echo 'gunicorn --threads 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:3000 api.main:app &' >> /app/start.sh && \
    echo '# 等待 API 服務啟動' >> /app/start.sh && \
    echo 'sleep 5' >> /app/start.sh && \
    echo '# 啟動 Nginx' >> /app/start.sh && \
    echo 'nginx -g "daemon off;"' >> /app/start.sh && \
    chmod 755 /app/start.sh

# 暴露端口 (Cloud Run 要求使用 8080 端口)
EXPOSE 8080
# 健康檢查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
# 啟動服務
CMD ["/app/start.sh"]
