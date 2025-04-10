"""
YCM 智能會議記錄助手配置文件
此文件允許用戶自定義轉錄和摘要生成的模型和參數
"""

import os
from dotenv import load_dotenv

# 載入環境變量
load_dotenv()

# API 密鑰配置
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# 轉錄配置
TRANSCRIPTION_CONFIG = {
    # 轉錄模型: "whisper-1" 或其他 OpenAI 支持的模型
    "model": os.environ.get("TRANSCRIPTION_MODEL", "whisper-1"),
    # 語言: "zh" (中文), "en" (英文), "auto" (自動檢測)
    "language": os.environ.get("TRANSCRIPTION_LANGUAGE", "zh"),
}

# 摘要生成配置
SUMMARY_CONFIG = {
    # 提供者: "openai" 或 "ollama"
    "provider": os.environ.get("SUMMARY_PROVIDER", "openai"),
    
    # OpenAI 配置
    "model": os.environ.get("SUMMARY_MODEL", "gpt-4"),
    "temperature": float(os.environ.get("SUMMARY_TEMPERATURE", "0.7")),
    
    # Ollama 配置
    "ollama_host": os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
    "ollama_model": os.environ.get("OLLAMA_MODEL", "gemma3:12b"),
    
    # 通用配置
    "system_prompt": os.environ.get("SUMMARY_SYSTEM_PROMPT", 
        "你是一個專業的會議摘要助手，請根據會議轉錄內容生成一個結構化的會議摘要。"
        "摘要應包括：會議主題、主要討論點、決策和行動項目。請使用繁體中文。"),
}
