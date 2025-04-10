"""
Summary generator module for the meeting recorder application.
"""

import os
import openai
import requests
import sys

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.config import Config

class SummaryGenerator:
    """摘要生成器類，可以使用多種模型生成會議摘要。"""

    def __init__(self):
        """初始化摘要生成器。"""
        self.config = Config()
        self.api_key_set = self._force_set_api_key()
        self.last_summary = ""

    def _force_set_api_key(self):
        """設置 OpenAI API 密鑰。"""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("警告: 未設置 OPENAI_API_KEY 環境變量，摘要生成功能將無法使用")
            return False
        openai.api_key = api_key
        return True

    def generate_summary(self, transcript, meeting_title=None, participants=None):
        """
        根據會議轉錄生成摘要。
        
        參數:
            transcript (str): 會議轉錄文本。
            meeting_title (str, optional): 會議標題。
            participants (list, optional): 參與者列表。
            
        返回:
            str: 生成的摘要。
        """
        # 檢查是否使用 Ollama 本地模型
        use_ollama = hasattr(self.config, 'use_local_model') and self.config.use_local_model
        
        if use_ollama:
            return self._generate_summary_ollama(transcript, meeting_title, participants)
        else:
            return self._generate_summary_openai(transcript, meeting_title, participants)

    def _generate_summary_openai(self, transcript, meeting_title=None, participants=None):
        """使用 OpenAI API 生成摘要。"""
        if not self.api_key_set:
            return "錯誤: 未設置 OpenAI API 密鑰，無法生成摘要。請在環境變量或 .env 文件中設置 OPENAI_API_KEY。"
            
        try:
            # 從配置中獲取模型和溫度
            model = self.config.get_openai_config().get("summary_model", "gpt-4")
            temperature = 0.5  # 降低溫度以獲得更一致的輸出
            
            # 改進的系統提示詞
            system_prompt = """你是一位專業的會議摘要專家，擅長將冗長的會議記錄轉化為清晰、結構化且信息豐富的摘要。
你的任務是分析會議轉錄內容，提取關鍵信息，並生成一份全面的會議摘要報告。

請嚴格按照以下結構輸出摘要：

1. 會議標題：[提供簡潔明確的會議標題，如果已提供則使用]

2. 日期：[如果在轉錄中提到日期，請提取；否則可以省略]

3. 參與者：[列出所有參與會議的人員，如有提供]

4. 摘要：[用3-5個段落概述會議的主要內容和目的，突出最重要的討論要點]

5. 關鍵點：[以項目符號列出5-8個會議中討論的最重要觀點或信息]

6. 行動項目：[以項目符號列出會議中確定的所有需要採取的行動，包括負責人和截止日期（如有提及）]

7. 決策：[以項目符號列出會議中做出的所有決定]

請使用繁體中文輸出，保持專業、簡潔的語言風格。確保摘要能夠讓未參加會議的人清楚了解會議內容和結果。
如果某個部分在會議記錄中沒有相關信息，可以省略該部分，但不要編造信息。"""
            
            # 添加會議標題和參與者信息到提示中
            user_prompt = f"請根據以下會議轉錄內容，生成一份專業的會議摘要：\n\n"
            
            if meeting_title:
                user_prompt += f"會議標題: {meeting_title}\n"
                
            if participants and len(participants) > 0:
                user_prompt += f"參與者: {', '.join(participants)}\n"
                
            user_prompt += f"\n會議轉錄內容:\n{transcript}\n\n請提供一份結構化的會議摘要，包含上述要求的所有部分。特別注意識別關鍵討論點、行動項目和決策。"
            
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=4000
            )
            
            summary = response.choices[0].message.content
            self.last_summary = self._clean_summary(summary)
            return self.last_summary
            
        except Exception as e:
            return f"生成摘要時發生錯誤: {str(e)}"

    def _generate_summary_ollama(self, transcript, meeting_title=None, participants=None):
        """使用 Ollama API 生成摘要。"""
        try:
            # 從配置中獲取 Ollama 設置
            ollama_url = self.config.ollama_url
            model = self.config.gemma_model
            temperature = 0.5  # 降低溫度以獲得更一致的輸出
            
            # 改進的系統提示詞
            system_prompt = """你是一位專業的會議摘要專家，擅長將冗長的會議記錄轉化為清晰、結構化且信息豐富的摘要。
你的任務是分析會議轉錄內容，提取關鍵信息，並生成一份全面的會議摘要報告。

請嚴格按照以下結構輸出摘要：

1. 會議標題：[提供簡潔明確的會議標題，如果已提供則使用]

2. 日期：[如果在轉錄中提到日期，請提取；否則可以省略]

3. 參與者：[列出所有參與會議的人員，如有提供]

4. 摘要：[用3-5個段落概述會議的主要內容和目的，突出最重要的討論要點]

5. 關鍵點：[以項目符號列出5-8個會議中討論的最重要觀點或信息]

6. 行動項目：[以項目符號列出會議中確定的所有需要採取的行動，包括負責人和截止日期（如有提及）]

7. 決策：[以項目符號列出會議中做出的所有決定]

請使用繁體中文輸出，保持專業、簡潔的語言風格。確保摘要能夠讓未參加會議的人清楚了解會議內容和結果。
如果某個部分在會議記錄中沒有相關信息，可以省略該部分，但不要編造信息。"""
            
            # 添加會議標題和參與者信息到提示中
            user_prompt = f"請根據以下會議轉錄內容，生成一份專業的會議摘要：\n\n"
            
            if meeting_title:
                user_prompt += f"會議標題: {meeting_title}\n"
                
            if participants and len(participants) > 0:
                user_prompt += f"參與者: {', '.join(participants)}\n"
                
            user_prompt += f"\n會議轉錄內容:\n{transcript}\n\n請提供一份結構化的會議摘要，包含上述要求的所有部分。特別注意識別關鍵討論點、行動項目和決策。"
            
            # 構建請求
            payload = {
                "model": model,
                "prompt": user_prompt,
                "system": system_prompt,
                "temperature": temperature,
                "stream": False
            }
            
            # 發送請求
            response = requests.post(ollama_url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get("response", "")
                self.last_summary = self._clean_summary(summary)
                return self.last_summary
            else:
                return f"Ollama API 返回錯誤: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"使用 Ollama 生成摘要時發生錯誤: {str(e)}"

    def _clean_summary(self, summary):
        """清理摘要文本。"""
        # 移除多餘的空行
        summary = "\n".join([line for line in summary.split("\n") if line.strip()])
        return summary
        
    def get_summary(self):
        """獲取最近生成的摘要。"""
        return self.last_summary
