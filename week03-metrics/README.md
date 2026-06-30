# Week 3 — Semantic metrics

## What changed from Week 2

| Week 2 | Week 3 |
|--------|--------|
| Factual validation only | Factual **+** semantic metrics |
| PASS/FAIL on facts | Compare facts vs BERTScore / True Lies |
| Console output | Console **+** HTML reports in `reports/` |

## Setup (one time)

If you already have the course venv at `ia-testers-practice`, you can reuse it:

```powershell
cd C:\Users\dell\ia-testers-practice
.\venv\Scripts\Activate.ps1
cd C:\Users\dell\ai-qa-portfolio\week03-metrics
```

Or create a venv in the portfolio:

```powershell
cd C:\Users\dell\ai-qa-portfolio
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On Windows, if True Lies shows encoding errors:

```powershell
$env:PYTHONUTF8=1
```

## Your tasks today (in order)

### Step 1 — Main comparison (factual vs BERTScore)

```powershell
cd C:\Users\dell\ai-qa-portfolio\week03-metrics
python compare_all.py
```

First run downloads the BERTScore model (~1 minute).

Look for **"Gap"** cases: semantic PASS but factual FAIL. Those are the dangerous ones.

### Step 2 — Open the HTML report

Open the newest file in `reports/week03_factual_vs_bertscore_*.html` in your browser.

Yellow rows = gap cases.

### Step 3 — True Lies report (checking_balance)

```powershell
python true_lies_report.py
```

Opens `reports/week03_true_lies_checking.html`.

### Step 4 — Hallucination vs factual check (True Lies)

```powershell
python hallucination_check.py
python hallucination_check.py --retail
```

Compares our factual validator with True Lies labels:
- **Factual accuracy issues** → wrong facts
- **Possible hallucination** → low semantic similarity (True Lies definition)

Reports: `reports/hallucination_check_banking.html` and `hallucination_check_retailco.html`

### Step 5 — Optional BLEU demo

```powershell
python bleu_ter_demo.py
```

Shows why word-overlap metrics alone are not enough.

## Week 3 deliverable

- [ ] Ran `compare_all.py`
- [ ] HTML report in `reports/`
- [ ] Found at least 1 gap case (semantic pass, factual fail)
- [ ] Notes written in `notes.md`

## Key lesson

> Semantic similarity measures **how similar it sounds**.
> Factual validation checks **whether the data is correct**.
> You need **both** for AI QA in production.
