"""
會議摘要 API 主入口
整合文字轉摘要、音頻轉文字和音頻轉摘要的 API 服務
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
import sys
import os

# 添加項目根目錄到 Python 路徑，以便正確導入模塊
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 添加 AI_meeting_by_Gradio 目錄到 Python 路徑
ai_meeting_dir = os.path.join(os.path.dirname(__file__), '..', 'AI_meeting_by_Gradio')
if ai_meeting_dir not in sys.path:
    sys.path.append(ai_meeting_dir)

# 導入子模塊的路由
from api.text_to_summary import router as text_router
from api.audio_to_text import router as audio_text_router
from api.audio_to_summary import router as audio_summary_router

# 創建主應用
app = FastAPI(
    title="YCM 智能會議記錄助手 API",
    description="提供文字轉摘要、音頻轉文字和音頻轉摘要的 API 服務",
    version="1.0.0"
)

# 允許跨域請求 - 更詳細的配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許所有來源
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有方法
    allow_headers=["*"],  # 允許所有頭部
    expose_headers=["*"],  # 暴露所有頭部
    max_age=86400,  # 預檢請求結果的緩存時間（秒）
)

# 配置最大請求體積限制
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class LimitUploadSize(BaseHTTPMiddleware):
    def __init__(self, app, max_upload_size: int):
        super().__init__(app)
        self.max_upload_size = max_upload_size

    async def dispatch(self, request: Request, call_next):
        if request.method == 'POST':
            content_length = request.headers.get('content-length')
            if content_length:
                content_length = int(content_length)
                if content_length > self.max_upload_size:
                    return JSONResponse(
                        status_code=413,
                        content={"detail": f"上傳文件太大。最大允許大小為 {self.max_upload_size / 1024 / 1024:.1f} MB"}
                    )
        return await call_next(request)

# 添加最大上傳大小限制中間件 (100MB)
app.add_middleware(LimitUploadSize, max_upload_size=100 * 1024 * 1024)

# 將子模塊的路由添加到主應用
app.include_router(text_router, tags=["文字轉摘要"])
app.include_router(audio_text_router, tags=["音頻轉文字"])
app.include_router(audio_summary_router, tags=["音頻轉摘要"])

# 添加 OPTIONS 方法的全局處理
@app.options("/{full_path:path}")
async def options_handler(request: Request):
    """處理所有 OPTIONS 請求"""
    return JSONResponse(
        status_code=200,
        content={"detail": "OK"}
    )

@app.get("/", include_in_schema=False)
async def root():
    """重定向到 API 文檔"""
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["健康檢查"])
async def health_check():
    """API 健康檢查端點"""
    return {"status": "healthy"}

if __name__ == "__main__":
    # 使用字符串導入方式運行應用
    uvicorn.run("api.main:app", host="0.0.0.0", port=8080, reload=True)
