from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from transformers import pipeline
import re
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('requests.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
CORS(app)

print("=" * 50)
print("Загрузка AI-модели...")
print("=" * 50)
classifier = pipeline(
    "text-classification",
    model="models/sms-shield-finetuned",
    device=0  # GPU
)
print("Модель загружена! Сервер готов к работе.")
print("=" * 50)

SUSPICIOUS_KEYWORDS = {
    # Призы / выигрыши (RO)
    "câștigat": "Cuvânt suspect: 'câștigat' — tipic pentru mesaje frauduloase",
    "câștig": "Cuvânt suspect: 'câștig' — tipic pentru escrocherii",
    "premiu": "Cuvânt suspect: 'premiu' — tentativă de înșelăciune",
    "felicitări": "Cuvânt suspect: 'felicitări' în context financiar",
    "tombola": "Cuvânt suspect: 'tombola' — schemă de câștig fals",
    "voucher": "Cuvânt suspect: 'voucher' — poate fi fraudulos",
    # Призы / выигрыши (RU)
    "выиграл": "Подозрительное: 'выиграл' — типичная схема мошенничества",
    "выиграли": "Подозрительное: 'выиграли'",
    "приз": "Подозрительное: 'приз' — типичная приманка мошенников",
    "поздравляем": "Подозрительное: 'поздравляем' + ссылка — мошенническая схема",
    "победитель": "Подозрительное: 'победитель' — фиктивный розыгрыш",
    "розыгрыш": "Подозрительное: 'розыгрыш' — типичная мошенническая приманка",
    # Срочность (RO)
    "urgent": "Создаёт ложное чувство срочности: 'urgent'",
    "imediat": "Создаёт ложное чувство срочности: 'imediat'",
    "acum": "Cuvânt de urgență: 'acum' — presiune artificială",
    # Срочность (RU)
    "срочно": "Создаёт ложное чувство срочности: 'срочно'",
    "немедленно": "Создаёт ложное чувство срочности: 'немедленно'",
    "сейчас": "Давление срочности: 'сейчас'",
    # Банки / блокировки (RO)
    "blocat": "Имитация банка: 'blocat' — фальшивое предупреждение",
    "suspendat": "Имитация банка: 'suspendat' — фальшивое предупреждение",
    "verificare": "Запрос верификации: 'verificare' — типичный фишинг",
    "confirmare": "Запрос подтверждения: 'confirmare'",
    "deblocare": "Имитация банка: 'deblocare' — фишинг",
    "reziliat": "Угроза расторжения: 'reziliat' — давление на жертву",
    # Банки / блокировки (RU)
    "заблокирован": "Имитация банка: 'заблокирован' — фишинговая схема",
    "заблокирована": "Имитация банка: 'заблокирована'",
    "заморожен": "Имитация банка: 'заморожен' — угроза для давления",
    "подтвердите": "Запрос подтверждения — фишинговый признак",
    "верифицируйте": "Запрос верификации — типичный фишинг",
    "взломан": "Ложная угроза: 'взломан' — паника для кражи данных",
    "скомпрометирован": "Ложная угроза: 'скомпрометирован'",
    # Деньги / кредиты
    "без справок": "Мошеннический кредит: 'без справок'",
    "без документов": "Мошеннический кредит: 'без документов'",
    "fără acte": "Credit fraudulos: 'fără acte'",
    "fără garanții": "Ofertă frauduloasă: 'fără garanții'",
    "гарантированный доход": "Финансовая пирамида: 'гарантированный доход'",
    "profit garantat": "Schema Ponzi: 'profit garantat'",
    "investiți": "Alertă investiție: 'investiți' cu promisiuni nerealiste",
    "инвестируйте": "Финансовая пирамида: 'инвестируйте'",
    # Полиция / госорганы (мошеннические)
    "сотрудник полиции": "Мошенничество от имени полиции — полиция не пишет SMS с требованиями",
    "следователь": "Мошенничество: 'следователь' в SMS — полиция так не работает",
    "задолженность": "Мошенническое давление: 'задолженность' + ссылка",
    "datorie": "Presiune frauduloasă: 'datorie' + link",
    "amendă": "Fraudă: 'amendă' prin SMS cu link — nu este practică oficială",
    "штраф": "Мошенничество: 'штраф' через SMS + ссылка",
    # EN
    "winner": "Suspicious: 'winner'",
    "won": "Suspicious: 'won'",
    "claim": "Suspicious: 'claim'",
    "free": "Suspicious: 'free' offer",
}

LOCAL_BRANDS = [
    "MAIB", "MICB", "Victoriabank", "Moldindconbank", "Mobiasbancă", "Mobiasbanca",
    "Moldtelecom", "Orange", "Moldcell", "BNM", "Moldova Agroindbank",
    "FISC", "CNAS", "Primăria", "Primaria", "Poșta Moldovei", "Posta Moldovei",
    "Nova Poshta", "Premier Energy", "Union Fenosa", "Moldovagaz",
    "Kaufland", "Lidl", "999.md", "emag.md",
]

SHORT_LINK_DOMAINS = ["bit.ly", "tinyurl", "t.co", "goo.gl", "ow.ly",
                      "is.gd", "buff.ly", "cutt.ly", "rb.gy", "shorturl.at"]


def find_reasons(text):
    reasons = []
    text_lower = text.lower()

    found_keywords = set()
    for keyword, explanation in SUSPICIOUS_KEYWORDS.items():
        if keyword.lower() in text_lower and keyword.lower() not in found_keywords:
            reasons.append(explanation)
            found_keywords.add(keyword.lower())

    for domain in SHORT_LINK_DOMAINS:
        if domain in text_lower:
            reasons.append(f"Содержит укороченную ссылку: {domain}")

    if re.search(r'https?://|www\.', text_lower):
        if not any(domain in text_lower for domain in SHORT_LINK_DOMAINS):
            reasons.append("Содержит внешнюю ссылку")

    has_link = bool(re.search(r'https?://|www\.|bit\.ly|tinyurl', text_lower))
    for brand in LOCAL_BRANDS:
        if brand.lower() in text_lower and has_link:
            reasons.append(f"Имитация бренда {brand} + ссылка (типичный фишинг)")
            break

    if re.search(r'\b(cod|код|password|parol|пароль)\b', text_lower):
        if has_link or "sms" in text_lower:
            reasons.append("Запрос кода или пароля (банк никогда не просит код по SMS)")

    return reasons


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/check", methods=["POST"])
def check_sms():
    try:
        data = request.get_json()

        if not data or "text" not in data:
            return jsonify({"error": "Поле 'text' обязательно"}), 400

        text = data.get("text", "").strip()

        if not text:
            return jsonify({"error": "Текст не может быть пустым"}), 400

        if len(text) > 1000:
            return jsonify({"error": "Текст слишком длинный (максимум 1000 символов)"}), 400

        logging.info(f"CHECK: {text[:100]}")

        result = classifier(text)[0]

        top_label = result["label"]
        confidence = float(result["score"])

        is_scam = top_label == "scam"
        verdict = "scam" if is_scam else "safe"

        reasons = find_reasons(text)

        if len(reasons) >= 2 and not is_scam:
            verdict = "suspicious"

        response = {
            "verdict": verdict,
            "confidence": round(confidence, 3),
            "reasons": reasons,
            "text_length": len(text),
            "ai_label": top_label
        }

        logging.info(f"RESULT: {verdict} ({confidence:.2%})")

        return jsonify(response)

    except Exception as e:
        logging.error(f"ERROR: {str(e)}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model_loaded": True})


if __name__ == "__main__":
    print("\nСервер запускается на http://127.0.0.1:5000")
    print("Чтобы остановить — нажми Ctrl+C\n")
    app.run(debug=False, port=5000, host="0.0.0.0")
