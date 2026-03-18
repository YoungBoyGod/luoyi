import whisper

models = ["tiny", "base", "small", "medium", "large"]

print("开始下载 Whisper 模型...")
for model_name in models:
    print(f"\n下载 {model_name} 模型...")
    whisper.load_model(model_name)
    print(f"[OK] {model_name} 模型下载完成")

print("\n所有模型下载完成！")
