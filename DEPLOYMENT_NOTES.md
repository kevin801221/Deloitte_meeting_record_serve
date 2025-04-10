# YCM 智能會議記錄助手 - 部署問題與解決方案

## 部署過程中遇到的問題

### 1. Gunicorn 依賴缺失

**問題描述**：
在 Cloud Run 部署過程中，出現 "unknown instruction: gunicorn" 錯誤，表示容器中缺少 gunicorn 包。

**原因**：
Dockerfile 中的啟動腳本使用了 gunicorn 命令，但沒有在 Python 依賴中安裝 gunicorn 包。

**解決方案**：
在 Dockerfile 中添加 gunicorn 依賴：
```dockerfile
RUN pip install --no-cache-dir \
    fastapi==0.95.0 \
    uvicorn==0.21.1 \
    gunicorn==20.1.0 \  # 添加 gunicorn 依賴
    python-multipart==0.0.6 \
    openai==0.27.4 \
    # 其他依賴...
```

### 2. 啟動腳本語法錯誤

**問題描述**：
Dockerfile 中創建啟動腳本的方式可能在某些 Docker 環境中導致語法錯誤。

**原因**：
使用多行字符串創建腳本文件時，不同的 Docker 環境可能對換行符和引號的處理方式不同。

**解決方案**：
使用更可靠的方式創建啟動腳本，逐行添加內容：
```dockerfile
# 創建啟動腳本
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo '# 啟動 API 服務 (使用 gunicorn 替代 uvicorn，並指定每個工作進程只用 1 個線程)' >> /app/start.sh && \
    echo 'gunicorn --threads 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:3000 api.main:app &' >> /app/start.sh && \
    echo '# 等待 API 服務啟動' >> /app/start.sh && \
    echo 'sleep 5' >> /app/start.sh && \
    echo '# 啟動 Nginx' >> /app/start.sh && \
    echo 'nginx -g "daemon off;"' >> /app/start.sh && \
    chmod 755 /app/start.sh
```

### 3. API 基礎 URL 設置錯誤

**問題描述**：
部署到 Cloud Run 後，前端無法連接到後端 API，出現 "Failed to fetch" 錯誤。

**原因**：
前端 JavaScript 中的 API 基礎 URL 設置為硬編碼的值 `'https://your-cloud-run-url.run.app/api'`，而不是實際的 Cloud Run URL。

**解決方案**：
修改 script.js 文件，使用動態獲取的主機名：
```javascript
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? `http://${window.location.hostname}:${window.location.port}/api` 
    : `https://${window.location.hostname}/api`;
```

### 4. API 文檔無法訪問

**問題描述**：
訪問 `/docs` 端點時沒有內容，無法查看 API 文檔。

**原因**：
Nginx 配置中只有 `/api/` 和 `/health` 路徑被配置為代理到 FastAPI 服務，但 `/docs` 路徑沒有被包含在內。

**解決方案**：
在 Nginx 配置中添加對 `/docs` 和相關路徑的支持：
```nginx
location ~ ^/(docs|openapi.json|redoc) { \
    proxy_pass http://localhost:3000; \
    proxy_http_version 1.1; \
    proxy_set_header Upgrade $http_upgrade; \
    proxy_set_header Connection "upgrade"; \
    proxy_set_header Host $host; \
    proxy_cache_bypass $http_upgrade; \
}
```

## API 密鑰處理機制

應用程序支持兩種方式獲取 OpenAI API 密鑰：

1. **用戶提供的 API 密鑰**：
   - 用戶在前端界面輸入自己的 OpenAI API 密鑰
   - 密鑰存儲在瀏覽器的 localStorage 中
   - 每次請求時，前端會從 localStorage 中獲取密鑰並發送到後端

2. **環境變量中的 API 密鑰**：
   - 在 Cloud Run 部署配置中設置 `OPENAI_API_KEY` 環境變量
   - 當用戶沒有提供 API 密鑰時，系統會使用這個環境變量

系統會按照以下順序尋找 API 密鑰：
1. 首先檢查請求頭中的 `X-API-KEY`（用戶從前端提供的密鑰）
2. 如果沒有，則檢查環境變量 `OPENAI_API_KEY`（部署時設置的密鑰）
3. 如果兩者都沒有，則返回 401 錯誤

## 部署後的檢查清單

- [x] 確認 gunicorn 依賴已添加到 Dockerfile
- [x] 確認啟動腳本創建方式正確
- [x] 確認前端 API 基礎 URL 設置正確
- [x] 確認 Nginx 配置支持 API 文檔訪問
- [x] 確認 API 密鑰處理機制正常工作
- [x] 確認上傳大文件的限制已設置（目前為 100MB）
- [x] 確認健康檢查端點正常工作

## 注意事項

1. **API 密鑰安全**：
   - 不要將 API 密鑰提交到版本控制系統中
   - 在生產環境中，使用 Cloud Run 的環境變量或密鑰管理服務存儲 API 密鑰

2. **資源限制**：
   - 監控 Cloud Run 的資源使用情況，特別是在處理大型音頻文件時
   - 考慮設置適當的超時時間和內存限制

3. **日誌和監控**：
   - 定期檢查 Cloud Run 日誌，查找潛在問題
   - 考慮添加更詳細的日誌記錄和監控

4. **更新依賴**：
   - 定期更新 Python 依賴，特別是 OpenAI API 和 FastAPI
   - 測試更新後的依賴是否與現有代碼兼容
