import csv
import json
import sys
import urllib.request
import urllib.error

sys.stdout.reconfigure(encoding="utf-8")

API_URL = "http://127.0.0.1:5000/api/check"
DATASET_PATH = "data/test_dataset.csv"
RESULTS_PATH = "data/evaluation_results.csv"


def check_sms(text):
    payload = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def normalize(verdict):
    return "scam" if verdict in ("scam", "suspicious") else "safe"


def main():
    rows = []
    with open(DATASET_PATH, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Датасет загружен: {len(rows)} SMS\n")

    results = []
    for i, row in enumerate(rows, 1):
        text = row["text"]
        expected = row["label"]
        language = row["language"]

        try:
            data = check_sms(text)
            raw_verdict = data.get("verdict", "safe")
            confidence = data.get("confidence", 0)
            predicted = normalize(raw_verdict)
            correct = predicted == expected
        except Exception as e:
            print(f"  [!] Ошибка при запросе #{i}: {e}")
            raw_verdict = "error"
            confidence = 0
            predicted = "safe"
            correct = False

        status = "OK" if correct else "XX"
        print(f"[{status}] [{language.upper()}] {expected.upper():4} -> {predicted.upper():4} ({confidence:.0%}) | {text[:60]}")

        results.append({
            "text": text,
            "language": language,
            "expected": expected,
            "predicted": predicted,
            "raw_verdict": raw_verdict,
            "confidence": round(confidence, 3),
            "correct": correct,
        })

    with open(RESULTS_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    total = len(results)
    correct_count = sum(1 for r in results if r["correct"])
    accuracy = correct_count / total

    true_positives = sum(1 for r in results if r["predicted"] == "scam" and r["expected"] == "scam")
    false_positives = sum(1 for r in results if r["predicted"] == "scam" and r["expected"] == "safe")
    false_negatives = sum(1 for r in results if r["predicted"] == "safe" and r["expected"] == "scam")

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    print("\n" + "=" * 50)
    print(f"  Accuracy  (точность):  {accuracy:.1%}  ({correct_count}/{total})")
    print(f"  Precision (scam):      {precision:.1%}")
    print(f"  Recall    (scam):      {recall:.1%}")
    print(f"  F1-score  (scam):      {f1:.1%}")
    print("=" * 50)
    print(f"\nРезультаты сохранены в {RESULTS_PATH}")


if __name__ == "__main__":
    main()
