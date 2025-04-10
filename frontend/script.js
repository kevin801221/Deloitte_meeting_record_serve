document.addEventListener('DOMContentLoaded', function() {
    // API 基礎 URL - 可以根據部署環境修改
    const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
        ? `http://${window.location.hostname}:${window.location.port}/api` 
        : `https://${window.location.hostname}/api`;
    
    // 初始化 API 密鑰設置
    let useDefaultApiKey = localStorage.getItem('use_default_api_key') !== 'false';
    let customApiKey = localStorage.getItem('openai_api_key') || '';
    let apiKey = useDefaultApiKey ? '' : customApiKey; // 默認 API 密鑰將由服務器處理
    
    // 設置初始界面狀態
    document.getElementById('useDefaultApiKey').checked = useDefaultApiKey;
    document.getElementById('api-key').value = customApiKey;
    document.getElementById('customApiKeySection').style.display = useDefaultApiKey ? 'none' : 'block';
    
    // 切換默認/自定義 API 密鑰
    document.getElementById('useDefaultApiKey').addEventListener('change', function() {
        const useDefault = this.checked;
        document.getElementById('customApiKeySection').style.display = useDefault ? 'none' : 'block';
    });
    
    // 初始檢查 API 狀態
    checkApiStatus();
    
    // 檢查 API 狀態
    function checkApiStatus() {
        const endpoints = [
            { url: `${API_BASE_URL}/text-to-summary`, element: 'text-to-summary-status' },
            { url: `${API_BASE_URL}/audio-to-text`, element: 'audio-to-text-status' },
            { url: `${API_BASE_URL}/audio-to-summary`, element: 'audio-to-summary-status' }
        ];
        
        endpoints.forEach(endpoint => {
            fetch(endpoint.url, { 
                method: 'OPTIONS',
                headers: {
                    'X-API-KEY': apiKey
                }
            })
                .then(response => {
                    const statusElement = document.getElementById(endpoint.element);
                    if (response.ok) {
                        statusElement.classList.add('status-active');
                        statusElement.classList.remove('status-inactive');
                    } else {
                        statusElement.classList.add('status-inactive');
                        statusElement.classList.remove('status-active');
                    }
                })
                .catch(() => {
                    const statusElement = document.getElementById(endpoint.element);
                    statusElement.classList.add('status-inactive');
                    statusElement.classList.remove('status-active');
                });
        });
    }
    
    // 保存 API 密鑰
    document.getElementById('save-api-key').addEventListener('click', function() {
        const useDefault = document.getElementById('useDefaultApiKey').checked;
        localStorage.setItem('use_default_api_key', useDefault);
        
        if (!useDefault) {
            const newApiKey = document.getElementById('api-key').value.trim();
            if (newApiKey) {
                localStorage.setItem('openai_api_key', newApiKey);
                customApiKey = newApiKey;
                apiKey = customApiKey;
                showApiKeyStatus('您的 API 密鑰已成功保存！', 'success');
            } else {
                showApiKeyStatus('請輸入有效的 API 密鑰或選擇使用默認密鑰', 'danger');
                return;
            }
        } else {
            apiKey = ''; // 默認 API 密鑰將由服務器處理
            showApiKeyStatus('已設置使用系統默認 API 密鑰', 'success');
        }
        
        checkApiStatus();
    });
    
    // 顯示/隱藏密碼
    document.getElementById('togglePassword').addEventListener('click', function() {
        const apiKeyInput = document.getElementById('api-key');
        const icon = this.querySelector('i');
        
        if (apiKeyInput.type === 'password') {
            apiKeyInput.type = 'text';
            icon.classList.remove('bi-eye');
            icon.classList.add('bi-eye-slash');
        } else {
            apiKeyInput.type = 'password';
            icon.classList.remove('bi-eye-slash');
            icon.classList.add('bi-eye');
        }
    });
    
    // 音頻轉文字表單提交
    document.getElementById('audioToTextForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const audioFile = document.getElementById('audio-file').files[0];
        
        if (!audioFile) {
            alert('請選擇音頻文件');
            return;
        }
        
        if (!apiKey) {
            alert('請先設置 OpenAI API 密鑰');
            const apiKeyModal = new bootstrap.Modal(document.getElementById('apiKeyModal'));
            apiKeyModal.show();
            return;
        }
        
        const resultBox = document.getElementById('audioToTextResult');
        resultBox.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">正在處理音頻，這可能需要幾分鐘時間...</p></div>';
        
        const formData = new FormData();
        formData.append('file', audioFile);
        
        fetch(`${API_BASE_URL}/audio-to-text`, {
            method: 'POST',
            headers: {
                'X-API-KEY': apiKey
            },
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            resultBox.innerHTML = `<pre>${data.transcription}</pre>`;
        })
        .catch(error => {
            resultBox.innerHTML = `<div class="alert alert-danger">錯誤: ${error.message}</div>`;
            console.error('Error:', error);
        });
    });
    
    // 文字轉摘要表單提交
    document.getElementById('textToSummaryForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const meetingTitle = document.getElementById('meeting-title-text').value;
        const participantsText = document.getElementById('participants-text').value;
        const meetingText = document.getElementById('meeting-text').value;
        
        // 將逗號分隔的參與者字符串轉換為數組
        const participants = participantsText.split(',')
            .map(p => p.trim())
            .filter(p => p.length > 0);
        
        if (!meetingText) {
            alert('請輸入會議文字記錄');
            return;
        }
        
        if (!apiKey) {
            alert('請先設置 OpenAI API 密鑰');
            const apiKeyModal = new bootstrap.Modal(document.getElementById('apiKeyModal'));
            apiKeyModal.show();
            return;
        }
        
        const resultBox = document.getElementById('textToSummaryResult');
        resultBox.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">正在生成摘要，這可能需要幾分鐘時間...</p></div>';
        
        fetch(`${API_BASE_URL}/text-to-summary`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-KEY': apiKey
            },
            body: JSON.stringify({
                meeting_title: meetingTitle,
                participants: participants,
                text: meetingText
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            let summaryHtml = '';
            
            if (data.meeting_title) {
                summaryHtml += `<h5>會議標題: ${data.meeting_title}</h5>`;
            }
            
            if (data.date) {
                summaryHtml += `<p>日期: ${data.date}</p>`;
            }
            
            if (data.participants && data.participants.length > 0) {
                summaryHtml += `<p>參與者: ${data.participants.join(', ')}</p>`;
            }
            
            if (data.summary) {
                summaryHtml += `<h5>摘要</h5><p>${data.summary}</p>`;
            }
            
            if (data.key_points && data.key_points.length > 0) {
                summaryHtml += '<h5>關鍵點</h5><ul>';
                data.key_points.forEach(point => {
                    summaryHtml += `<li>${point}</li>`;
                });
                summaryHtml += '</ul>';
            }
            
            if (data.action_items && data.action_items.length > 0) {
                summaryHtml += '<h5>行動項目</h5><ul>';
                data.action_items.forEach(item => {
                    summaryHtml += `<li>${item}</li>`;
                });
                summaryHtml += '</ul>';
            }
            
            if (data.decisions && data.decisions.length > 0) {
                summaryHtml += '<h5>決策</h5><ul>';
                data.decisions.forEach(decision => {
                    summaryHtml += `<li>${decision}</li>`;
                });
                summaryHtml += '</ul>';
            }
            
            resultBox.innerHTML = summaryHtml;
        })
        .catch(error => {
            resultBox.innerHTML = `<div class="alert alert-danger">錯誤: ${error.message}</div>`;
            console.error('Error:', error);
        });
    });
    
    // 音頻轉摘要表單提交
    document.getElementById('audioToSummaryForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const audioFile = document.getElementById('audio-file-summary').files[0];
        const meetingTitle = document.getElementById('meeting-title-audio').value;
        const participantsText = document.getElementById('participants-audio').value;
        
        // 將逗號分隔的參與者字符串轉換為數組
        const participants = participantsText.split(',')
            .map(p => p.trim())
            .filter(p => p.length > 0)
            .join(',');  // 對於表單數據，我們需要將其轉回字符串
        
        if (!audioFile) {
            alert('請選擇音頻文件');
            return;
        }
        
        if (!apiKey) {
            alert('請先設置 OpenAI API 密鑰');
            const apiKeyModal = new bootstrap.Modal(document.getElementById('apiKeyModal'));
            apiKeyModal.show();
            return;
        }
        
        const resultBox = document.getElementById('audioToSummaryResult');
        resultBox.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">正在處理音頻並生成摘要，這可能需要幾分鐘時間...</p></div>';
        
        const formData = new FormData();
        formData.append('file', audioFile);
        formData.append('meeting_title', meetingTitle);
        formData.append('participants', participants);
        
        fetch(`${API_BASE_URL}/audio-to-summary`, {
            method: 'POST',
            headers: {
                'X-API-KEY': apiKey
            },
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            let summaryHtml = '';
            
            if (data.meeting_title) {
                summaryHtml += `<h5>會議標題: ${data.meeting_title}</h5>`;
            }
            
            if (data.date) {
                summaryHtml += `<p>日期: ${data.date}</p>`;
            }
            
            if (data.participants && data.participants.length > 0) {
                summaryHtml += `<p>參與者: ${data.participants.join(', ')}</p>`;
            }
            
            if (data.summary) {
                summaryHtml += `<h5>摘要</h5><p>${data.summary}</p>`;
            }
            
            if (data.key_points && data.key_points.length > 0) {
                summaryHtml += '<h5>關鍵點</h5><ul>';
                data.key_points.forEach(point => {
                    summaryHtml += `<li>${point}</li>`;
                });
                summaryHtml += '</ul>';
            }
            
            if (data.action_items && data.action_items.length > 0) {
                summaryHtml += '<h5>行動項目</h5><ul>';
                data.action_items.forEach(item => {
                    summaryHtml += `<li>${item}</li>`;
                });
                summaryHtml += '</ul>';
            }
            
            if (data.decisions && data.decisions.length > 0) {
                summaryHtml += '<h5>決策</h5><ul>';
                data.decisions.forEach(decision => {
                    summaryHtml += `<li>${decision}</li>`;
                });
                summaryHtml += '</ul>';
            }
            
            resultBox.innerHTML = summaryHtml;
        })
        .catch(error => {
            resultBox.innerHTML = `<div class="alert alert-danger">錯誤: ${error.message}</div>`;
            console.error('Error:', error);
        });
    });

    // 本地錄音功能
    let mediaRecorder;
    let audioChunks = [];
    let recordingStream;
    let recordingStartTime;
    let recordingTimer;
    let recordingPausedTime = 0;
    let recordingBlob;
    let audioContext;
    let analyser;
    let visualizerCanvas;
    let visualizerCanvasCtx;
    
    // 初始化音頻可視化器
    function initAudioVisualizer() {
        visualizerCanvas = document.getElementById('audioVisualizer');
        visualizerCanvasCtx = visualizerCanvas.getContext('2d');
        
        // 設置畫布尺寸
        visualizerCanvas.width = visualizerCanvas.offsetWidth;
        visualizerCanvas.height = visualizerCanvas.offsetHeight;
        
        // 清空畫布
        visualizerCanvasCtx.clearRect(0, 0, visualizerCanvas.width, visualizerCanvas.height);
        visualizerCanvasCtx.fillStyle = '#f0f0f0';
        visualizerCanvasCtx.fillRect(0, 0, visualizerCanvas.width, visualizerCanvas.height);
    }
    
    // 更新錄音時間顯示
    function updateRecordingTime() {
        const currentTime = new Date();
        let elapsedTime = currentTime - recordingStartTime + recordingPausedTime;
        
        const hours = Math.floor(elapsedTime / 3600000);
        const minutes = Math.floor((elapsedTime % 3600000) / 60000);
        const seconds = Math.floor((elapsedTime % 60000) / 1000);
        
        document.getElementById('recordingTime').textContent = 
            `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    
    // 繪製音頻可視化
    function drawAudioVisualization() {
        if (!analyser) return;
        
        requestAnimationFrame(drawAudioVisualization);
        
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        analyser.getByteTimeDomainData(dataArray);
        
        visualizerCanvasCtx.fillStyle = '#f0f0f0';
        visualizerCanvasCtx.fillRect(0, 0, visualizerCanvas.width, visualizerCanvas.height);
        
        visualizerCanvasCtx.lineWidth = 2;
        visualizerCanvasCtx.strokeStyle = '#007bff';
        visualizerCanvasCtx.beginPath();
        
        const sliceWidth = visualizerCanvas.width / bufferLength;
        let x = 0;
        
        for (let i = 0; i < bufferLength; i++) {
            const v = dataArray[i] / 128.0;
            const y = v * visualizerCanvas.height / 2;
            
            if (i === 0) {
                visualizerCanvasCtx.moveTo(x, y);
            } else {
                visualizerCanvasCtx.lineTo(x, y);
            }
            
            x += sliceWidth;
        }
        
        visualizerCanvasCtx.lineTo(visualizerCanvas.width, visualizerCanvas.height / 2);
        visualizerCanvasCtx.stroke();
    }
    
    // 開始錄音
    document.getElementById('startRecording').addEventListener('click', async function() {
        try {
            // 檢查是否有未保存的錄音
            if (recordingBlob && document.getElementById('recordedAudioContainer').style.display !== 'none') {
                // 顯示確認對話框
                if (!confirm('您有一個未保存的錄音。開始新錄音將會丟失當前錄音。確定要繼續嗎？')) {
                    return; // 用戶取消，不開始新錄音
                }
            }
            
            // 初始化音頻可視化器
            initAudioVisualizer();
            
            // 獲取麥克風權限
            recordingStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // 設置音頻上下文和分析器
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const source = audioContext.createMediaStreamSource(recordingStream);
            analyser = audioContext.createAnalyser();
            analyser.fftSize = 2048;
            source.connect(analyser);
            
            // 創建 MediaRecorder
            mediaRecorder = new MediaRecorder(recordingStream);
            
            // 收集音頻數據
            mediaRecorder.ondataavailable = function(e) {
                if (e.data.size > 0) {
                    audioChunks.push(e.data);
                }
            };
            
            // 錄音完成時處理
            mediaRecorder.onstop = function() {
                // 創建音頻 Blob
                recordingBlob = new Blob(audioChunks, { type: 'audio/wav' });
                
                // 創建音頻 URL 並設置播放器
                const audioURL = URL.createObjectURL(recordingBlob);
                const audioPlayer = document.getElementById('recordedAudio');
                audioPlayer.src = audioURL;
                
                // 顯示錄音控件
                document.getElementById('recordedAudioContainer').style.display = 'block';
                
                // 自動保存錄音到本地
                autoSaveRecording();
                
                // 停止計時器
                clearInterval(recordingTimer);
                
                // 重置 UI
                document.getElementById('startRecording').disabled = false;
                document.getElementById('pauseRecording').disabled = true;
                document.getElementById('resumeRecording').disabled = true;
                document.getElementById('stopRecording').disabled = true;
                document.getElementById('recordingStatus').textContent = '錄音完成';
                
                // 停止音頻可視化
                if (recordingStream) {
                    recordingStream.getTracks().forEach(track => track.stop());
                }
            };
            
            // 開始錄音
            mediaRecorder.start(1000);
            audioChunks = [];
            
            // 開始計時
            recordingStartTime = new Date();
            recordingPausedTime = 0;
            recordingTimer = setInterval(updateRecordingTime, 1000);
            
            // 開始音頻可視化
            drawAudioVisualization();
            
            // 更新 UI
            document.getElementById('recordingStatus').textContent = '正在錄音...';
            document.getElementById('startRecording').disabled = true;
            document.getElementById('pauseRecording').disabled = false;
            document.getElementById('resumeRecording').disabled = true;
            document.getElementById('stopRecording').disabled = false;
        } catch (error) {
            console.error('錄音失敗:', error);
            alert(`無法啟動錄音: ${error.message}`);
        }
    });
    
    // 暫停錄音
    document.getElementById('pauseRecording').addEventListener('click', function() {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.pause();
            recordingPausedTime = new Date() - recordingStartTime;
            clearInterval(recordingTimer);
            
            document.getElementById('recordingStatus').textContent = '錄音已暫停';
            document.getElementById('pauseRecording').disabled = true;
            document.getElementById('resumeRecording').disabled = false;
        }
    });
    
    // 繼續錄音
    document.getElementById('resumeRecording').addEventListener('click', function() {
        if (mediaRecorder && mediaRecorder.state === 'paused') {
            mediaRecorder.resume();
            recordingStartTime = new Date() - recordingPausedTime;
            recordingTimer = setInterval(updateRecordingTime, 1000);
            
            document.getElementById('recordingStatus').textContent = '正在錄音...';
            document.getElementById('pauseRecording').disabled = false;
            document.getElementById('resumeRecording').disabled = true;
        }
    });
    
    // 停止錄音
    document.getElementById('stopRecording').addEventListener('click', function() {
        if (mediaRecorder && (mediaRecorder.state === 'recording' || mediaRecorder.state === 'paused')) {
            mediaRecorder.stop();
        }
    });
    
    // 自動保存錄音到本地
    function autoSaveRecording() {
        if (!recordingBlob) {
            return;
        }
        
        // 獲取會議標題作為文件名
        let fileName = document.getElementById('meeting-title-recording').value.trim();
        if (!fileName) {
            const now = new Date();
            fileName = `錄音_${now.getFullYear()}${(now.getMonth() + 1).toString().padStart(2, '0')}${now.getDate().toString().padStart(2, '0')}_${now.getHours().toString().padStart(2, '0')}${now.getMinutes().toString().padStart(2, '0')}`;
        }
        
        // 創建下載鏈接
        const downloadLink = document.createElement('a');
        downloadLink.href = URL.createObjectURL(recordingBlob);
        downloadLink.download = `${fileName}.wav`;
        
        // 模擬點擊下載
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
        
        // 顯示保存狀態
        const saveStatus = document.getElementById('saveStatus');
        const saveStatusText = document.getElementById('saveStatusText');
        saveStatusText.textContent = `錄音已自動保存為 "${fileName}.wav"`;
        saveStatus.style.display = 'block';
    }
    
    // 生成最終摘要
    document.getElementById('generateSummaryFromRecording').addEventListener('click', function() {
        if (!recordingBlob) {
            alert('沒有可用的錄音');
            return;
        }
        
        if (!apiKey) {
            alert('請先設置 OpenAI API 密鑰');
            const apiKeyModal = new bootstrap.Modal(document.getElementById('apiKeyModal'));
            apiKeyModal.show();
            return;
        }
        
        // 切換到音頻轉摘要標籤
        document.getElementById('audio-to-summary-tab').click();
        
        // 獲取會議標題
        const meetingTitle = document.getElementById('meeting-title-recording').value.trim();
        if (meetingTitle) {
            document.getElementById('meeting-title-audio').value = meetingTitle;
        }
        
        // 創建 File 對象
        const fileName = meetingTitle || 'recording.wav';
        const audioFile = new File([recordingBlob], fileName, { type: 'audio/wav' });
        
        // 創建 DataTransfer 對象並設置文件
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(audioFile);
        document.getElementById('audio-file-summary').files = dataTransfer.files;
        
        // 自動提交表單
        document.getElementById('audioToSummaryForm').dispatchEvent(new Event('submit'));
    });
    
    // 顯示 API 密鑰狀態
    function showApiKeyStatus(message, type) {
        const statusElement = document.getElementById('apiKeyStatus');
        statusElement.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
    }
});
