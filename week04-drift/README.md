# Week 4 — Drift testing + GitHub

## What is drift?

A model can **degrade over time** — new versions, API changes, or fine-tuning can make previously correct answers wrong. Drift testing re-runs your golden set on a schedule and alerts you when pass rates drop.

## Step 1 — Run drift test (demo: 3 simulated days)

```powershell
cd C:\Users\dell\ai-qa-portfolio\week04-drift
python drift_test.py --simulate-days 3
```

This simulates 3 "days" with rising error rates (5% → 15% → 30%). You should see:

- Accuracy dropping each day
- `[DRIFT]` alert when the drop exceeds 10 points
- History appended to `drift_results.json`

### Single run (like a real scheduled job)

```powershell
python drift_test.py
python drift_test.py --error-rate 0.20
```

Run the same command on different days in production. For learning, `--simulate-days` is faster.

## Step 2 — Review history

Open `week04-drift/drift_results.json`. Each entry has:

- `timestamp`
- `error_rate_simulated`
- `accuracy`
- per-scenario `output` and `correct`

## Step 3 — Push to GitHub

### 3a. Initialize git (if not done yet)

```powershell
cd C:\Users\dell\ai-qa-portfolio
git init
git add .
git commit -m "AI QA portfolio: factual validation, semantic metrics, drift testing"
```

### 3b. Create repo on GitHub

1. Go to https://github.com/new
2. Name: `ai-qa-portfolio`
3. Public, no README (you already have one)
4. Create repository

### 3c. Push

```powershell
git remote add origin https://github.com/YOUR_USERNAME/ai-qa-portfolio.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub handle.

## Step 4 — Add to resume

Use the line from the main `README.md`:

> Portfolio: QA evaluation suite for a fictional banking chatbot — golden prompt set, factual validation, semantic metrics (BERTScore/True Lies), drift testing, and HTML reports. Python, pytest, Playwright.

## Week 4 deliverable

- [ ] Ran `drift_test.py --simulate-days 3`
- [ ] `drift_results.json` has 3+ entries
- [ ] Repo on GitHub (public)
- [ ] Resume line added

## In production (real job)

You would run `python drift_test.py` weekly via CI (GitHub Actions, Jenkins) and fail the pipeline if drift is detected — not simulate error rates, but call the real model API.
