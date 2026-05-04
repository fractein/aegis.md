"""
Генератор большого датасета SMS для Aegis.md.
Создаёт ~1000 разнообразных примеров через шаблоны с подстановкой.
"""
import csv
import os
import random
import sys

sys.stdout.reconfigure(encoding="utf-8")

random.seed(42)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "test_dataset.csv")

# ─── Подстановки ──────────────────────────────────────────────────────────────

BANKS_RO = ["MAIB", "MICB", "Victoriabank", "Mobiasbancă", "Moldindconbank", "OTP Bank", "EuroCreditBank"]
BANKS_RU = ["MAIB", "MICB", "Викториабанк", "Мобиасбанка", "Молдиндконбанк", "OTP Bank"]
GOV_RO = ["FISC", "CNAS", "Primăria Chișinău", "Vama Moldovei", "ANRE", "MAI"]
GOV_RU = ["FISC", "CNAS", "Примэрия Кишинёва", "Таможня Молдовы", "МВД"]
TELECOM_RO = ["Orange", "Moldcell", "Moldtelecom", "Starnet"]
TELECOM_RU = ["Orange", "Moldcell", "Moldtelecom", "Старнет"]
DELIVERY_RO = ["Poșta Moldovei", "Nova Poshta", "DHL", "DPD", "Posta Romana"]
DELIVERY_RU = ["Почта Молдовы", "Nova Poshta", "DHL", "DPD"]
SHOPS_RO = ["Kaufland", "Lidl", "Linella", "Nr.1", "999.md", "emag.md", "darwin.md"]
SHOPS_RU = ["Kaufland", "Lidl", "Linella", "Nr.1", "999.md", "emag.md"]
SHORT_DOMAINS = ["bit.ly", "tinyurl.com", "cutt.ly", "is.gd", "ow.ly", "shorturl.at", "rb.gy", "t.ly"]
FAKE_TLDS = [".ml", ".tk", ".xyz", ".ru", ".cf", ".ga", ".cc"]
AMOUNTS = [500, 1000, 2000, 3000, 5000, 7500, 10000, 15000, 20000, 25000, 30000, 50000, 100000]
SMALL_AMOUNTS = [25, 30, 35, 50, 75, 100, 150, 200, 250, 300, 500]
DEVICES = ["iPhone 15", "iPhone 16 Pro", "Samsung Galaxy S24", "MacBook Pro", "AirPods Pro", "PlayStation 5", "Xbox Series X"]
PHONES_MD = lambda: f"068{random.randint(100000,999999)}"
WHATSAPP = lambda: f"+373 6{random.randint(0,9)} {random.randint(100,999)} {random.randint(100,999)}"

NAMES_RU = ["Мама", "Папа", "Лена", "Анна", "Виктор", "Сергей", "Игорь", "Ольга", "Друг", "Коллега", "Настя"]
NAMES_RO = ["Mama", "Tata", "Ana", "Maria", "Ion", "Andrei", "Vlad", "Elena", "Diana", "Mihai"]
TIMES = ["10:00", "11:30", "14:00", "15:30", "16:45", "18:00", "19:00", "20:30"]
DAYS_RO = ["luni", "marți", "miercuri", "joi", "vineri", "sâmbătă", "duminică"]
DAYS_RU = ["понедельник", "вторник", "среду", "четверг", "пятницу", "субботу", "воскресенье"]


def fake_link(brand=None):
    base = (brand.lower().replace(" ", "-").replace("ă", "a").replace("ș", "s")
            .replace("ț", "t").replace("ё", "e") if brand else "verify")
    return f"{base}-secure{random.choice(FAKE_TLDS)}/{random.choice(['login','verify','confirm','deblocare','activate'])}"


def short_link():
    return f"{random.choice(SHORT_DOMAINS)}/{random.choice('abcdefghijkmnpqrstuvwxyz')}{random.randint(1000,9999)}"


# ─── Шаблоны: SCAM ────────────────────────────────────────────────────────────

scam_templates = [
    # Банковский фишинг RO
    lambda: f"{random.choice(BANKS_RO)}: Cardul dvs. a fost blocat din cauza activității suspecte. Pentru deblocare accesați: {fake_link(random.choice(BANKS_RO))}",
    lambda: f"{random.choice(BANKS_RO)}: Contul dvs. a fost suspendat. Verificați identitatea urgent: {short_link()}",
    lambda: f"ATENȚIE {random.choice(BANKS_RO)}: tranzacție suspectă de {random.choice(AMOUNTS)} MDL. Confirmați: {fake_link()}",
    lambda: f"{random.choice(BANKS_RO)}: Parola dvs. a fost compromisă. Resetați acum: {short_link()}",
    lambda: f"Cardul Visa de la {random.choice(BANKS_RO)} expiră azi. Reînnoiți: {fake_link()}",

    # Банковский фишинг RU
    lambda: f"{random.choice(BANKS_RU)}: Ваша карта заблокирована. Срочно перейдите для разблокировки: {fake_link(random.choice(BANKS_RO))}",
    lambda: f"{random.choice(BANKS_RU)}: Подозрительная операция на {random.choice(AMOUNTS)} лей. Подтвердите: {short_link()}",
    lambda: f"ВНИМАНИЕ {random.choice(BANKS_RU)}: попытка входа в ваш аккаунт из неизвестного устройства. Заблокировать: {short_link()}",
    lambda: f"{random.choice(BANKS_RU)}: Ваш счёт заморожен. Введите код подтверждения на сайте: {fake_link()}",
    lambda: f"Срочно! Ваша банковская карта ({random.choice(BANKS_RU)}) скомпрометирована. Защитите средства: {short_link()}",

    # Призы / выигрыши RO
    lambda: f"Felicitări! Ai câștigat {random.choice(AMOUNTS)} lei la tombola {random.choice(SHOPS_RO + TELECOM_RO)}! Ridică premiul: {short_link()}",
    lambda: f"Ai fost selectat câștigător! Premiul: {random.choice(DEVICES)}. Accesează urgent: {short_link()}",
    lambda: f"FELICITĂRI! Ești câștigătorul concursului {random.choice(SHOPS_RO)}! Voucher de {random.choice(AMOUNTS)} lei: {fake_link()}",
    lambda: f"Premiul tău {random.choice(DEVICES)} te așteaptă! Confirmă datele: {short_link()}",
    lambda: f"{random.choice(TELECOM_RO)}: Ați câștigat {random.choice(AMOUNTS)} minute gratuite + {random.choice([1,2,3,5])} luni internet! Activați: {short_link()}",

    # Призы / выигрыши RU
    lambda: f"Поздравляем! Вы выиграли {random.choice(AMOUNTS)} лей в розыгрыше {random.choice(SHOPS_RU + TELECOM_RU)}! Ссылка для получения: {short_link()}",
    lambda: f"Вы стали победителем розыгрыша {random.choice(DEVICES)}! Срочно перейдите: {short_link()}",
    lambda: f"ПОЗДРАВЛЯЕМ! Главный приз — {random.choice(DEVICES)}. Заберите по ссылке: {fake_link()}",
    lambda: f"Ваш номер выиграл {random.choice(AMOUNTS)} лей! Получить приз: {short_link()}",
    lambda: f"{random.choice(TELECOM_RU)}: Вы выиграли {random.choice([3,6,12])} месяцев бесплатного интернета! Активируйте: {short_link()}",

    # Госорганы RO
    lambda: f"{random.choice(GOV_RO)}: Datorie fiscală {random.choice(AMOUNTS)} lei. Achitați urgent sau veți fi acționat în instanță: {short_link()}",
    lambda: f"{random.choice(GOV_RO)}: Plată socială {random.choice(AMOUNTS)} lei disponibilă. Activați cardul: {fake_link()}",
    lambda: f"Primăria: Amendă {random.choice(SMALL_AMOUNTS)*10} lei pentru parcare ilegală. Achitați online: {short_link()}",
    lambda: f"VAMA: Coletul dvs. internațional necesită declarație. Completați: {short_link()}",
    lambda: f"Citație de la procuratura: vă prezentați urgent. Detalii: {short_link()}",

    # Госорганы RU
    lambda: f"{random.choice(GOV_RU)}: У вас задолженность {random.choice(AMOUNTS)} лей. Оплатите сейчас: {short_link()}",
    lambda: f"{random.choice(GOV_RU)}: Социальная выплата {random.choice(AMOUNTS)} лей доступна. Активируйте карту: {fake_link()}",
    lambda: f"Примэрия: Штраф {random.choice(SMALL_AMOUNTS)*10} лей за нарушение ПДД. Оплатить: {short_link()}",
    lambda: f"Суд Молдовы: Повестка на заседание. Подробности: {short_link()}",
    lambda: f"Сотрудник полиции: На ваше имя оформлен кредит мошенниками. Срочно переведите деньги на безопасный счёт {random.randint(1000000,9999999)}",

    # Доставки RO
    lambda: f"{random.choice(DELIVERY_RO)}: Coletul #MD{random.randint(100000,999999)} reținut la vamă. Achitați {random.choice(SMALL_AMOUNTS)} lei: {short_link()}",
    lambda: f"{random.choice(DELIVERY_RO)}: Coletul dvs. necesită achitarea taxelor vamale {random.choice(SMALL_AMOUNTS)} lei: {fake_link()}",
    lambda: f"Coletul tău nu poate fi livrat. Reprogramare aici: {short_link()}",

    # Доставки RU
    lambda: f"{random.choice(DELIVERY_RU)}: Посылка задержана на таможне. Оплатите {random.choice(SMALL_AMOUNTS)} лей: {short_link()}",
    lambda: f"{random.choice(DELIVERY_RU)}: Ваша посылка #UA{random.randint(100000,999999)} ожидает оплаты {random.choice(SMALL_AMOUNTS)} лей: {fake_link()}",
    lambda: f"Посылка возвращена отправителю. Доплатите за хранение {random.choice(SMALL_AMOUNTS)} лей: {short_link()}",

    # Кредиты / займы (RO)
    lambda: f"Credite rapide fără acte! Aprobat în {random.choice([5,10,15])} minute. {random.choice(AMOUNTS)} lei pe card: {short_link()}",
    lambda: f"Cererea dvs. de credit a fost aprobată! Ridicați {random.choice(AMOUNTS)} lei: {fake_link()}",
    lambda: f"Bani rapid acasă! Fără garanții, fără verificări. Sună la {PHONES_MD()}",

    # Кредиты / займы (RU)
    lambda: f"Быстрые деньги без справок! Одобрение за {random.choice([5,10,15])} минут. {random.choice(AMOUNTS)} лей на карту: {short_link()}",
    lambda: f"Ваша заявка на кредит одобрена! Получите {random.choice(AMOUNTS)} лей: {fake_link()}",
    lambda: f"Деньги под 0%! Без проверок, без документов. WhatsApp: {WHATSAPP()}",

    # Инвестиции / пирамиды
    lambda: f"Investiți {random.choice(SMALL_AMOUNTS)} lei și primiți {random.choice(AMOUNTS)} lei în {random.choice([3,5,7,10])} zile! Profit garantat: {short_link()}",
    lambda: f"Câștigă {random.choice(AMOUNTS)} euro pe săptămână! Sistem dovedit de investiții crypto: {short_link()}",
    lambda: f"Инвестируйте {random.choice(SMALL_AMOUNTS)} лей и получите {random.choice(AMOUNTS)} за неделю! Гарантированно: {fake_link()}",
    lambda: f"Заработай {random.choice(AMOUNTS)} евро в неделю на криптовалюте! Проверенная схема: {short_link()}",
    lambda: f"Bitcoin a explodat! Investiți acum și câștigați {random.choice([5,10,20])}x: {short_link()}",

    # Recovery scam
    lambda: f"Vas obmanuli? Ați fost înșelat? Vă ajutăm să recuperați banii. Detalii: {short_link()}",
    lambda: f"Вас обманули мошенники? Поможем вернуть деньги! Бесплатная консультация: {WHATSAPP()}",
    lambda: f"Vy byli obmanuty? Compensație pentru victimele fraudei disponibilă: {short_link()}",
    lambda: f"Recuperăm banii pierduți la cazinouri online! Garanție 100%: {short_link()}",

    # Интим / эксплуатация (RU)
    lambda: f"Работа для девушек, заработок от {random.choice([1000,1500,2000,3000])} лей в день. Без опыта, обучение бесплатно. WhatsApp: {WHATSAPP()}",
    lambda: f"Подработка для девушек {random.randint(18,25)}+. Высокая оплата, гибкий график. Пиши: {WHATSAPP()}",
    lambda: f"Клуб ищет девушек {random.randint(18,30)}+ для работы. Зарплата от {random.choice(AMOUNTS)} лей/мес. Telegram: @{random.choice(['club','vip','luxury','elite'])}_{random.randint(100,999)}",
    lambda: f"Интим услуги, дискретно, Кишинёв. Звони {PHONES_MD()}",
    lambda: f"Срочно требуются девушки модельной внешности. Высокий доход. {WHATSAPP()}",
    lambda: f"Эскорт услуги премиум, высокая оплата, для девушек {random.randint(18,28)}+: {short_link()}",

    # Интим / эксплуатация (RO)
    lambda: f"Lucru pentru fete, câștiguri de la {random.choice([1000,1500,2000,3000])} lei pe zi. Fără experiență. WhatsApp: {WHATSAPP()}",
    lambda: f"Servicii intime, discret, Chișinău. Sună acum: {PHONES_MD()}",
    lambda: f"Club caută fete {random.randint(18,30)}+ pentru lucru. Câștiguri mari. Telegram: @club_{random.randint(100,999)}",
    lambda: f"Escortă premium Chișinău, câștiguri rapide fete. Detalii: {short_link()}",
    lambda: f"Fete modele căutate, câștig garantat {random.choice(AMOUNTS)} lei/lună. Sună: {PHONES_MD()}",

    # Romance / развод
    lambda: f"Salut, sunt o fată de {random.randint(18,25)} ani, vreau să te cunosc. Profilul meu: {short_link()}",
    lambda: f"Привет, я познакомилась с тобой через приложение. Мой профиль: {short_link()}",
    lambda: f"Hi! I saw your profile, want to chat? My pics: {short_link()}",

    # Tech support scam
    lambda: f"Microsoft: Computerul dvs. este infectat cu virus. Sunați urgent {PHONES_MD()}",
    lambda: f"Apple Support: Apple ID-ul dvs. va fi blocat. Verificați: {short_link()}",
    lambda: f"Microsoft: Ваш компьютер заражён вирусом. Срочно позвоните {PHONES_MD()}",
    lambda: f"Google: Ваш аккаунт будет удалён через 24 часа. Подтвердите: {short_link()}",
    lambda: f"Ваш аккаунт WhatsApp взломан! Подтвердите личность: {short_link()}",

    # Соц. сети / мессенджеры
    lambda: f"Instagram: Suspect activity on your account. Verify now: {short_link()}",
    lambda: f"Telegram: Tentativă de conectare suspectă. Confirmați: {fake_link()}",
    lambda: f"Facebook: Ваш аккаунт будет заблокирован. Подтвердите данные: {short_link()}",

    # Crypto
    lambda: f"Bitcoin gratis! Reclamă acum {random.choice([0.001,0.01,0.1])} BTC: {short_link()}",
    lambda: f"Ethereum airdrop! Получи {random.choice([100,500,1000])} токенов бесплатно: {fake_link()}",
    lambda: f"Investește în Crypto Moldova - profit 30% lunar garantat! {short_link()}",

    # Разное
    lambda: f"URGENT: Контракт {random.choice(GOV_RU)} расторгнут. Подтвердите данные: {short_link()}",
    lambda: f"Получите гуманитарную помощь {random.choice(AMOUNTS)} лей! Регистрация: {fake_link()}",
    lambda: f"Ajutor umanitar disponibil pentru cetățenii Moldovei. Înregistrați-vă: {fake_link()}",
    lambda: f"Снять наличные с любой карты без комиссии! WhatsApp: {WHATSAPP()}",
    lambda: f"Ofertă unică {random.choice(DEVICES)} la doar {random.choice([999,1499,1999])} lei! Doar azi: {short_link()}",
    lambda: f"Cazino online bonus {random.choice(AMOUNTS)} lei la înregistrare! {short_link()}",
    lambda: f"Онлайн казино: бонус {random.choice(AMOUNTS)} лей при регистрации! {short_link()}",
    lambda: f"Vă datorăm {random.choice(AMOUNTS)} lei compensație. Detalii: {short_link()}",
    lambda: f"Возврат налогов {random.choice(AMOUNTS)} лей одобрен! Перейдите: {fake_link()}",
    lambda: f"Petrom Moldova: Ai câștigat 1 an de combustibil gratis! {short_link()}",
]


# ─── Шаблоны: SAFE ────────────────────────────────────────────────────────────

safe_templates = [
    # Банковские уведомления (реальный формат)
    lambda: f"{random.choice(BANKS_RO)}: Tranzacție {random.choice(SMALL_AMOUNTS)} MDL. Sold: {random.randint(500,15000)} MDL. {random.randint(1,28):02d}.{random.randint(1,12):02d}.2026 {random.choice(TIMES)}",
    lambda: f"{random.choice(BANKS_RU)}: Списание {random.choice(SMALL_AMOUNTS)} MDL. Остаток: {random.randint(500,15000)} MDL. {random.randint(1,28):02d}.{random.randint(1,12):02d}.2026 {random.choice(TIMES)}",
    lambda: f"{random.choice(BANKS_RO)}: Încasare {random.choice(AMOUNTS)} MDL. Sold: {random.randint(1000,30000)} MDL.",
    lambda: f"{random.choice(BANKS_RU)}: Зачисление {random.choice(AMOUNTS)} MDL. Баланс: {random.randint(1000,30000)} MDL.",
    lambda: f"{random.choice(BANKS_RO)}: Codul dvs. de confirmare este: {random.randint(100000,999999)}. Nu îl comunicați nimănui.",
    lambda: f"{random.choice(BANKS_RU)}: Ваш код подтверждения: {random.randint(100000,999999)}. Никому не сообщайте.",
    lambda: f"{random.choice(BANKS_RO)}: Plata pentru utilități a fost procesată cu succes. Suma: {random.choice(SMALL_AMOUNTS)*5} MDL.",
    lambda: f"{random.choice(BANKS_RU)}: Платёж за коммунальные услуги принят. Сумма: {random.choice(SMALL_AMOUNTS)*5} MDL.",

    # Telecom уведомления
    lambda: f"{random.choice(TELECOM_RO)}: Sold internet {random.choice([5,8,10,15,20])} GB. Valabil până pe {random.randint(1,28):02d}.{random.randint(1,12):02d}.2026.",
    lambda: f"{random.choice(TELECOM_RU)}: Остаток интернета {random.choice([5,8,10,15,20])} ГБ. До {random.randint(1,28):02d}.{random.randint(1,12):02d}.2026.",
    lambda: f"{random.choice(TELECOM_RO)}: Tariful dvs. lunar a fost reînnoit. {random.choice([300,500,750])} minute + internet.",
    lambda: f"{random.choice(TELECOM_RU)}: Ваш тариф продлён. {random.choice([300,500,750])} минут + интернет.",
    lambda: f"{random.choice(TELECOM_RO)}: Sold cont: {random.choice(SMALL_AMOUNTS)} MDL. Reîncărcare: *100#",
    lambda: f"{random.choice(TELECOM_RU)}: Баланс: {random.choice(SMALL_AMOUNTS)} MDL. Пополнить: *100#",

    # Доставки (нормальные)
    lambda: f"{random.choice(DELIVERY_RO)}: Comanda #{random.randint(10000,99999)} a fost livrată cu succes. Mulțumim!",
    lambda: f"{random.choice(DELIVERY_RU)}: Заказ #{random.randint(10000,99999)} доставлен. Спасибо!",
    lambda: f"{random.choice(SHOPS_RO)}: Comanda dvs. a fost expediată. Livrare estimată: {random.randint(1,5)} zile lucrătoare.",
    lambda: f"{random.choice(SHOPS_RU)}: Ваш заказ отправлен. Доставка через {random.randint(1,5)} рабочих дней.",
    lambda: f"{random.choice(DELIVERY_RO)}: Coletul vă așteaptă la oficiul poștal. Cod: {random.randint(1000,9999)}",

    # Личные сообщения RU
    lambda: f"{random.choice(NAMES_RU)}: Привет, как дела? Давай встретимся в {random.choice(DAYS_RU)}",
    lambda: f"{random.choice(NAMES_RU)}, я уже еду домой, буду через {random.choice([15,20,30,45])} минут",
    lambda: f"Не забудь {random.choice(['купить хлеб','забрать ребёнка','позвонить маме','купить молоко'])}, пожалуйста",
    lambda: f"{random.choice(NAMES_RU)}: документы на столе, не забудь взять",
    lambda: f"Встреча перенесена на {random.choice(DAYS_RU)} в {random.choice(TIMES)}",
    lambda: f"Привет! Не забудь про день рождения {random.choice(NAMES_RU)} в {random.choice(DAYS_RU)}",
    lambda: f"{random.choice(NAMES_RU)}: позвони когда освободишься, нужно обсудить",
    lambda: f"Я буду дома к {random.choice(TIMES)}, ужин будет?",
    lambda: f"Спасибо за вчера, было классно! Повторим в {random.choice(DAYS_RU)}?",
    lambda: f"{random.choice(NAMES_RU)}: жду тебя в кафе на {random.choice(['Стефан чел Маре','Пушкина','Когылничану','Дачия'])}",

    # Личные сообщения RO
    lambda: f"{random.choice(NAMES_RO)}: Salut, ce mai faci? Ne vedem {random.choice(DAYS_RO)}?",
    lambda: f"{random.choice(NAMES_RO)}, am ajuns acasă. Sunt la tine în {random.choice([15,20,30])} min",
    lambda: f"Nu uita să {random.choice(['cumperi pâine','iei copilul','suni mama','cumperi lapte'])}, te rog",
    lambda: f"{random.choice(NAMES_RO)}: documentele sunt pe birou, nu uita să le iei",
    lambda: f"Ședința se mută pe {random.choice(DAYS_RO)} la {random.choice(TIMES)}",
    lambda: f"Bună! Nu uita de ziua de naștere a {random.choice(NAMES_RO)} duminică!",
    lambda: f"{random.choice(NAMES_RO)}: sună-mă când ești liber, trebuie să discutăm",
    lambda: f"Ajung acasă la {random.choice(TIMES)}, e cina pregătită?",
    lambda: f"Mulțumesc pentru ieri, a fost super! Repetăm {random.choice(DAYS_RO)}?",
    lambda: f"{random.choice(NAMES_RO)}: te aștept la cafenea pe {random.choice(['Ștefan cel Mare','Pușkin','Kogălniceanu'])}",

    # Медицина
    lambda: f"Reminder: programare la medic {random.choice(DAYS_RO)} la {random.choice(TIMES)}. Clinica {random.choice(['Medpark','Galaxia','Excellence'])}.",
    lambda: f"Напоминание: запись к врачу в {random.choice(DAYS_RU)} в {random.choice(TIMES)}. Клиника {random.choice(['Медпарк','Галаксия','Эксселенс'])}.",
    lambda: f"IMSP: Rezultatele analizelor sunt disponibile. Le puteți ridica de luni.",
    lambda: f"IMSP: Результаты анализов готовы. Можно забрать с понедельника.",
    lambda: f"Farmacia: Comanda dvs. este gata. Programul: 9-21.",

    # Госуслуги (легитимные предупреждения)
    lambda: f"Poliția Moldovei avertizează: nu accesați linkuri suspecte din SMS! Banca nu cere date prin mesaje.",
    lambda: f"BNM avertizează: site-uri false care imită băncile moldovenești sunt active. Verificați adresa.",
    lambda: f"Полиция Молдовы предупреждает: не переходите по ссылкам в подозрительных SMS!",
    lambda: f"Кишинев в теме: Внимание! Снова активизировались мошенники под видом банков. Не доверяйте!",
    lambda: f"ATENȚIE: Schemă nouă de fraudă - nu transferați bani la cererea unor necunoscuți!",

    # Магазины
    lambda: f"{random.choice(SHOPS_RO)}: Puncte bonus disponibile: {random.randint(50,500)}. Valabile până pe {random.randint(1,28):02d}.{random.randint(1,12):02d}.2026.",
    lambda: f"{random.choice(SHOPS_RU)}: Ваши бонусы: {random.randint(50,500)}. Действительны до {random.randint(1,28):02d}.{random.randint(1,12):02d}.2026.",
    lambda: f"{random.choice(SHOPS_RO)}: Reduceri de pana la 50% in week-end! Magazinele sunt deschise 9-22.",
    lambda: f"{random.choice(SHOPS_RU)}: Скидки до 50% в выходные! Магазины открыты 9-22.",

    # Коммунальные платежи
    lambda: f"Premier Energy: Factura lunară {random.choice([200,300,450,600])} lei. Scadență: {random.randint(15,28)}.{random.randint(1,12):02d}.",
    lambda: f"Moldovagaz: Платёж за газ {random.choice([200,300,450,600])} лей принят. Спасибо.",
    lambda: f"Apă-Canal: Plata pentru apă {random.choice([100,150,200])} lei a fost înregistrată.",
    lambda: f"Moldelectrica: Электричество {random.choice([200,300,400])} лей оплачено.",
    lambda: f"Union Fenosa Distribuție: Plata {random.choice([200,300,400])} MDL primită. Mulțumim.",

    # Рабочие
    lambda: f"Ședința echipei {random.choice(DAYS_RO)} la {random.choice(TIMES)}, sala de conferințe.",
    lambda: f"Совещание команды в {random.choice(DAYS_RU)} в {random.choice(TIMES)}, конференц-зал.",
    lambda: f"Salariul a fost virat pe card. Sumă: {random.randint(8000,25000)} MDL.",
    lambda: f"Зарплата перечислена. Сумма: {random.randint(8000,25000)} MDL.",
    lambda: f"Документы готовы, можешь забрать в офисе с {random.choice(TIMES)}",
    lambda: f"Documentele sunt gata, le poți ridica de la birou de la {random.choice(TIMES)}",

    # Образование
    lambda: f"Universitatea: Notele pentru sesiune sunt publicate. Verificați platforma.",
    lambda: f"Школа: Родительское собрание в {random.choice(DAYS_RU)} в {random.choice(TIMES)}",
    lambda: f"Liceul: Ședința cu părinții {random.choice(DAYS_RO)} la {random.choice(TIMES)}",

    # Транспорт
    lambda: f"Записал тебя на техосмотр {random.choice(DAYS_RU)} в {random.choice(TIMES)}",
    lambda: f"Автосервис: ваша машина готова, можно забрать после {random.choice(TIMES)}",
    lambda: f"Bolt: Plată finalizată {random.choice(SMALL_AMOUNTS)} MDL. Mulțumim!",
    lambda: f"Yandex Go: Поездка завершена. {random.choice(SMALL_AMOUNTS)} MDL списано.",

    # Подтверждения
    lambda: f"Cod de confirmare: {random.randint(100000,999999)}",
    lambda: f"Код подтверждения: {random.randint(100000,999999)}",
    lambda: f"Your verification code: {random.randint(100000,999999)}",
    lambda: f"OTP: {random.randint(1000,9999)}. Не сообщайте никому.",
    lambda: f"OTP: {random.randint(1000,9999)}. Nu comunicați nimănui.",
]


# ─── Генерация ────────────────────────────────────────────────────────────────

def detect_lang(text):
    cyrillic = sum(1 for c in text if 'Ѐ' <= c <= 'ӿ')
    latin = sum(1 for c in text if c.isalpha() and c.isascii() or c in 'ăâîșțĂÂÎȘȚ')
    return "ru" if cyrillic > latin else "ro"


def generate(target_per_class=500):
    rows = set()  # уникальность по тексту
    scam, safe = [], []

    while len(scam) < target_per_class:
        text = random.choice(scam_templates)()
        if text not in rows:
            rows.add(text)
            scam.append((text, "scam", detect_lang(text)))

    while len(safe) < target_per_class:
        text = random.choice(safe_templates)()
        if text not in rows:
            rows.add(text)
            safe.append((text, "safe", detect_lang(text)))

    all_rows = scam + safe
    random.shuffle(all_rows)

    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(["text", "label", "language"])
        w.writerows(all_rows)

    # статистика
    from collections import Counter
    cnt = Counter((r[1], r[2]) for r in all_rows)
    print(f"Сгенерировано: {len(all_rows)} SMS")
    print(f"  Scam RU: {cnt[('scam','ru')]:3} | Scam RO: {cnt[('scam','ro')]:3}")
    print(f"  Safe RU: {cnt[('safe','ru')]:3} | Safe RO: {cnt[('safe','ro')]:3}")
    print(f"\nСохранено: {OUTPUT_PATH}")


if __name__ == "__main__":
    generate(500)
