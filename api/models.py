"""
會議摘要 API 的共用模型和配置
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 定義請求和響應模型
class TextSummaryRequest(BaseModel):
    """文字轉摘要的請求模型"""
    text: str
    meeting_title: Optional[str] = ""
    participants: Optional[List[str]] = None

class AudioProcessRequest(BaseModel):
    """音頻處理的請求模型"""
    audio_file_path: str
    meeting_title: Optional[str] = ""
    participants: Optional[List[str]] = None

class SummaryResponse(BaseModel):
    """摘要響應模型"""
    summary: str
    status: str = "success"
    message: Optional[str] = None

class TranscriptionSummaryResponse(BaseModel):
    """轉錄和摘要響應模型"""
    transcription: str
    summary: str
    status: str = "success"
    message: Optional[str] = None
