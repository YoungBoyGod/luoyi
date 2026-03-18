import whisper
import sys

if len(sys.argv) > 1:
    model_name = sys.argv[1]
else:
    model_name = "medium"

print(f"下载 {model_name} 模型...")
max_retries = 3

for attempt in range(max_retries):
    try:
        whisper.load_model(model_name)
        print(f"[OK] {model_name} 模型下载完成")
        break
    except RuntimeError as e:
        if "checksum" in str(e):
            print(f"校验失败，重试 {attempt + 1}/{max_retries}...")
            if attempt < max_retries - 1:
                continue
            else:
                print("下载失败，请稍后网络稳定时重试")
        else:
            raise
