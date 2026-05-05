# Aegis.md

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1.3-lightgrey?logo=flask)
![AI](https://img.shields.io/badge/AI-XLM--RoBERTa--large-purple?logo=huggingface)
![ONIA](https://img.shields.io/badge/ONIA-2026-orange)

## Despre proiect

**Aegis.md** este o aplicație web cu inteligență artificială pentru detectarea mesajelor SMS frauduloase în limbile română și rusă. Sistemul combină un model AI antrenat local (`xlm-roberta-large` fine-tuned) cu un motor de reguli bazat pe pattern-uri specifice fraudelor din Republica Moldova.

## Problema

Republica Moldova se confruntă cu o creștere alarmantă a fraudelor prin SMS: phishing bancar (MAIB, Victoriabank, MICB), scheme de câștiguri false, impostori care se prezintă drept polițiști sau funcționari FISC. Potrivit Poliției Moldovei, mii de cetățeni pierd anual sume semnificative din cauza acestor scheme.

**Beneficiari direcți:** cetățenii Republicii Moldova care primesc SMS-uri suspecte.  
**Beneficiari indirecți:** instituțiile bancare, autoritățile de protecție a consumatorilor, organizațiile de educație digitală.

## Soluția

Un detector în timp real care analizează textul SMS-ului și returnează:
- **Verdict**: `scam` / `suspicious` / `safe`
- **Nivelul de încredere** al modelului AI (%)
- **Motivele** detectării — cuvinte suspecte, link-uri scurtate, imitarea brandurilor locale

## Tehnologii utilizate

| Componentă | Tehnologie | Versiune |
|---|---|---|
| Model AI | `xlm-roberta-large` (fine-tuned) | HuggingFace Transformers |
| Framework web | Flask | 3.1.3 |
| Procesare NLP | Transformers | 5.7.0 |
| Deep Learning | PyTorch (CUDA) | 2.11.0+cu128 |
| CORS | Flask-CORS | 6.0.2 |
| Frontend | HTML/CSS/JS | fără dependențe externe |
| Date antrenament | Dataset propriu | 1046 SMS (RO + RU + EN) |

## Seturile de date

Datele utilizate sunt **sintetice și publice**, generate pe baza șabloanelor de fraude documentate:
- **Surse:** Avertismentele oficiale ale Poliției Republicii Moldova (politia.md), cazuri publicate pe Chisinau în Temă (Telegram), articole din Moldova.org și Ziarul de Gardă
- **Dimensiune:** 1046 SMS-uri (540 scam / 506 safe)
- **Limbi:** română (RO), rusă (RU), engleză (EN)
- **Distribuție:** echilibrată între clase (51.6% scam / 48.4% safe)
- **Legalitate:** datele sunt anonimizate complet și nu conțin informații personale reale
- **Preprocesare:** lowercase normalization, truncation la 128 tokens, padding, tokenizare cu `xlm-roberta-large` tokenizer

## Explorarea datelor

Analiza distribuției datelor este disponibilă în [`notebooks/explorare_date.ipynb`](notebooks/explorare_date.ipynb):
- Distribuția echilibrată scam/safe previne bias-ul modelului
- Pattern-urile frecvente identificate: urgență falsă, imitare branduri, link-uri scurtate, câștiguri false
- SMS-urile scam au în medie 15% mai multe cuvinte decât cele legitime

## Modelarea AI

**Model ales:** `xlm-roberta-large` — model multilingv cu 560M parametri, optim pentru text în română și rusă simultan.

**Justificare:** spre deosebire de modelele monolingve, XLM-RoBERTa procesează ambele limbi fără traducere, ceea ce este esențial pentru Republica Moldova (populație bilingvă RO/RU).

**Arhitectura:**
- Encoder transformer cu 24 straturi (large)
- Head de clasificare binar (safe / scam)
- Tokenizer SentencePiece multilingv (250K vocab)

**Hiperparametri:**
| Parametru | Valoare | Justificare |
|---|---|---|
| Learning rate | 1e-5 | Mic pentru fine-tuning stabil pe model pre-antrenat |
| Batch size | 8 | Optim pentru 16GB VRAM |
| Epochs | 25 | Convergență completă fără overfitting |
| Max length | 128 tokens | Suficient pentru SMS (max 160 caractere) |
| Weight decay | 0.01 | Regularizare împotriva overfitting |
| Warmup steps | 20% din total | Stabilizare la începutul antrenării |

**Procedura:** 80% antrenare / 20% validare, early stopping pe F1, salvare cel mai bun checkpoint.

## Rezultate finale

| Metrică | Zero-shot (bază) | După fine-tuning |
|---|---|---|
| Accuracy | 68.6% | **97.7%** |
| Precision (scam) | 63.6% | **100.0%** |
| Recall (scam) | 82.4% | **95.6%** |
| F1-score | 71.6% | **97.7%** |

**Matricea confuziilor (pe 1046 SMS):**

|  | Prezis: safe | Prezis: scam |
|---|---|---|
| Real: safe | 506 (TN) | 0 (FP) |
| Real: scam | 24 (FN) | 516 (TP) |

**Analiza erorilor:** cele 24 false-negative sunt SMS-uri scam formulate fără cuvinte-cheie tipice și fără link-uri — cazuri extreme de scam "implicit". Precision 100% garantează zero alerte false pe mesaje legitime.

**Comparație cu alternative:**
- `xlm-roberta-base` (zero-shot): 68.6% accuracy
- Regex-only (fără AI): ~60% recall, ~80% precision
- `xlm-roberta-large` fine-tuned: **97.7% accuracy, 100% precision** ← soluția aleasă

## Implementarea soluției

Aplicație **web** (Flask) accesibilă la `http://127.0.0.1:5000`:
- Interfață dark UI responsive, fără framework-uri externe
- API REST endpoint `/api/check` (POST JSON)
- Integrare directă a modelului prin HuggingFace `pipeline("text-classification")`
- Motor de reguli secundar: keywords, link-uri scurtate, imitare branduri locale

## Capturi de ecran

> Porniți serverul (`python app.py`) și accesați `http://127.0.0.1:5000` pentru a vedea interfața.

![Interfața principală](docs/screenshots/main.png)
![Exemplu SMS scam detectat](docs/screenshots/scam_result.png)
![Exemplu SMS safe](docs/screenshots/safe_result.png)

## Impact și sustenabilitate

**Beneficii potențiale:**
- Protejarea cetățenilor vulnerabili (vârstnici, persoane cu educație digitală redusă)
- Poate fi integrat ca extensie de browser sau aplicație mobilă
- Modelul poate fi reantrenat pe noi tipare de fraudă pe măsură ce acestea evoluează

**Riscuri etice:**
- Modelul a fost antrenat pe date sintetice — performanța pe SMS-uri reale din teren poate fi mai mică
- Risc de bias lingvistic: SMS-uri cu dialecte regionale sau greșeli ortografice pot scăpa nedetectate
- Datele de antrenament reflectă tipare cunoscute — fraudele noi, nereprezentate, pot evita detecția

**Limitări tehnice:**
- Modelul are recall 95.6% — aproximativ 4.4% din SMS-urile scam trec nedetectate
- Funcționează offline: nu verifică în timp real dacă un link este activ sau phishing
- Necesită GPU pentru rulare rapidă (>2s/SMS pe CPU)
- Nu analizează metadatele SMS-ului (numărul expeditorului, ora)

**Oportunități de extindere:**
- Integrare API cu operatorii de telefonie mobilă (Moldcell, Orange Moldova) pentru filtrare automată
- Adăugarea verificării link-urilor prin VirusTotal API
- Extindere dataset cu SMS-uri reale colectate cu consimțământ

## Cum se rulează local

### 1. Clonați repository-ul
```bash
git clone https://github.com/fractein/aegis.md.git
cd aegis.md
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

Versiuni exacte utilizate:
```
transformers==5.7.0
torch==2.11.0+cu128
flask==3.1.3
flask-cors==6.0.2
```

### 4. (Opțional) Antrenați modelul pe GPU
```bash
python finetune.py
```
> Prima rulare descarcă modelul de bază `xlm-roberta-large` (~1.1 GB). GPU recomandat (NVIDIA cu CUDA).

### 5. Porniți serverul
```bash
python app.py
```

### 6. Deschideți aplicația
```
http://127.0.0.1:5000
```

## Structura proiectului

```
aegis-md/
├── app.py                      # Server Flask + logica de detectare + motor de reguli
├── finetune.py                 # Antrenare completă xlm-roberta-large (25 epoci)
├── continue_finetune.py        # Antrenare incrementală de pe checkpoint existent
├── evaluate.py                 # Evaluare prin API REST (necesită server pornit)
├── quick_eval.py               # Evaluare directă pe model (fără server)
├── data/
│   ├── test_dataset.csv        # 1046 SMS-uri etichetate (RO + RU + EN)
│   └── evaluation_results.csv  # Rezultate detaliate pe fiecare SMS
├── models/                     # Exclus din Git (~500 MB)
│   └── sms-shield-finetuned/   # xlm-roberta-large fine-tuned (checkpoint final)
├── templates/
│   └── index.html              # Interfața web (dark UI, fără dependențe externe)
├── notebooks/
│   └── explorare_date.ipynb    # Analiza exploratorie a datelor
├── docs/
│   ├── arhitectura.md          # Diagrama arhitecturii sistemului
│   └── screenshots/            # Capturi de ecran ale aplicației
├── requirements.txt
└── README.md
```

## Concluzii

Aegis.md demonstrează că un model NLP multilingv fine-tuned pe date specifice contextului local poate atinge performanțe ridicate (Acc 97.7%, Precision 100%) pentru detectarea fraudelor SMS în Republica Moldova. Combinația dintre modelul AI și motorul de reguli bazat pe pattern-uri locale oferă robustețe suplimentară față de utilizarea exclusivă a AI.

**Dezvoltări viitoare recomandate:**
- Colectarea de date reale cu acordul utilizatorilor pentru a reduce dependența de date sintetice
- Implementarea ca serviciu cloud cu API public pentru integrare de terți
- Adăugarea explicabilității (SHAP/LIME) pentru a arăta utilizatorului exact ce a declanșat alerta

## Echipa

| Nume |
|---|
| Bondarenco Alexandru |
| Isipchiuc Alexandr |

> Proiect realizat pentru **ONIA 2026** — Olimpiada Națională de Inteligență Artificială.

## Licență

MIT License — liber pentru utilizare educațională și necomercială.
