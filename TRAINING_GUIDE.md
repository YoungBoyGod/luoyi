# Whisper 模型微调指南

## 前置要求

### 硬件要求
- GPU: 至少 16GB 显存（推荐 RTX 3090 或 A100）
- 内存: 32GB+
- 硬盘: 100GB+ 空闲空间

### 软件要求
- Python 3.8+
- CUDA 11.8+
- PyTorch 2.0+

## 步骤概览

1. 准备训练数据（音频 + 文本标注）
2. 安装训练依赖
3. 数据预处理
4. 微调模型
5. 测试和部署

## 详细步骤

### 1. 准备训练数据
 
数据组织结构：
```
training_data/
├── audio/
│   ├── 001.wav
│   ├── 002.wav
│   └── ...
└── transcripts.json
```

transcripts.json 格式：
```json
[
  {"audio": "001.wav", "text": "这是第一段录音的文本"},
  {"audio": "002.wav", "text": "这是第二段录音的文本"}
]
```

### 2. 安装依赖

运行：`pip install -r requirements_training.txt`

### 3. 运行训练

```bash
python train_whisper.py --model_name small --epochs 10 --batch_size 8
```

### 4. 测试模型

```bash
python test_model.py --model_path ./fine_tuned_model
```

## 注意事项

- 训练时间：根据数据量，可能需要几小时到几天
- 成本：如果使用云GPU（如 Google Colab Pro），每月约 $10-50
- 数据质量：标注准确性直接影响效果
