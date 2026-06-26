# AI QA Portfolio — Dolores Curubeto

Practice portfolio for **AI Testing**, built after completing an AI-for-testers course.

Job working with AI to practice: here I simulate a fictional banking chatbot and evaluate it with Python scripts.

## What this repo includes

| Folder | What you practice | Difficulty |
|--------|-------------------|------------|
| `week01-baseline/` | Manual test cases + factual validation | Easy |
| `week02-golden-set/` | Golden set of prompts (JSON file) | Easy |
| `week03-metrics/` | BLEU, BERTScore, True Lies | Medium |
| `week04-drift/` | Regression over time | Medium |
| `data/` | Shared test data | — |
| `reports/` | Generated HTML reports | — |

## Setup (one time)

```powershell
cd C:\Users\dell\ai-qa-portfolio
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Where to start

1. Read `PLAN-4-WEEKS.md` (step-by-step plan).
2. Run the first exercise:

```powershell
cd week01-baseline
python evaluate_factual.py
```

3. When I finish week 1, continue with week 2 in the same plan.
4. Week 3 (semantic metrics):

```powershell
cd week03-metrics
python compare_all.py
```

See `week03-metrics/README.md` for full steps.

4. Week 4 (drift + GitHub):

```powershell
cd week04-drift
python drift_test.py --simulate-days 3
```

See `week04-drift/README.md` for GitHub push steps.

## Previous course projects

I already have exercises in `C:\Users\dell\ia-testers-practice`, this portfolio **organizes and extends** them. 

## Portfolio goal

Demonstrate that I can:

- Design test cases for AI (not just "does it respond?")
- Validate **factual data** (amounts, account types)
- Measure **semantic similarity** (BERTScore, True Lies)
- Detect **drift** when a model degrades over time
- Document results with reports

## For my resume (after completing all 4 weeks)

> Portfolio: QA evaluation suite for a fictional banking chatbot — golden prompt set, factual validation, semantic metrics (BERTScore/True Lies), drift testing, and HTML reports. Python, pytest, Playwright.
