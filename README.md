# Aegis.md

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1-lightgrey?logo=flask)
![AI](https://img.shields.io/badge/AI-XLM--RoBERTa-purple?logo=huggingface)
![ONIA](https://img.shields.io/badge/ONIA-2026-orange)

## Despre proiect

**Aegis.md** este o aplicație web cu inteligență artificială pentru detectarea mesajelor SMS frauduloase în limbile română și rusă. Sistemul combină un model AI antrenat local cu un motor de reguli bazat pe pattern-uri specifice fraudelor din Republica Moldova.

## Problema

Republica Moldova se confruntă cu o creștere alarmantă a fraudelor prin SMS: phishing bancar (MAIB, Victoriabank, MICB), scheme de câștiguri false, impostori care se prezintă drept polițiști sau funcționari FISC. Potrivit Poliției Moldovei, mii de cetățeni pierd anual sume semnificative din cauza acestor scheme.

## Soluția

Un detector în timp real care analizează textul SMS-ului și returnează:
- **Verdict**: `scam` / `suspicious` / `safe`
- **Nivelul de încredere** al modelului AI (%)
- **Motivele** detectării — cuvinte suspecte, link-uri scurtate, imitarea brandurilor locale

## Tehnologii utilizate

| Componentă | Tehnologie |
|---|---|
| Model AI | `xlm-roberta-base` (fine-tuned pe date moldovenești) |
| Framework web | Flask 3.1 |
| Procesare text | Transformers 5.7, PyTorch 2.11 (CUDA) |
| Frontend | HTML/CSS/JS — fără dependențe externe |
| Date antrenament | 120+ SMS-uri reale și sintetice (RO + RU) |

## Rezultate teste

| Metrică | Rezultat |
|---|---|
| Accuracy | **68.6%** (model de bază zero-shot) |
| Accuracy după fine-tuning | **100%** (validare internă) |
| Precision (scam) | **63.6%** → îmbunătățit după antrenare |
| Recall (scam) | **82.4%** |

> Modelul a fost antrenat pe GPU NVIDIA RTX 5070 Ti în ~15 minute pe un dataset de 120+ exemple specifice Republicii Moldova.

## Cum se rulează local

### 1. Clonați repository-ul
```bash
git clone https://github.com/<user>/aegis-md.git
cd aegis-md
```

### 2. Creați mediul virtual

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Mac / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalați dependențele
```bash
pip install -r requirements.txt
```

### 4. (Opțional) Antrenați modelul pe GPU
```bash
python finetune.py
```
> Prima rulare descarcă modelul de bază (~1.1 GB). GPU recomandat.

### 5. Porniți serverul
```bash
python src/app.py
```

### 6. Deschideți aplicația
```
http://127.0.0.1:5000
```

## Structura proiectului

```
aegis-md/
├── src/                        # Codul sursă al aplicației
│   ├── app.py                  # Server Flask + logica de detectare
│   ├── finetune.py             # Script de antrenare pe GPU
│   ├── evaluate.py             # Evaluarea preciziei modelului
│   └── templates/
│       └── index.html          # Interfața web (dark UI)
├── data/
│   ├── test_dataset.csv        # 120+ SMS-uri etichetate (RO + RU)
│   └── evaluation_results.csv
├── models/                     # Exclus din Git (500 MB)
│   └── sms-shield-finetuned/   # xlm-roberta-base fine-tuned
├── notebooks/
│   └── explorare_date.ipynb    # Analiza distribuției datelor
├── docs/
│   └── arhitectura.md          # Diagrama arhitecturii
├── requirements.txt
└── README.md
```

## Surse de date

Pattern-urile de fraudă sunt bazate pe:
- Avertismentele oficiale ale **Poliției Republicii Moldova** (politia.md)
- Cazuri publicate pe **Kișinău în Temă** (Telegram)
- Articole din **Moldova.org**, **Ziarul de Gardă** despre fraude SMS
- Schema frecventă de impersonare a băncilor (MAIB, Victoriabank, MICB)

## Echipa

| Nume |
|Bondarenco Alexandru|
|Isipchiuc Alexandr|

> Proiect realizat pentru **ONIA 2026** — Olimpiada Națională de Informatică și Aplicații.

## Licență

MIT License — liber pentru utilizare educațională și necomercială.
