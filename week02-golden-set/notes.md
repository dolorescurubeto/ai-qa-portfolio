# Week 2 — Practice notes

## 1. What changed from Week 1?

In Week 1, candidates lived **inside the script** (`evaluate_factual.py`). In Week 2, we moved them to **JSON files**:

- `data/golden_scenarios.json` → the correct answer (reference + facts)
- `data/candidates.json` → "model" responses to evaluate

The script `evaluate_from_json.py` only reads those files and evaluates everything. To add a new case, I edit JSON — not Python.

## 2. Why separate data and code?

In a real project, the QA team (or product) owns the golden set, not the developer. If there are 50 new scenarios tomorrow, I should not touch code each time — only JSON. That is closer to how production works.

## 3. What interesting cases did I find?

- **cand4 in `transfer_limit`**: says $3,200.00 instead of $3,000.00 → FAIL on amount, even though "checking" is correct.
- **cand5 in `checking_balance` and `savings_balance`**: correct amount but missing account type → FAIL (incomplete response).
- **cand4 in `checking_balance` and `savings_balance`**: alternate wording with the same data → PASS (the validator does not require an exact copy).

I learned that **sounding good is not enough**: you need the correct amount **and** an explicit account type.

## 4. What did I add this week?

- New scenario: **`minimum_balance_savings`** (minimum balance $100 in savings).
- **`transfer_limit`**: candidate `cand4` with wrong amount ($3,200).
- **`savings_balance`**: completed to 6 candidates (same as `checking_balance`).
- Ran `evaluate_from_json.py` several times to verify PASS/FAIL.

## 5. How many scenarios and candidates do I have?

| Scenario | Candidates | PASS |
|----------|------------|------|
| checking_balance | 6 | 3/6 |
| savings_balance | 6 | 3/6 |
| term_deposit_balance | 3 | 2/3 |
| transfer_limit | 4 | 2/4 |
| minimum_balance_savings | 4 | 2/4 |
| **Total** | **23** | **12/23 (52%)** |

Half fail on purpose — that is correct for a test golden set.

## 6. What is next in Week 3?

Add semantic metrics (BERTScore, True Lies) on the same candidates and compare: does any response pass semantic checks but fail factual validation? That shows why **both** test types are needed in AI QA.
