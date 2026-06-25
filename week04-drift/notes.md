# Week 4 — Practice notes

## 1. What is drift testing?

**Drift** = the model gets worse over time. Maybe a new version was deployed, fine-tuning changed behavior, or the API provider updated silently.

Drift testing means running the **same golden set** periodically and comparing pass rates. If accuracy drops beyond a threshold, you alert the team.

## 2. How does my script simulate it?

`drift_test.py` simulates a banking chatbot with a configurable **error rate**:

- Low error rate → model usually picks a correct response
- High error rate → model often picks a failing candidate from the golden set

Each run is saved to `drift_results.json` with a timestamp.

## 3. Demo command (3 simulated days)

```powershell
python drift_test.py --simulate-days 3
```

Runs with error rates 5% → 15% → 30%. You should see accuracy drop and a `[DRIFT]` alert after day 2 or 3.

## 4. What to put on GitHub

- Full repo with `README.md`, all 4 weeks, `data/`, sample HTML in `reports/`
- `week04-drift/drift_results.json` showing drift history
- Optional: screenshot of HTML report + drift console output

## 5. Resume line (English)

> Built an AI QA evaluation suite for a fictional banking chatbot: golden prompt set (23 cases), factual validation, BERTScore/True Lies semantic metrics, drift monitoring, and HTML reports. Python.

## 6. Portfolio checklist

- [x] 5 scenarios, 23 candidates in golden set
- [x] Automated factual validation
- [x] Semantic metrics (BERTScore + True Lies)
- [x] Drift test with history
- [ ] Public GitHub repo
- [x] HTML report in `reports/`
