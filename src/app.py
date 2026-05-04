from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from transformers import pipeline
import re
import logging
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'requests.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__, template_folder='templates')
CORS(app)

print("=" * 50)
print("Загрузка AI-модели...")
print("=" * 50)
MODEL_PATH = os.path.join(BASE_DIR, "models", "aegis-finetuned")
classifier = pipeline(
    "text-classification",
    model=MODEL_PATH,
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
    # Схемы «возврата денег» / recovery scam (RU)
    "вас обманули": "Мошенничество: 'вас обманули' — схема возврата денег жертвам",
    "вы были обмануты": "Мошенничество: схема повторного обмана жертв",
    "обманули": "Подозрительно: 'обманули' — возможная recovery-схема",
    "вернём деньги": "Мошенничество: 'вернём деньги' — повторный обман жертв",
    "компенсация за мошенничество": "Мошенничество: обещание компенсации — типичная recovery-схема",
    "помогаем жертвам": "Подозрительно: 'помогаем жертвам' мошенничества за плату",
    "возврат средств": "Подозрительно: 'возврат средств' с требованием предоплаты",
    "recuperăm banii": "Fraudă: 'recuperăm banii' — schema de înșelăciune secundară",
    "ați fost înșelat": "Fraudă: 'ați fost înșelat' — recovery scam",
    "compensație": "Suspect: 'compensație' — poate fi fraudă secundară",
    # Эротические услуги / эксплуатация (RU)
    "интим услуги": "Опасно: предложение интим-услуг через SMS",
    "интим-услуги": "Опасно: предложение интим-услуг через SMS",
    "эскорт": "Опасно: предложение эскорт-услуг",
    "досуг для взрослых": "Опасно: реклама услуг для взрослых",
    "съёмки для взрослых": "Опасно: вербовка для съёмок контента для взрослых",
    "работа для девушек": "Опасно: подозрительная 'работа для девушек' — риск эксплуатации",
    "подработка для девушек": "Опасно: 'подработка для девушек' — схема вербовки",
    "без опыта от 1000": "Подозрительно: нереалистичная подработка без опыта",
    "клуб ищет девушек": "Опасно: вербовка через SMS — риск эксплуатации",
    "модельный бизнес": "Подозрительно: 'модельный бизнес' через SMS — схема вербовки",
    "фотосессия оплата": "Подозрительно: предложение платной фотосессии через SMS",
    # Эротические услуги / эксплуатация (RO)
    "servicii intime": "Pericol: ofertă de servicii intime prin SMS",
    "escortă": "Pericol: ofertă de servicii escortă",
    "escorta": "Pericol: ofertă de servicii escortă",
    "agrement adulti": "Pericol: publicitate servicii pentru adulți",
    "agrement adulți": "Pericol: publicitate servicii pentru adulți",
    "filmari adulti": "Pericol: recrutare pentru conținut pentru adulți",
    "lucru pentru fete": "Pericol: 'lucru pentru fete' — risc de exploatare",
    "castiguri rapide fete": "Pericol: recrutare suspectă prin SMS",
    "câștiguri rapide fete": "Pericol: recrutare suspectă prin SMS",
    "club cauta fete": "Pericol: recrutare prin SMS — risc de exploatare",
    "afaceri modelling": "Suspect: 'modelling' prin SMS — posibilă schemă de recrutare",
    # Схемы «возврата денег» / recovery scam (RO)
    "ati fost inselat": "Fraudă: 'ați fost înșelat' — recovery scam",
    "recuperam banii": "Fraudă: 'recuperăm banii' — schema de înșelăciune secundară",
    "compensatie": "Suspect: 'compensatie' — poate fi fraudă secundară",
}

# Ключевые слова высокого риска — suspicious при ОДНОМ совпадении
HIGH_RISK_KEYWORDS = {
    "интим услуги", "интим-услуги", "эскорт", "досуг для взрослых",
    "съёмки для взрослых", "работа для девушек", "подработка для девушек",
    "клуб ищет девушек", "servicii intime", "escortă", "escorta",
    "agrement adulti", "agrement adulți", "filmari adulti", "filmări adulți",
    "lucru pentru fete", "club cauta fete", "castiguri rapide fete",
    "câștiguri rapide fete", "вас обманули", "вы были обмануты",
    "компенсация за мошенничество", "вернём деньги",
    "ati fost inselat", "recuperam banii",
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

        text_lower = text.lower()
        has_high_risk = any(kw in text_lower for kw in HIGH_RISK_KEYWORDS)

        if has_high_risk and not is_scam:
            verdict = "suspicious"
        elif len(reasons) >= 2 and not is_scam:
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
