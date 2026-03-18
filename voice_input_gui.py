import sys
import whisper
import subprocess
import pyperclip
import keyboard
import tempfile
import os
import json
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox, QPushButton, QLabel, QTextEdit
from PyQt6.QtCore import QThread, pyqtSignal

CONFIG_FILE = "config.json"
LOG_FILE = "voice_log.txt"
MODEL_DIR = "models"
FFMPEG_DIR = os.path.join(os.path.dirname(__file__), "ffmpeg")
FFMPEG_PATH = os.path.join(FFMPEG_DIR, "ffmpeg.exe")

# 设置环境变量，让 Whisper 能找到 ffmpeg
os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")

class VoiceWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, device, model, sample_rate, audio_path):
        super().__init__()
        self.device = device
        self.model = model
        self.sample_rate = sample_rate
        self.audio_path = audio_path

    def run(self):
        result = self.model.transcribe(
            self.audio_path,
            language="zh",
            temperature=0.0,
            beam_size=5,
            best_of=5,
            patience=1.0
        )
        text = result["text"]
        os.unlink(self.audio_path)
        self.finished.emit(text)

def get_audio_devices():
    cmd = [FFMPEG_PATH, "-list_devices", "true", "-f", "dshow", "-i", "dummy"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    devices = []
    for line in result.stderr.split('\n'):
        if '(audio)' in line:
            start = line.find('"') + 1
            end = line.find('"', start)
            if start > 0 and end > start:
                devices.append(line[start:end])
    return devices

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("语音输入")
        self.setGeometry(100, 100, 450, 400)

        self.model = None
        self.recording_process = None
        self.temp_audio_path = None
        self.load_config()

        widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("选择 Whisper 模型:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large"])
        self.model_combo.setCurrentText(self.config.get("model", "base"))
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        layout.addWidget(self.model_combo)

        layout.addWidget(QLabel("选择采样率:"))
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItems(["16000", "22050", "44100", "48000"])
        self.sample_rate_combo.setCurrentText(str(self.config.get("sample_rate", 16000)))
        layout.addWidget(self.sample_rate_combo)

        layout.addWidget(QLabel("选择麦克风设备:"))
        self.device_combo = QComboBox()
        devices = get_audio_devices()
        self.device_combo.addItems(devices)
        if self.config.get("device") in devices:
            self.device_combo.setCurrentText(self.config["device"])
        layout.addWidget(self.device_combo)

        self.status_label = QLabel("加载模型中...")
        layout.addWidget(self.status_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

        keyboard.on_press_key('space', self.on_key_press)
        keyboard.on_release_key('space', self.on_key_release)
        self.load_model()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {}

    def load_model(self):
        if not os.path.exists(MODEL_DIR):
            os.makedirs(MODEL_DIR)
        model_name = self.model_combo.currentText()
        self.status_label.setText(f"加载 {model_name} 模型中...")
        self.model = whisper.load_model(model_name, download_root=MODEL_DIR)
        self.status_label.setText("按住空格键开始录音")

    def on_model_changed(self):
        self.load_model()

    def save_config(self):
        self.config["device"] = self.device_combo.currentText()
        self.config["model"] = self.model_combo.currentText()
        self.config["sample_rate"] = int(self.sample_rate_combo.currentText())
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def on_key_press(self, e):
        if self.recording_process is None and self.model:
            self.start_recording()

    def on_key_release(self, e):
        if self.recording_process is not None:
            self.stop_recording()

    def start_recording(self):
        if not self.model:
            return
        self.status_label.setText("录音中... (松开空格键停止)")
        self.save_config()

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        self.temp_audio_path = temp_file.name
        temp_file.close()

        sample_rate = int(self.sample_rate_combo.currentText())
        cmd = [FFMPEG_PATH, "-f", "dshow", "-i", f"audio={self.device_combo.currentText()}",
               "-ar", str(sample_rate), "-ac", "1", self.temp_audio_path, "-y"]
        self.recording_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def stop_recording(self):
        if self.recording_process:
            self.recording_process.terminate()
            self.recording_process.wait()
            self.recording_process = None
            self.status_label.setText("识别中...")
            self.worker = VoiceWorker(self.device_combo.currentText(), self.model,
                                     int(self.sample_rate_combo.currentText()), self.temp_audio_path)
            self.worker.finished.connect(self.on_transcribe_finished)
            self.worker.start()

    def on_transcribe_finished(self, text):
        if text.strip():
            self.status_label.setText(f"识别: {text}")
            pyperclip.copy(text)
            keyboard.send('ctrl+v')

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {text}\n"
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            self.log_text.append(log_entry.strip())
        else:
            self.status_label.setText("未识别到内容")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


