import whisper
import subprocess
import pyperclip
import keyboard
import tempfile
import os

model = whisper.load_model("base")

def record_audio(duration=5):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_path = temp_file.name
    temp_file.close()

    cmd = [
        "ffmpeg", "-f", "dshow",
        "-i", "audio=Microphone Array (Realtek(R) Audio)",
        "-t", str(duration), "-ar", "16000", "-ac", "1",
        temp_path, "-y"
    ]
    subprocess.run(cmd, capture_output=True)
    return temp_path

def transcribe_and_type():
    print("录音中... (5秒)")
    audio_path = record_audio(5)

    print("识别中...")
    result = model.transcribe(audio_path, language="zh")
    text = result["text"]

    os.unlink(audio_path)

    if text.strip():
        print(f"识别结果: {text}")
        pyperclip.copy(text)
        keyboard.send('ctrl+v')
    else:
        print("未识别到内容")

if __name__ == "__main__":
    print("语音输入已启动，按 Ctrl+Shift+Space 开始录音")
    keyboard.add_hotkey('ctrl+shift+space', transcribe_and_type)
    keyboard.wait()
