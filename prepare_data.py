import json
import os
from pathlib import Path

def prepare_dataset():
    """准备训练数据集"""

    # 检查数据目录
    audio_dir = Path("training_data/audio")
    transcript_file = Path("training_data/transcripts.json")

    if not audio_dir.exists():
        print("创建 training_data/audio 目录...")
        audio_dir.mkdir(parents=True)
        print("请将音频文件（WAV格式）放入 training_data/audio/ 目录")
        return False

    if not transcript_file.exists():
        print("创建示例 transcripts.json...")
        example = [
            {"audio": "001.wav", "text": "这是示例文本"},
            {"audio": "002.wav", "text": "请替换为实际内容"}
        ]
        with open(transcript_file, 'w', encoding='utf-8') as f:
            json.dump(example, f, ensure_ascii=False, indent=2)
        print("请编辑 training_data/transcripts.json 添加音频对应的文本")
        return False

    # 验证数据
    with open(transcript_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"找到 {len(data)} 条训练数据")

    missing = []
    for item in data:
        audio_path = audio_dir / item['audio']
        if not audio_path.exists():
            missing.append(item['audio'])

    if missing:
        print(f"警告: {len(missing)} 个音频文件缺失")
        print("缺失文件:", missing[:5])
        return False

    print("数据验证通过！")
    return True

if __name__ == "__main__":
    if prepare_dataset():
        print("可以开始训练了")
    else:
        print("请先准备好训练数据")
