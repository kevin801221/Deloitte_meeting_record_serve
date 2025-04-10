import os
import openai
import datetime
import sys
from pathlib import Path

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.config import Config

class Transcriber:
    """音頻轉錄器類，使用 OpenAI Whisper API 將音頻轉換為文本。"""

    def __init__(self):
        """初始化轉錄器。"""
        self.config = Config()
        self.api_key_set = self._force_set_api_key()
        self.transcriptions = []

    def _force_set_api_key(self):
        """設置 OpenAI API 密鑰。"""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("警告: 未設置 OPENAI_API_KEY 環境變量，轉錄功能將無法使用")
            return False
        openai.api_key = api_key
        return True

    def transcribe_audio(self, audio_path):
        """
        將音頻文件轉錄為文本。
        
        參數:
            audio_path (str): 音頻文件的路徑。
            
        返回:
            str: 轉錄的文本。
        """
        if not self.api_key_set:
            return "錯誤: 未設置 OpenAI API 密鑰，無法進行轉錄。請在環境變量或 .env 文件中設置 OPENAI_API_KEY。"
            
        try:
            # 獲取配置
            model = self.config.get_openai_config()["transcription_model"]
            language = self.config.language
            
            # 檢查文件是否存在
            if not os.path.exists(audio_path):
                return f"錯誤: 音頻文件不存在: {audio_path}"
            
            # 讀取音頻文件
            audio_file = open(audio_path, "rb")
            
            # 調用 OpenAI API 進行轉錄
            transcription_params = {
                "model": model,
                "file": audio_file,
                "response_format": "text"
            }
            
            # 添加語言參數
            if language != "auto":
                transcription_params["language"] = language
            
            # 執行轉錄
            transcript = openai.Audio.transcribe(**transcription_params)
            
            # 保存轉錄結果
            self.add_transcription(transcript)
            
            return transcript
                
        except Exception as e:
            return f"轉錄過程中發生錯誤: {str(e)}"
            
    def add_transcription(self, text):
        """添加轉錄結果到歷史記錄。"""
        self.transcriptions.append({
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "text": text
        })
        
    def get_all_transcriptions(self):
        """獲取所有轉錄結果。"""
        return self.transcriptions
        
    def get_combined_text(self):
        """獲取所有轉錄結果合併為一個文本。"""
        return "\n".join([t["text"] for t in self.transcriptions])
        
    def clear_transcriptions(self):
        """清空轉錄歷史記錄。"""
        self.transcriptions = []
