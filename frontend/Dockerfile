FROM nginx:alpine

# 複製靜態文件到 Nginx 的默認目錄
COPY . /usr/share/nginx/html/

# 配置 Nginx 以支持 SPA 路由和 API 代理
RUN echo 'server { \
    listen       80; \
    server_name  localhost; \
    location / { \
        root   /usr/share/nginx/html; \
        index  index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
    # 配置 API 代理 \
    location /api/ { \
        proxy_pass http://api:8080; \
        proxy_http_version 1.1; \
        proxy_set_header Upgrade $http_upgrade; \
        proxy_set_header Connection "upgrade"; \
        proxy_set_header Host $host; \
        proxy_cache_bypass $http_upgrade; \
        # 增加超時時間以處理長時間運行的請求 \
        proxy_read_timeout 300s; \
        proxy_connect_timeout 300s; \
        proxy_send_timeout 300s; \
    } \
}' > /etc/nginx/conf.d/default.conf

# 健康檢查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:80 || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
