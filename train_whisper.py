import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration, Seq2SeqTrainingArguments, Seq2SeqTrainer
from datasets import Dataset, Audio
import json
from pathlib import Path

def load_data():
    """加载训练数据"""
    with open("training_data/transcripts.json", 'r', encoding='utf-8') as f:
        data = json.load(f)

    audio_files = [str(Path("training_data/audio") / item['audio']) for item in data]
    texts = [item['text'] for item in data]

    dataset = Dataset.from_dict({"audio": audio_files, "text": texts})
    dataset = dataset.cast_column("audio", Audio(sampling_rate=16000))
    return dataset

def train(model_name="small", epochs=10, batch_size=8):
    """微调 Whisper 模型"""

    print(f"加载 {model_name} 模型...")
    processor = WhisperProcessor.from_pretrained(f"openai/whisper-{model_name}")
    model = WhisperForConditionalGeneration.from_pretrained(f"openai/whisper-{model_name}")

    print("加载训练数据...")
    dataset = load_data()

    def prepare_dataset(batch):
        audio = batch["audio"]
        batch["input_features"] = processor(audio["array"], sampling_rate=audio["sampling_rate"], return_tensors="pt").input_features[0]
        batch["labels"] = processor.tokenizer(batch["text"]).input_ids
        return batch

    dataset = dataset.map(prepare_dataset, remove_columns=dataset.column_names)

    training_args = Seq2SeqTrainingArguments(
        output_dir="./fine_tuned_model",
        per_device_train_batch_size=batch_size,
        num_train_epochs=epochs,
        save_steps=500,
        logging_steps=100,
        learning_rate=1e-5,
        warmup_steps=500,
        fp16=True,
        report_to=["tensorboard"]
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        tokenizer=processor.feature_extractor
    )

    print("开始训练...")
    trainer.train()

    print("保存模型...")
    model.save_pretrained("./fine_tuned_model")
    processor.save_pretrained("./fine_tuned_model")
    print("训练完成！")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", default="small", choices=["tiny", "base", "small", "medium"])
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch_size", type=int, default=8)
    args = parser.parse_args()

    train(args.model_name, args.epochs, args.batch_size)

