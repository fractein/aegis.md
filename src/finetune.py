import sys
import csv
import os
import random
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.optim import AdamW
from transformers import get_linear_schedule_with_warmup

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "data", "test_dataset.csv")
# xlm-roberta-large: 560M параметров, лучше для большого датасета
BASE_MODEL = "xlm-roberta-large"
SAVE_PATH = os.path.join(BASE_DIR, "models", "aegis-finetuned")
EPOCHS = 25
BATCH_SIZE = 8
LR = 1e-5
LABEL2ID = {"safe": 0, "scam": 1}
ID2LABEL = {0: "safe", 1: "scam"}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Устройство: {device}")
if device.type == "cuda":
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
print()


def load_data():
    rows = []
    with open(DATASET_PATH, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows.append({"text": row["text"], "label": LABEL2ID[row["label"]]})
    random.seed(42)
    random.shuffle(rows)
    split = int(len(rows) * 0.8)
    return rows[:split], rows[split:]


class SMSDataset(Dataset):
    def __init__(self, data, tokenizer):
        self.data = data
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        enc = self.tokenizer(
            item["text"],
            truncation=True,
            max_length=128,
            padding="max_length",
            return_tensors="pt",
        )
        return {
            "input_ids": enc["input_ids"].squeeze(),
            "attention_mask": enc["attention_mask"].squeeze(),
            "labels": torch.tensor(item["label"], dtype=torch.long),
        }


def evaluate(model, loader):
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for batch in loader:
            ids = batch["input_ids"].to(device)
            mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            out = model(input_ids=ids, attention_mask=mask)
            preds = out.logits.argmax(dim=-1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    return correct / total if total > 0 else 0


def main():
    print("Загрузка датасета...")
    train_data, val_data = load_data()
    print(f"Обучение: {len(train_data)} SMS | Валидация: {len(val_data)} SMS")

    print(f"\nЗагрузка модели {BASE_MODEL}...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL,
        num_labels=2,
        id2label=ID2LABEL,
        label2id=LABEL2ID,
    )
    model.to(device)

    train_loader = DataLoader(SMSDataset(train_data, tokenizer), batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(SMSDataset(val_data, tokenizer), batch_size=BATCH_SIZE)

    optimizer = AdamW(model.parameters(), lr=LR, weight_decay=0.01)
    total_steps = len(train_loader) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=max(1, total_steps // 5),
        num_training_steps=total_steps,
    )

    print(f"\nНачало обучения ({EPOCHS} эпох на {device})...\n")
    best_acc = 0.0

    for epoch in range(1, EPOCHS + 1):
        model.train()
        total_loss = 0.0

        for batch in train_loader:
            ids = batch["input_ids"].to(device)
            mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            optimizer.zero_grad()
            out = model(input_ids=ids, attention_mask=mask, labels=labels)
            out.loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            total_loss += out.loss.item()

        avg_loss = total_loss / len(train_loader)
        val_acc = evaluate(model, val_loader)
        marker = " <-- лучший" if val_acc > best_acc else ""
        print(f"Эпоха {epoch:2}/{EPOCHS} | Loss: {avg_loss:.4f} | Val Acc: {val_acc:.1%}{marker}")

        if val_acc > best_acc:
            best_acc = val_acc
            model.save_pretrained(SAVE_PATH)
            tokenizer.save_pretrained(SAVE_PATH)

    print(f"\nОбучение завершено! Лучшая точность: {best_acc:.1%}")
    print(f"Модель сохранена в: {SAVE_PATH}/")
    print("\nЧтобы использовать в app.py, замени строку загрузки модели на:")
    print(f'  classifier = pipeline("text-classification", model="{SAVE_PATH}")')


if __name__ == "__main__":
    main()
