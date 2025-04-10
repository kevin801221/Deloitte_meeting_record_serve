"""
Main application for the AI meeting recorder using Gradio.
"""

import os
import gradio as gr
from core.audio import AudioRecorder
from core.transcription import Transcriber
from core.summary import SummaryGenerator
from core.export import Exporter
from utils import Config

class MeetingRecorderApp:
    """Main application class for the meeting recorder."""
    
    def __init__(self):
        """Initialize the application."""
        self.config = Config()
        self.audio_recorder = AudioRecorder()
        self.transcriber = Transcriber()
        self.summary_generator = SummaryGenerator()
        self.exporter = Exporter()
        
        self.meeting_title = self.config.get_app_config()["default_meeting_title"]
        self.participants = []
    
    def set_meeting_info(self, title, participants_str):
        """Set meeting information."""
        self.meeting_title = title if title else self.config.get_app_config()["default_meeting_title"]
        self.participants = [p.strip() for p in participants_str.split(",") if p.strip()]
        return f"會議訊息已設置: {self.meeting_title} (參與者: {', '.join(self.participants)})"
    
    def start_recording(self):
        """Start recording audio."""
        return self.audio_recorder.start_recording()
    def stop_recording(self):
        """Stop recording audio."""
        return self.audio_recorder.stop_recording()
    
    def transcribe_audio(self, audio_file):
        """Transcribe audio to text."""
        if not audio_file:
            return "請先錄製音頻。"
        return self.transcriber.transcribe_audio(audio_file)
    
    def generate_summary(self, transcription):
        """Generate meeting summary."""
        return self.summary_generator.generate_summary(
            transcription, 
            meeting_title=self.meeting_title, 
            participants=self.participants
        )
    
    def export_meeting(self):
        """Export meeting record."""
        return self.exporter.export_meeting(
            self.meeting_title,
            self.participants,
            self.transcriber.get_all_transcriptions(),
            self.summary_generator.get_summary()
        )
    
    def process_uploaded_audio(self, audio_file, title, participants_str):
        """Process uploaded audio file: transcribe and generate summary."""
        # Set meeting info
        info_message = self.set_meeting_info(title, participants_str)
        
        # Transcribe audio
        if not audio_file:
            return info_message, "請上傳音頻文件。", ""
        
        transcription = self.transcriber.transcribe_audio(audio_file)
        
        # Generate summary
        summary = self.summary_generator.generate_summary(
            transcription, 
            meeting_title=self.meeting_title, 
            participants=self.participants
        )
        
        # Export meeting
        export_status = self.exporter.export_meeting(
            self.meeting_title,
            self.participants,
            self.transcriber.get_all_transcriptions(),
            summary
        )
        
        return info_message, transcription, summary, export_status
    
    def process_recorded_audio(self, audio_file):
        """Process recorded audio: transcribe, generate summary, and export."""
        if not audio_file:
            return "請先錄製音頻。", "", ""
        
        print(f"Processing recorded audio: {audio_file}")
        
        # Transcribe audio
        transcription = self.transcriber.transcribe_audio(audio_file)
        
        # If transcription failed with an error message, return it
        if transcription.startswith("轉錄失敗") or transcription.startswith("請先錄製") or transcription.startswith("音頻文件不存在") or transcription.startswith("無法處理音頻"):
            return transcription, "", ""
        
        # Generate summary
        summary = self.summary_generator.generate_summary(
            transcription, 
            meeting_title=self.meeting_title, 
            participants=self.participants
        )
        
        # Export meeting
        export_status = self.exporter.export_meeting(
            self.meeting_title,
            self.participants,
            self.transcriber.get_all_transcriptions(),
            summary
        )
        
        return transcription, summary, export_status
    
    def create_interface(self):
        """Create the Gradio interface."""
        with gr.Blocks(title="YCM智能會議記錄助手", theme=gr.themes.Soft()) as app:
            # 使用 Markdown 顯示標題，並在標題旁邊嵌入一個小尺寸的 logo 圖片
            gr.Markdown("""
            <div style="display: flex; align-items: center; margin-bottom: 1em;">
                <h1 style="margin: 0;">YCM智能會議記錄助手</h1>
            </div>
            """)
            gr.Markdown("### 自動記錄會議內容，識別說話者，並生成摘要")
            
            with gr.Tab("一站式會議處理"):
                gr.Markdown("### 在一個頁面完成所有會議記錄流程")
                
                with gr.Row():
                    meeting_title_all = gr.Textbox(label="會議標題", placeholder="輸入會議標題", value=self.meeting_title)
                    participants_all = gr.Textbox(label="參與者 (用逗號分隔)", placeholder="例如: 張三, 李四, 王五")
                
                set_info_btn_all = gr.Button("設置會議訊息")
                info_output_all = gr.Textbox(label="訊息", interactive=False)
                
                gr.Markdown("#### 選擇錄音或上傳音頻")
                
                with gr.Tabs():
                    with gr.TabItem("錄製音頻"):
                        with gr.Row():
                            start_btn_all = gr.Button("開始錄音", variant="primary")
                            stop_btn_all = gr.Button("停止錄音", variant="stop")
                        
                        status_all = gr.Textbox(label="錄音狀態", interactive=False)
                        audio_output_all = gr.Audio(label="錄音結果", type="filepath", interactive=False)
                        process_recording_btn = gr.Button("處理錄音", variant="primary")
                    
                    with gr.TabItem("上傳音頻"):
                        upload_audio = gr.Audio(label="上傳或拖放音頻文件", type="filepath", interactive=True)
                        process_upload_btn = gr.Button("處理上傳的音頻", variant="primary")
                
                with gr.Accordion("處理結果", open=False):
                    transcription_all = gr.Textbox(label="轉錄結果", interactive=False, lines=10)
                    summary_all = gr.Textbox(label="會議摘要", interactive=False, lines=15)
                    export_status_all = gr.Textbox(label="導出狀態", interactive=False)
                
                # Connect the buttons to their respective functions
                set_info_btn_all.click(
                    fn=self.set_meeting_info,
                    inputs=[meeting_title_all, participants_all],
                    outputs=info_output_all
                )
                
                start_btn_all.click(fn=self.start_recording, outputs=status_all)
                
                def stop_and_process():
                    audio_file, message = self.stop_recording()
                    return audio_file, message
                
                stop_btn_all.click(fn=stop_and_process, outputs=[audio_output_all, status_all])
                
                process_recording_btn.click(
                    fn=self.process_recorded_audio,
                    inputs=[audio_output_all],
                    outputs=[transcription_all, summary_all, export_status_all]
                )
                
                process_upload_btn.click(
                    fn=self.process_uploaded_audio,
                    inputs=[upload_audio, meeting_title_all, participants_all],
                    outputs=[info_output_all, transcription_all, summary_all, export_status_all]
                )
            
            with gr.Tab("會議設置"):
                with gr.Row():
                    meeting_title = gr.Textbox(label="會議標題", placeholder="輸入會議標題", value=self.meeting_title)
                    participants = gr.Textbox(label="參與者 (用逗號分隔)", placeholder="例如: 張三, 李四, 王五")
                
                set_info_btn = gr.Button("設置會議訊息")
                info_output = gr.Textbox(label="訊息", interactive=False)
                
                set_info_btn.click(
                    fn=self.set_meeting_info,
                    inputs=[meeting_title, participants],
                    outputs=info_output
                )
            
            with gr.Tab("錄音與轉錄"):
                with gr.Row():
                    start_btn = gr.Button("開始錄音", variant="primary")
                    stop_btn = gr.Button("停止錄音", variant="stop")
                
                status = gr.Textbox(label="狀態", interactive=False)
                audio_output = gr.Audio(label="錄音結果", type="filepath", interactive=False)
                
                transcription = gr.Textbox(label="轉錄結果", interactive=False, lines=10)
                transcribe_btn = gr.Button("轉錄音頻")
                
                # Connect the buttons to their respective functions
                start_btn.click(fn=self.start_recording, outputs=status)
                
                def stop_and_process():
                    audio_file, message = self.stop_recording()
                    return audio_file, message
                
                stop_btn.click(fn=stop_and_process, outputs=[audio_output, status])
                transcribe_btn.click(fn=self.transcribe_audio, inputs=audio_output, outputs=transcription)
            
            with gr.Tab("摘要生成"):
                generate_btn = gr.Button("生成會議摘要")
                summary_output = gr.Textbox(label="會議摘要", interactive=False, lines=15)
                
                generate_btn.click(fn=self.generate_summary, inputs=transcription, outputs=summary_output)
            
            with gr.Tab("導出"):
                export_btn = gr.Button("導出會議記錄")
                export_output = gr.Textbox(label="導出狀態", interactive=False)
                
                export_btn.click(fn=self.export_meeting, outputs=export_output)
            
            with gr.Tab("拖放音頻處理"):
                gr.Markdown("### 拖放音頻文件進行快速處理")
                gr.Markdown("上傳音頻文件，一鍵完成轉錄和摘要生成")
                
                with gr.Row():
                    drop_title = gr.Textbox(label="會議標題", placeholder="輸入會議標題", value=self.meeting_title)
                    drop_participants = gr.Textbox(label="參與者 (用逗號分隔)", placeholder="例如: 張三, 李四, 王五")
                
                drop_audio = gr.Audio(label="拖放音頻文件到這裡", type="filepath", interactive=True)
                process_btn = gr.Button("處理音頻", variant="primary")
                
                drop_info = gr.Textbox(label="處理訊息", interactive=False)
                drop_transcription = gr.Textbox(label="轉錄結果", interactive=False, lines=10)
                drop_summary = gr.Textbox(label="會議摘要", interactive=False, lines=15)
                drop_export = gr.Textbox(label="導出狀態", interactive=False)
                
                process_btn.click(
                    fn=self.process_uploaded_audio,
                    inputs=[drop_audio, drop_title, drop_participants],
                    outputs=[drop_info, drop_transcription, drop_summary, drop_export]
                )
        
        return app

def main():
    """Main entry point for the application."""
    # 獲取 favicon 的絕對路徑
    favicon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "favicon.ico")
    
    # 檢查是否在 Docker 容器中運行
    in_docker = os.path.exists('/.dockerenv')
    server_name = "0.0.0.0" if in_docker else "127.0.0.1"
    
    app = MeetingRecorderApp().create_interface()
    app.launch(share=False, favicon_path=favicon_path, server_name=server_name)

if __name__ == "__main__":
    main()
