"""
錄音到摘要 API
提供將會議錄音轉換為文字並生成結構化摘要的 API 端點
"""
import os
import tempfile
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import sys

# 添加項目根目錄到 Python 路徑，以便正確導入模塊
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("audio_to_summary_api")

# 添加 AI_meeting_by_Gradio 目錄到 Python 路徑
ai_meeting_dir = os.path.join(os.path.dirname(__file__), '..', 'AI_meeting_by_Gradio')
if ai_meeting_dir not in sys.path:
    sys.path.append(ai_meeting_dir)

# 導入現有的轉錄和摘要模組
from core.transcription.transcriber import Transcriber
from core.summary.generator import SummaryGenerator

# 定義模型
class AudioProcessRequest(BaseModel):
    audio_file_path: str
    meeting_title: Optional[str] = None
    participants: Optional[List[str]] = None

class TranscriptionSummaryResponse(BaseModel):
    transcription: str
    summary: str
    status: str
    message: Optional[str] = None

# 創建 APIRouter
router = APIRouter()

# 初始化轉錄器和摘要生成器
transcriber = Transcriber()
summary_generator = SummaryGenerator()

@router.post("/api/audio-to-summary", response_model=TranscriptionSummaryResponse)
async def audio_to_summary(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    meeting_title: str = Form(""),
    participants: str = Form(""),
    x_api_key: Optional[str] = Header(None)
):
    """
    處理上傳的音頻文件，進行轉錄並生成摘要
    
    - **file**: 上傳的音頻文件（WAV、MP3、M4A 等格式）
    - **meeting_title**: 會議標題（可選）
    - **participants**: 參與者列表，以逗號分隔（可選）
    - **x_api_key**: OpenAI API 密鑰（可從請求頭獲取）
    
    返回轉錄文本和生成的會議摘要
    """
    try:
        # 檢查 API 密鑰
        api_key = x_api_key if x_api_key else os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=401, detail="未提供 OpenAI API 密鑰，請在請求頭中添加 X-API-KEY 或設置環境變數 OPENAI_API_KEY")
        
        # 臨時設置 OpenAI API 密鑰
        os.environ["OPENAI_API_KEY"] = api_key
        
        # 解析參與者列表
        participants_list = [p.strip() for p in participants.split(",") if p.strip()]
        
        # 保存上傳的文件
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file.filename)
        
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(await file.read())
        
        # 轉錄音頻文件
        transcription = transcriber.transcribe_audio(temp_file_path)
        
        if "失敗" in transcription or "錯誤" in transcription:
            # 清理臨時文件
            background_tasks.add_task(lambda: os.remove(temp_file_path) if os.path.exists(temp_file_path) else None)
            background_tasks.add_task(lambda: os.rmdir(temp_dir) if os.path.exists(temp_dir) else None)
            
            return TranscriptionSummaryResponse(
                transcription="",
                summary="",
                status="error",
                message=transcription
            )
        
        # 生成摘要
        summary = summary_generator.generate_summary(
            transcription, 
            meeting_title=meeting_title, 
            participants=participants_list
        )
        
        # 清理臨時文件
        background_tasks.add_task(lambda: os.remove(temp_file_path) if os.path.exists(temp_file_path) else None)
        background_tasks.add_task(lambda: os.rmdir(temp_dir) if os.path.exists(temp_dir) else None)
        
        return TranscriptionSummaryResponse(
            transcription=transcription,
            summary=summary,
            status="success"
        )
    except Exception as e:
        logger.error(f"處理音頻到摘要時發生錯誤: {str(e)}")
        return TranscriptionSummaryResponse(
            transcription="",
            summary="",
            status="error",
            message=f"處理音頻到摘要時發生錯誤: {str(e)}"
        )

@router.post("/api/process-audio-file", response_model=TranscriptionSummaryResponse)
async def process_audio_file_api(request: AudioProcessRequest, x_api_key: Optional[str] = Header(None)):
    """
    處理本地音頻文件，進行轉錄並生成摘要
    
    - **audio_file_path**: 本地音頻文件路徑
    - **meeting_title**: 會議標題（可選）
    - **participants**: 參與者列表（可選）
    - **x_api_key**: OpenAI API 密鑰（可從請求頭獲取）
    
    返回轉錄文本和生成的會議摘要
    """
    try:
        # 檢查 API 密鑰
        api_key = x_api_key if x_api_key else os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=401, detail="未提供 OpenAI API 密鑰，請在請求頭中添加 X-API-KEY 或設置環境變數 OPENAI_API_KEY")
        
        # 臨時設置 OpenAI API 密鑰
        os.environ["OPENAI_API_KEY"] = api_key
        
        # 檢查文件是否存在
        if not request.audio_file_path or not os.path.exists(request.audio_file_path):
            raise HTTPException(status_code=400, detail="音頻文件路徑無效或文件不存在")
        
        # 轉錄音頻文件
        transcription = transcriber.transcribe_audio(request.audio_file_path)
        
        if "失敗" in transcription or "錯誤" in transcription:
            return TranscriptionSummaryResponse(
                transcription="",
                summary="",
                status="error",
                message=transcription
            )
        
        # 生成摘要
        participants = request.participants if request.participants else []
        summary = summary_generator.generate_summary(
            transcription, 
            meeting_title=request.meeting_title, 
            participants=participants
        )
        
        return TranscriptionSummaryResponse(
            transcription=transcription,
            summary=summary,
            status="success"
        )
    except Exception as e:
        logger.error(f"處理音頻文件時發生錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=f"處理音頻文件時發生錯誤: {str(e)}")

# 創建 FastAPI 應用
app = FastAPI(title="錄音到摘要 API", description="提供將會議錄音轉換為文字並生成結構化摘要的 API")

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
    uvicorn.run("api.audio_to_summary:app", host="0.0.0.0", port=8002, reload=True)