# Week 5 — Transformer attention (`week05-attention/`)

Extends the course file `AutoAtencion.py` from `ia-testers-practice`.

## What you learn

| Concept | Meaning |
|---------|---------|
| **Tokens** | How BERT splits text (`[CLS]`, words, `##` subwords, `[SEP]`) |
| **Attention matrix** | Who "looks at" whom — rows = query, cols = key |
| **Heads** | Multiple attention patterns; averaged here for readability |
| **Relevant tokens** | Pairs with the highest weights |

## Setup

Reuse the course venv:

```powershell
cd C:\Users\dell\ia-testers-practice
.\venv\Scripts\Activate.ps1
pip install matplotlib
cd C:\Users\dell\ai-qa-portfolio\week05-attention
```

## Run

```powershell
python attention_explorer.py
python attention_explorer.py --spanish
python attention_explorer.py --heatmap
```

Heatmap outputs:
- `reports/week05_attention_heatmap.png` — content words only (easier to read)
- `reports/week05_attention_heatmap_full.png` — all tokens

The script filters out `[CLS]`, `[SEP]`, punctuation, and number fragments so you see **semantic** links (e.g. `checking` → `account`).

## Link to course

| File | Location |
|------|----------|
| Original | `ia-testers-practice/AutoAtencion.py` |
| Extended | `week05-attention/attention_explorer.py` |

## Why this matters for AI QA

Attention shows **what the model focuses on** (interpretability). It does **not** replace factual validation — wrong answers can still look plausible in the attention map.
