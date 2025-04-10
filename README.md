# YCM 智能會議記錄助手

## 簡介

YCM 智能會議記錄助手是一個強大的會議記錄工具，能夠自動錄製會議內容、轉錄語音為文字，並生成結構化的會議摘要。該應用程序利用先進的 OpenAI API 技術，幫助您高效地記錄和整理會議內容，節省寶貴的時間。

## 功能特點

- **語音錄製**：直接在應用中錄製會議音頻
- **音頻上傳**：支持上傳已有的會議錄音文件
- **語音轉文字**：使用 OpenAI Whisper 模型將語音自動轉換為文字
- **會議摘要生成**：使用 OpenAI GPT-4 模型生成結構化的會議摘要
- **會議記錄導出**：將會議記錄和摘要導出為文本文件
- **繁體中文支持**：完全支持繁體中文輸入和輸出
- **本地錄音一鍵摘要**：使用單一按鈕自動保存錄音並生成摘要
- **詳細使用手冊**：內建完整的使用指南，幫助用戶快速上手

## 系統需求

- Docker 和 Docker Compose（推薦使用最新版本）
- 網絡連接（用於 OpenAI API 調用）
- **OpenAI API 密鑰**（必需）
- 支持的操作系統：Windows、macOS、Linux

## 使用的模型

- **語音轉文字**：OpenAI Whisper 模型
- **摘要生成**：OpenAI GPT-4 模型

## 設置 OpenAI API 密鑰（必需）

YCM 智能會議記錄助手使用 OpenAI API 進行語音轉文字和摘要生成，因此**必須**設置 OpenAI API 密鑰。有以下幾種方式設置：

### 使用 Docker Compose（推薦）

1. 在 `docker-compose.yml` 文件所在的目錄中創建 `.env` 文件
2. 在文件中添加以下內容：
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
3. 使用 `docker-compose up -d` 啟動應用

### 直接在 docker-compose.yml 中設置

打開 `docker-compose.yml` 文件，找到以下部分並替換為您的 API 密鑰：
```yaml
environment:
  - OPENAI_API_KEY=your_openai_api_key_here
```

## 自定義配置選項

YCM 智能會議記錄助手提供了靈活的配置選項，允許您根據需求自定義轉錄和摘要生成功能。您可以通過設置環境變量來修改這些配置：

### 轉錄配置

- `TRANSCRIPTION_MODEL`: 設置用於語音轉文字的 OpenAI Whisper 模型（默認為 "whisper-1"）
- `TRANSCRIPTION_LANGUAGE`: 設置音頻語言（"zh" 為中文，"en" 為英文，"auto" 為自動檢測，默認為 "zh"）

### 摘要生成配置

#### 模型提供者選擇
- `SUMMARY_PROVIDER`: 設置摘要生成使用的提供者（"openai" 或 "ollama"，默認為 "openai"）

#### OpenAI 配置（當 SUMMARY_PROVIDER="openai" 時使用）
- `SUMMARY_MODEL`: 設置用於生成摘要的 OpenAI 模型（默認為 "gpt-4"）
- `SUMMARY_TEMPERATURE`: 設置生成摘要的創意度（0.0-2.0，默認為 0.7）

#### Ollama 配置（當 SUMMARY_PROVIDER="ollama" 時使用）
- `OLLAMA_HOST`: 設置 Ollama 服務的主機地址（默認為 "http://localhost:11434"）
- `OLLAMA_MODEL`: 設置用於生成摘要的 Ollama 模型（默認為 "gemma3:12b"）

#### 通用配置
- `SUMMARY_SYSTEM_PROMPT`: 自定義系統提示詞，指導摘要生成的風格和內容

### 配置示例

在 `.env` 文件中添加以下內容來自定義配置：

```
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# 轉錄配置
TRANSCRIPTION_MODEL=whisper-1
TRANSCRIPTION_LANGUAGE=zh

# 摘要生成配置 - 使用 OpenAI
SUMMARY_PROVIDER=openai
SUMMARY_MODEL=gpt-4
SUMMARY_TEMPERATURE=0.7
```

或者使用 Ollama 本地模型進行摘要生成：

```
# OpenAI API Key (仍然需要用於轉錄)
OPENAI_API_KEY=your_openai_api_key_here

# 轉錄配置
TRANSCRIPTION_MODEL=whisper-1
TRANSCRIPTION_LANGUAGE=zh

# 摘要生成配置 - 使用 Ollama 本地模型
SUMMARY_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gemma3:12b
SUMMARY_TEMPERATURE=0.7
```

> **重要提示**：即使使用 Ollama 本地模型進行摘要生成，您仍然需要設置 OpenAI API 密鑰用於音頻轉錄功能。

## 快速開始（Docker）

1. **克隆倉庫**：
   ```bash
   git clone https://github.com/your-username/YCM_meeting_record.git
   cd YCM_meeting_record
   ```

2. **設置 API 密鑰**：
   在項目根目錄創建 `.env` 文件，添加您的 OpenAI API 密鑰：
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

3. **啟動應用**：
   ```bash
   docker-compose up -d
   ```

4. **訪問應用**：
   打開瀏覽器，訪問 http://localhost:7860

## 使用指南

### 基本功能

1. **音頻轉文字**：
   - 點擊「音頻轉文字」標籤
   - 上傳您的會議錄音文件
   - 輸入會議標題和參與者信息（可選）
   - 點擊「轉換為文字」按鈕
   - 等待系統處理，處理時間取決於音頻長度

2. **音頻轉摘要**：
   - 點擊「音頻轉摘要」標籤
   - 上傳您的會議錄音文件
   - 輸入會議標題和參與者信息（可選）
   - 點擊「生成摘要」按鈕
   - 等待系統處理，這可能需要幾分鐘時間

3. **本地錄音功能**：
   - 點擊「本地錄音」標籤
   - 輸入會議標題（可選）
   - 點擊「開始錄音」按鈕開始錄製會議
   - 使用「暫停」、「繼續」和「停止」按鈕控制錄音過程
   - 錄音完成後，系統會自動保存錄音文件到您的本地設備
   - 點擊「生成最終摘要」按鈕，系統會自動處理錄音並生成摘要

4. **文字轉摘要功能**：
   - 點擊「文字轉摘要」標籤
   - 輸入會議標題和參與者信息（可選）
   - 在文本框中輸入或粘貼會議文字記錄
   - 點擊「生成摘要」按鈕
   - 等待系統處理，處理時間取決於文字長度

### 使用前準備

1. **設置 OpenAI API 密鑰**：
   - 點擊右上角的「設置 API 密鑰」按鈕
   - 輸入您的 OpenAI API 密鑰
   - 如果您沒有 API 密鑰，可以在 [OpenAI 官網](https://platform.openai.com/account/api-keys) 申請

2. **檢查 API 狀態**：
   - 頁面頂部顯示了三個 API 的狀態指示器
   - 確保它們都是綠色的，表示 API 可用

## 故障排除

- **轉錄或摘要功能無法使用**：
  - 檢查是否正確設置了 OpenAI API 密鑰
  - 確認 API 密鑰是否有效，以及是否有足夠的額度
  - 檢查網絡連接是否正常
  - 確保 API 狀態指示器顯示為綠色

- **錄音功能無法使用**：
  - 確保已授予瀏覽器麥克風訪問權限
  - 檢查麥克風設備是否正常工作
  - 在 Docker 環境中，確保設置了 `DOCKER_AUDIO_ENABLED=true`

- **上傳音頻文件時出現錯誤**：
  - 確保您的音頻文件格式受支持（WAV、MP3、M4A 等）
  - 檢查文件大小是否超過 100MB 的上傳限制
  - 如果遇到 HTTP 413 錯誤，表示文件過大，請嘗試縮短音頻長度或降低音頻質量

- **處理時間過長**：
  - 處理時間取決於音頻長度和文字數量
  - 較長的會議錄音可能需要更多時間處理
  - 確保網絡連接穩定

## 隱私與安全

- OpenAI API 調用會將音頻和文本數據發送到 OpenAI 服務器進行處理
- 所有會議記錄和摘要都保存在本地，不會上傳到雲端（除了 API 調用）
- 建議不要在應用中處理高度敏感或機密的會議內容

## 聯繫與支持

如有任何問題或建議，請聯繫 YCM 技術支持團隊。
# Deloitte_meeting_record_serve
# Deloitte_meeting_record_serve
