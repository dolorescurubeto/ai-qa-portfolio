# AI QA Portfolio — Dolores Curubeto

Practice portfolio for **AI Testing**, built after completing an AI-for-testers course.

You do not need a job working with AI to practice: here you simulate a fictional banking chatbot and evaluate it with Python scripts.

## What this repo includes

| Folder | What you practice | Difficulty |
|--------|-------------------|------------|
| `week01-baseline/` | Manual test cases + factual validation | Easy |
| `week02-golden-set/` | Golden set of prompts (JSON file) | Easy |
| `week03-metrics/` | BLEU, BERTScore, True Lies | Medium |
| `week04-drift/` | Regression over time | Medium |
| `week05-attention/` | BERT attention matrices + relevant tokens | Medium |
| `week06-llm-judge/` | LLM-as-judge with Ollama (local) | Medium |
| `tests/` | **pytest** automated suites (job prep Week 1) | Easy |
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

3. When you finish week 1, continue with week 2 in the same plan.
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

5. Week 5 (transformer attention):

```powershell
cd week05-attention
python attention_explorer.py --heatmap
```

See `week05-attention/README.md`.

6. Week 6 (LLM-as-judge with Ollama):

```powershell
cd week06-llm-judge
python llm_judge_ollama.py --dry-run --limit 3
python llm_judge_ollama.py --limit 3
```

See `week06-llm-judge/README.md` for Ollama install steps.

7. **Job prep** — 8-week plan toward RAG / enterprise AI QA roles:

```powershell
pip install pytest
pytest tests/ -v
```

See `PLAN-8-WEEKS-JOB-PREP.md` and `tests/README.md`.

## Previous course projects

If you already have exercises in `C:\Users\dell\ia-testers-practice`, this portfolio **organizes and extends** them. You do not need to delete anything.

## Portfolio goal

Demonstrate that you can:

- Design test cases for AI (not just "does it respond?")
- Validate **factual data** (amounts, account types)
- Measure **semantic similarity** (BERTScore, True Lies)
- Detect **drift** when a model degrades over time
- Explore **transformer attention** (interpretability)
- Use an **LLM-as-judge** (Ollama) and compare with factual checks
- Document results with reports

## For your resume

> Portfolio: QA evaluation suite for a fictional banking chatbot — golden prompt set, factual validation, semantic metrics (BERTScore/True Lies), drift testing, BERT attention analysis, LLM-as-judge (Ollama), and HTML reports. Python.
