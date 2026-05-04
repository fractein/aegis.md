from transformers import pipeline

print("Загрузка модели, подождите...")
print("(первый запуск качает ~1 ГБ, потом будет быстро)")

classifier = pipeline(
    "zero-shot-classification",
    model="MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
)

print("Модель загружена!\n")

test_messages = [
    "Поздравляем! Вы выиграли 10000 лей, перейдите по ссылке bit.ly/win",
    "Привет, как дела? Давай встретимся в субботу",
    "Felicitări! Ai câștigat un premiu de 5000 lei, accesează linkul",
    "Salut, ce mai faci? Ne vedem mâine la ora 18?",
    "Ваша карта MAIB заблокирована. Срочно перейдите по ссылке для разблокировки",
    "Cardul dvs. MAIB a fost blocat. Accesați urgent link-ul pentru deblocare",
    "Mama, sună-mă când ai timp",
    "Ваш заказ доставлен. Спасибо за покупку!"
]

labels = ["fraudă sau înșelăciune", "mesaj normal sigur"]

for msg in test_messages:
    result = classifier(msg, candidate_labels=labels)
    top_label = result["labels"][0]
    confidence = result["scores"][0]

    verdict = "СКАМ" if "fraudă" in top_label else "НОРМ"

    print(f"{verdict} [{confidence:.2%}] — {msg}")
