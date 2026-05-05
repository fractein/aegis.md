"""Инкрементальное дообучение: продолжает тренировать существующий чекпоинт
models/sms-shield-finetuned на обновлённом датасете (с примерами «скам/обман/fraudă»).

Запуск: python continue_finetune.py
"""
import sys
import csv
import os
import time
import random
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.optim import AdamW
from transformers import get_linear_schedule_with_warmup

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "data", "test_dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "models", "sms-shield-finetuned")
EPOCHS = 6
BATCH_SIZE = 8
LR = 5e-6  # ниже базового LR, т.к. дообучаем уже обученную модель
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
    split = int(len(rows) * 0.85)
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


def metrics(model, loader):
    model.eval()
    correct, total = 0, 0
    tp = fp = fn = 0
    with torch.no_grad():
        for batch in loader:
            ids = batch["input_ids"].to(device)
            mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            out = model(input_ids=ids, attention_mask=mask)
            preds = out.logits.argmax(dim=-1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
            tp += ((preds == 1) & (labels == 1)).sum().item()
            fp += ((preds == 1) & (labels == 0)).sum().item()
            fn += ((preds == 0) & (labels == 1)).sum().item()
    acc = correct / total if total else 0.0
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return acc, prec, rec, f1


def main():
    print("Загрузка датасета...")
    train_data, val_data = load_data()
    print(f"Обучение: {len(train_data)} SMS | Валидация: {len(val_data)} SMS")

    if not os.path.isdir(MODEL_PATH):
        print(f"ОШИБКА: не найден существующий чекпоинт {MODEL_PATH}")
        sys.exit(1)

    print(f"\nЗагрузка существующего чекпоинта {MODEL_PATH}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
    model.to(device)

    train_loader = DataLoader(SMSDataset(train_data, tokenizer), batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(SMSDataset(val_data, tokenizer), batch_size=BATCH_SIZE)

    optimizer = AdamW(model.parameters(), lr=LR, weight_decay=0.01)
    total_steps = len(train_loader) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=max(1, total_steps // 10),
        num_training_steps=total_steps,
    )

    acc0, p0, r0, f0 = metrics(model, val_loader)
    print(f"\nДо дообучения: Acc={acc0:.1%} | Prec={p0:.1%} | Rec={r0:.1%} | F1={f0:.1%}")

    print(f"\nНачало дообучения ({EPOCHS} эпох на {device})...\n")
    best_f1 = f0
    best_acc = acc0
    t0 = time.time()

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
        acc, prec, rec, f1 = metrics(model, val_loader)
        elapsed = (time.time() - t0) / 60
        marker = " <-- лучший" if f1 > best_f1 else ""
        print(f"Эпоха {epoch}/{EPOCHS} | Loss: {avg_loss:.4f} | "
              f"Acc: {acc:.1%} | Prec: {prec:.1%} | Rec: {rec:.1%} | F1: {f1:.1%}"
              f" | {elapsed:.1f} мин{marker}")

        if f1 > best_f1:
            best_f1 = f1
            best_acc = acc
            model.save_pretrained(MODEL_PATH)
            tokenizer.save_pretrained(MODEL_PATH)

    total_min = (time.time() - t0) / 60
    print(f"\nГотово за {total_min:.1f} мин. Лучшая F1: {best_f1:.1%} | Acc: {best_acc:.1%}")
    print(f"Модель сохранена в: {MODEL_PATH}")


if __name__ == "__main__":
    main()
