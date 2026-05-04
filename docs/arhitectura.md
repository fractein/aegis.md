# Arhitectura Aegis.md

## Fluxul de analiză

```
SMS introdus de utilizator
         │
         ▼
┌─────────────────────────┐
│   Motor de reguli       │  ← SUSPICIOUS_KEYWORDS, HIGH_RISK_KEYWORDS,
│   (find_reasons)        │    SHORT_LINK_DOMAINS, LOCAL_BRANDS
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Model AI              │  ← xlm-roberta-base fine-tuned
│   (text-classification) │    antrenat pe 120+ SMS moldovenești
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Logică de decizie     │  scam / suspicious / safe
└─────────────────────────┘
         │
         ▼
    Răspuns JSON → Interfață web
```

## Componente

| Fișier | Rol |
|---|---|
| `src/app.py` | Server Flask, API `/api/check`, `/api/health` |
| `src/finetune.py` | Antrenarea modelului xlm-roberta-base pe GPU |
| `src/evaluate.py` | Evaluarea preciziei modelului (accuracy, precision, recall, F1) |
| `src/templates/index.html` | Interfața web (HTML/CSS/JS, fără dependențe externe) |
| `data/test_dataset.csv` | Dataset: 120+ SMS etichetate (scam/safe, RO/RU) |
| `models/aegis-finetuned/` | Modelul antrenat local (exclus din Git — ~2 GB) |

## Stack tehnic

- **Python 3.13** + **Flask 3.1**
- **Transformers 5.7** (Hugging Face) + **PyTorch 2.11 CUDA**
- **GPU**: NVIDIA RTX 5070 Ti (16 GB VRAM)
- **Model de bază**: `xlm-roberta-base` (multilingual, 270M parametri)
- **Antrenament**: 60 epoci, batch_size=8, lr=2e-5, ~15 minute
