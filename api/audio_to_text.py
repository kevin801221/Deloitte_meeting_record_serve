"""
音頻轉文字 API
提供將會議錄音轉換為文字的 API 端點
"""

import os
import tempfile
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import sys


# 添加項目根目錄到 Python 路徑，以便正確導入模塊
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("audio_to_text_api")

# 添加 AI_meeting_by_Gradio 目錄到 Python 路徑
ai_meeting_dir = os.path.join(os.path.dirname(__file__), '..', 'AI_meeting_by_Gradio')
if ai_meeting_dir not in sys.path:
    sys.path.append(ai_meeting_dir)

# 導入現有的轉錄模組
from core.transcription.transcriber import Transcriber

# 定義直接在文件中的模型
class AudioTextRequest(BaseModel):
    audio_file_path: str

class TranscriptionResponse(BaseModel):
    transcription: str
    status: str
    message: Optional[str] = None

# 創建 APIRouter
router = APIRouter()

# 初始化轉錄器
transcriber = Transcriber()

@router.post("/api/audio-to-text")
async def audio_to_text(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    x_api_key: Optional[str] = Header(None)
):
    """
    處理上傳的音頻文件，進行轉錄
    
    - **file**: 上傳的音頻文件（WAV、MP3、M4A 等格式）
    - **x_api_key**: OpenAI API 密鑰（可從請求頭獲取）
    
    返回轉錄文本
    """
    try:
        # 檢查 API 密鑰
        api_key = x_api_key if x_api_key else os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=401, detail="未提供 OpenAI API 密鑰，請在請求頭中添加 X-API-KEY 或設置環境變數 OPENAI_API_KEY")
        
        # 臨時設置 OpenAI API 密鑰
        os.environ["OPENAI_API_KEY"] = api_key
        
        # 檢查文件是否為音頻文件
        content_type = file.content_type
        if not content_type or not content_type.startswith("audio/"):
            raise HTTPException(status_code=400, detail="請上傳有效的音頻文件")
        
        # 創建臨時文件
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file.filename)
        
        # 保存上傳的文件
        with open(temp_file_path, "wb") as buffer:
            contents = await file.read()
            buffer.write(contents)
        
        # 進行轉錄
        logger.info(f"開始轉錄文件: {file.filename}")
        transcription = transcriber.transcribe_audio(temp_file_path)
        
        # 清理臨時文件
        background_tasks.add_task(os.remove, temp_file_path)
        background_tasks.add_task(os.rmdir, temp_dir)
        
        return TranscriptionResponse(
            transcription=transcription,
            status="success"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"處理音頻轉文字時發生錯誤: {str(e)}")
        return TranscriptionResponse(
            transcription="",
            status="error",
            message=f"處理音頻轉文字時發生錯誤: {str(e)}"
        )

@router.post("/api/process-audio-text")
async def process_audio_text_api(request: AudioTextRequest, x_api_key: Optional[str] = Header(None)):
    """
    處理本地音頻文件，進行轉錄
    
    - **audio_file_path**: 本地音頻文件路徑
    - **x_api_key**: OpenAI API 密鑰（可從請求頭獲取）
    
    返回轉錄文本
    """
    try:
        # 檢查 API 密鑰
        api_key = x_api_key if x_api_key else os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=401, detail="未提供 OpenAI API 密鑰，請在請求頭中添加 X-API-KEY 或設置環境變數 OPENAI_API_KEY")
        
        # 臨時設置 OpenAI API 密鑰
        os.environ["OPENAI_API_KEY"] = api_key
        
        # 檢查文件是否存在
        if not os.path.exists(request.audio_file_path):
            raise HTTPException(status_code=400, detail="音頻文件不存在")
        
        # 進行轉錄
        logger.info(f"開始轉錄文件: {request.audio_file_path}")
        transcription = transcriber.transcribe_audio(request.audio_file_path)
        
        return TranscriptionResponse(
            transcription=transcription,
            status="success"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"處理音頻轉文字時發生錯誤: {str(e)}")
        return TranscriptionResponse(
            transcription="",
            status="error",
            message=f"處理音頻轉文字時發生錯誤: {str(e)}"
        )

# 創建 FastAPI 應用
app = FastAPI(title="音頻轉文字 API", description="提供將會議錄音轉換為文字的 API")

# 允許跨域請求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 將路由添加到應用
app.include_router(router)

# 獨立運行時使用
if __name__ == "__main__":
    # 使用字符串導入方式運行應用
    uvicorn.run("api.audio_to_text:app", host="0.0.0.0", port=8003, reload=True)