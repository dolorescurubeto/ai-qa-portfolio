# 4-Week Plan — AI QA Portfolio

**Suggested time:** 2–3 hours per week.  
**Golden rule:** do not skip weeks. Each one builds on the previous.

---

## Week 1 — Foundation: test cases + factual validation

**Goal:** understand that testing AI means verifying concrete data, not just "sounds good".

### Tasks (in order)

1. [ ] Open `week01-baseline/evaluate_factual.py` and read it (~60 lines).
2. [ ] Run: `python evaluate_factual.py`
3. [ ] Open `data/golden_scenarios.json` and read the scenarios.
4. [ ] Add **1 new scenario** in the JSON (invent a balance and account type).
5. [ ] Add **2 candidate responses** in the script (one correct, one incorrect).
6. [ ] Run again and observe PASS vs FAIL.
7. [ ] Write in `week01-baseline/notes.md`: what you learned in 5 lines.

### What you do NOT need this week

- OpenAI API
- Ollama
- BERTScore
- GitHub (you can push in week 4)

### Week 1 deliverable

- Script running with at least 4 scenarios evaluated.
- You understand the difference between "similar" and "correct".

---

## Week 2 — Golden set of prompts

**Goal:** have a fixed file of questions/expected answers (like in production).

### Tasks

1. [ ] Copy `data/golden_scenarios.json` to `data/golden_scenarios_v2.json`.
2. [ ] Reach **10 scenarios** (checking, savings, term deposit, transfers, etc.).
3. [ ] For each scenario, define:
   - `reference` (ideal response)
   - `facts` (amount, account type)
4. [ ] Modify `evaluate_factual.py` to read from JSON (or use `evaluate_from_json.py`).
5. [ ] Run evaluation across all scenarios.

### Week 2 deliverable

- JSON file with documented test cases.
- One command that evaluates everything.

---

## Week 3 — Semantic metrics

**Goal:** add BLEU / BERTScore / True Lies on top of factual checks.

### Tasks

1. [ ] Install: `pip install bert-score true-lies-validator nltk`
2. [ ] Copy your course scripts (`BleuYTer.py`, `PruebasFuncionalesIA.py`, `TrueLiesEjemplo.py`) to `week03-metrics/`.
3. [ ] Run True Lies on the same candidates from week 1.
4. [ ] Compare: does any response pass semantic checks but fail factual validation?
5. [ ] Save an HTML report in `reports/`.

### Week 3 deliverable

- At least 1 HTML report in `reports/`.
- Comparative table: factual vs semantic (in notes or README).

---

## Week 4 — Drift + portfolio on GitHub

**Goal:** show that a model can degrade over time and publish your work.

### Tasks

1. [ ] Copy `LongTermDriftTesting.py` to `week04-drift/` and adapt it to your golden set.
2. [ ] Run the drift test **3 times on different days** (or simulate by changing the error rate).
3. [ ] (Optional) Install Ollama and connect a local model — only if you want to go further.
4. [ ] Create a GitHub repo: `ai-qa-portfolio`.
5. [ ] Push the project with an updated README.
6. [ ] Add the main README line to your resume.

### Week 4 deliverable

- Public GitHub repo.
- Drift history in `drift_results.json`.
- README with screenshots or sample output.

---

## If you get stuck

| Problem | Solution |
|---------|----------|
| I do not understand the code | Ask: "explain evaluate_factual.py line by line" |
| Python error | Copy the full error and paste it in chat |
| No API key | Weeks 1–2 do not need one |
| True Lies emoji error | Run with `$env:PYTHONUTF8=1` before the script |
| Feeling overwhelmed | Do **only one task per session** (1 checkbox) |

---

## Final portfolio checklist

- [ ] 10+ scenarios in golden set
- [ ] Automated factual validation
- [ ] At least 1 semantic metric (BERTScore or True Lies)
- [ ] Drift test with history
- [ ] README on GitHub
- [ ] 1 sample HTML report in `reports/`

When you have all 6 checks, you have a solid portfolio for junior QA / AI QA roles.
