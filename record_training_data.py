import os
import json
import subprocess
import time
from pathlib import Path

# 示例文章（可以替换为更多内容）
TEXTS = [
    "人工智能技术正在快速发展，深度学习模型在语音识别领域取得了突破性进展。",
    "今天天气很好，阳光明媚，适合出门散步和运动。",
    "我喜欢在周末的时候阅读书籍，这让我感到放松和充实。",
    "科技改变生活，互联网让世界变得更加紧密相连。",
    "学习新技能需要耐心和坚持，每天进步一点点就是成功。",
    "音乐是人类共同的语言，它能够跨越文化和语言的障碍。",
    "健康的生活方式包括合理饮食、适量运动和充足睡眠。",
    "编程是一门艺术，也是一门科学，需要逻辑思维和创造力。",
    "旅行可以开阔视野，体验不同的文化和风土人情。",
    "时间管理是成功的关键，合理安排时间能提高工作效率。"
]

def setup_directories():
    """创建必要的目录"""
    Path("training_data/audio").mkdir(parents=True, exist_ok=True)

def record_audio(output_file, duration=10):
    """录制音频"""
    ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg", "ffmpeg.exe")
    cmd = [
        ffmpeg_path, "-f", "dshow",
        "-i", "audio=Microphone Array (Realtek(R) Audio)",
        "-t", str(duration), "-ar", "16000", "-ac", "1",
        output_file, "-y"
    ]
    subprocess.run(cmd, capture_output=True)

def main():
    """主录音流程"""
    setup_directories()

    print("=" * 60)
    print("训练数据录音工具")
    print("=" * 60)
    print(f"共有 {len(TEXTS)} 段文本需要录音")
    print("每段录音 10 秒，请在倒计时结束前完成朗读")
    print()

    transcripts = []

    for i, text in enumerate(TEXTS, 1):
        print(f"\n[{i}/{len(TEXTS)}] 请朗读以下内容:")
        print("-" * 60)
        print(text)
        print("-" * 60)

        input("准备好后按 Enter 开始录音...")

        print("3...")
        time.sleep(1)
        print("2...")
        time.sleep(1)
        print("1...")
        time.sleep(1)
        print("开始录音！")

        audio_file = f"training_data/audio/{i:03d}.wav"
        record_audio(audio_file, duration=10)

        print("录音完成！")

        transcripts.append({
            "audio": f"{i:03d}.wav",
            "text": text
        })

    # 保存转录文件
    with open("training_data/transcripts.json", 'w', encoding='utf-8') as f:
        json.dump(transcripts, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"完成！共录制 {len(TEXTS)} 段音频")
    print("数据已保存到 training_data/ 目录")
    print("=" * 60)

if __name__ == "__main__":
    main()

