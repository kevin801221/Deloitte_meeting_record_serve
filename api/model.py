"""
共用模型和日誌配置

此模塊包含 API 使用的共用資料模型和日誌配置
"""

from pydantic import BaseModel
from typing import List, Optional
import logging
import os

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'api.log'),
            mode='a'
        ) if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')) else logging.NullHandler()
    ]
)

logger = logging.getLogger("meeting_api")

# 文字摘要請求模型
class TextSummaryRequest(BaseModel):
    text: str
    meeting_title: Optional[str] = None
    participants: Optional[List[str]] = None

# 摘要回應模型
class SummaryResponse(BaseModel):
    summary: str

# 音頻處理請求模型
class AudioProcessRequest(BaseModel):
    audio_file_path: str
    meeting_title: Optional[str] = None
    participants: Optional[List[str]] = None

# 音頻轉文字請求模型
class AudioTextRequest(BaseModel):
    audio_file_path: str

# 轉錄回應模型
class TranscriptionResponse(BaseModel):
    transcription: str
    status: str
    message: Optional[str] = None

# 轉錄和摘要回應模型
class TranscriptionSummaryResponse(BaseModel):
    transcription: str
    summary: str
    status: str
    message: Optional[str] = None