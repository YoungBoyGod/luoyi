import whisper
import sys

def test_model(model_path="./fine_tuned_model", audio_file=None):
    """测试微调后的模型"""

    print(f"加载模型: {model_path}")
    model = whisper.load_model(model_path)

    if not audio_file:
        print("请提供测试音频文件:")
        print("python test_model.py --audio test.wav")
        return

    print(f"识别音频: {audio_file}")
    result = model.transcribe(audio_file, language="zh")

    print("\n识别结果:")
    print(result["text"])

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", default="./fine_tuned_model")
    parser.add_argument("--audio", required=True)
    args = parser.parse_args()

    test_model(args.model_path, args.audio)
