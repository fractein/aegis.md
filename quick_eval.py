"""Быстрая оценка метрик финальной модели без запуска сервера."""
import sys, csv, torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

sys.stdout.reconfigure(encoding="utf-8")

MODEL_PATH = "models/sms-shield-finetuned"
DATASET_PATH = "data/test_dataset.csv"
LABEL2ID = {"safe": 0, "scam": 1}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.to(device)
model.eval()

rows = []
with open(DATASET_PATH, encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))

tp = fp = fn = tn = 0
for row in rows:
    text, expected = row["text"], row["label"]
    enc = tokenizer(text, truncation=True, max_length=128, return_tensors="pt").to(device)
    with torch.no_grad():
        logit = model(**enc).logits
    pred_id = logit.argmax(-1).item()
    pred = "scam" if pred_id == 1 else "safe"

    if pred == "scam" and expected == "scam": tp += 1
    elif pred == "scam" and expected == "safe": fp += 1
    elif pred == "safe" and expected == "scam": fn += 1
    else: tn += 1

total = tp + fp + fn + tn
acc = (tp + tn) / total
prec = tp / (tp + fp) if (tp + fp) else 0
rec = tp / (tp + fn) if (tp + fn) else 0
f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0

print(f"Dataset: {total} SMS ({tp+fn} scam / {tn+fp} safe)")
print(f"Accuracy:  {acc:.1%}  ({tp+tn}/{total})")
print(f"Precision: {prec:.1%}")
print(f"Recall:    {rec:.1%}")
print(f"F1-score:  {f1:.1%}")
print(f"Errors:    FP={fp} (safe→scam)  FN={fn} (scam→safe)")
