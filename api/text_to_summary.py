"""
文字轉摘要 API
提供將會議文字記錄轉換為結構化摘要的 API 端點
"""

import os
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("text_to_summary_api")

from fastapi import APIRouter, HTTPException, FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import sys

# 添加項目根目錄到 Python 路徑，以便正確導入模塊
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 添加 AI_meeting_by_Gradio 目錄到 Python 路徑
ai_meeting_dir = os.path.join(os.path.dirname(__file__), '..', 'AI_meeting_by_Gradio')
if ai_meeting_dir not in sys.path:
    sys.path.append(ai_meeting_dir)

# 導入現有的摘要模組
from core.summary.generator import SummaryGenerator

# 定義請求和響應模型
class TextSummaryRequest(BaseModel):
    """文字轉摘要的請求模型"""
    text: str
    meeting_title: Optional[str] = ""
    participants: Optional[List[str]] = None

class SummaryResponse(BaseModel):
    """摘要響應模型"""
    summary: str
    status: str = "success"
    message: Optional[str] = None

# 創建 APIRouter
router = APIRouter()

# 初始化摘要生成器
summary_generator = SummaryGenerator()

@router.post("/api/text-to-summary", response_model=SummaryResponse)
async def text_to_summary(request: TextSummaryRequest, x_api_key: Optional[str] = Header(None)):
    """
    將會議文字記錄轉換為結構化摘要
    
    - **text**: 會議文字記錄
    - **meeting_title**: 會議標題（可選）
    - **participants**: 參與者列表（可選）
    - **x_api_key**: OpenAI API 密鑰（可從請求頭獲取）
    
    返回生成的會議摘要
    """
    try:
        # 檢查 API 密鑰
        api_key = x_api_key if x_api_key else os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=401, detail="未提供 OpenAI API 密鑰，請在請求頭中添加 X-API-KEY 或設置環境變數 OPENAI_API_KEY")
        
        # 臨時設置 OpenAI API 密鑰
        os.environ["OPENAI_API_KEY"] = api_key
        
        # 使用現有的摘要生成器生成摘要
        participants = request.participants if request.participants else []
        summary = summary_generator.generate_summary(
            request.text, 
            meeting_title=request.meeting_title, 
            participants=participants
        )
        
        return SummaryResponse(summary=summary)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"處理文字摘要時發生錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=f"處理文字摘要時發生錯誤: {str(e)}")

# 創建 FastAPI 應用
app = FastAPI(title="文字轉摘要 API", description="提供將會議文字記錄轉換為結構化摘要的 API")

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
    uvicorn.run("api.text_to_summary:app", host="0.0.0.0", port=8001, reload=True)
