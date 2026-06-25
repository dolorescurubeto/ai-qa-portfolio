# Week 2 — Golden set from JSON

## What changed from Week 1

| Week 1 | Week 2 |
|--------|--------|
| Candidates inside the `.py` file | Candidates in `data/candidates.json` |
| One scenario (`checking`) | **All** scenarios from JSON |
| Edit Python to add cases | Edit JSON to add cases |

## Your task today (just this)

### Step 1 — Run the new script

```powershell
cd C:\Users\dell\ai-qa-portfolio\week02-golden-set
python evaluate_from_json.py
```

You should see **5 scenarios** evaluated and a **SUMMARY** at the end.

### Step 2 — Review the 2 JSON files

- `data/golden_scenarios.json` → what is correct (reference)
- `data/candidates.json` → simulated "model" responses to test

### Step 3 — Add 1 new candidate (practice)

1. Open `data/candidates.json`
2. In any scenario, add a new candidate (invent the text)
3. Save (**Ctrl + S**)
4. Run `python evaluate_from_json.py` again

Do not touch the `.py` file — only JSON.

## Optional task for the week

Add **1 new scenario** in `golden_scenarios.json` and its candidates in `candidates.json` (same key in both files).

## Week 2 goal

Reach **5–10 scenarios** in the golden set (at your own pace).
