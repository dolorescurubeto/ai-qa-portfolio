# Week 3 — Practice notes

## 1. What did Week 3 add?

On top of factual validation (Week 2), I added **semantic metrics**:

- **BERTScore** — measures how similar the wording is to the reference
- **True Lies** — combines factual extraction + semantic similarity
- **BLEU / TER** — word-overlap metrics (demo)

## 2. What is a "gap" case?

A **gap** = semantic PASS but factual FAIL.

Example from `checking_balance` cand2:

- Text: "The balance in your checking account is **$1,800.32**."
- BERTScore F1: **0.97** (looks very similar)
- Factual: **FAIL** (wrong amount)

The chatbot sounds right but gives wrong banking data. That is dangerous.

## 3. Main results (compare_all.py)

| Metric | Result |
|--------|--------|
| Candidates evaluated | 23 |
| Factual PASS | 12/23 |
| Semantic PASS (F1 >= 0.85) | 23/23 |
| **Gap cases** | **11/23** |

Almost every factual failure still passes BERTScore at 0.85. Semantic metrics alone are **not enough** for banking.

## 4. Gap examples I found

| Scenario | ID | Why factual fails | BERTScore F1 |
|----------|-----|-------------------|--------------|
| checking_balance | cand2 | Wrong amount | 0.97 |
| checking_balance | cand3 | Wrong account (savings) | 0.99 |
| checking_balance | cand5 | Missing "checking" | 0.97 |
| transfer_limit | cand4 | Wrong amount ($3,200) | 0.95 |

## 5. What reports did I generate?

- `reports/week03_factual_vs_bertscore_*.html` — full comparison table (yellow rows = gaps)
- `reports/week03_true_lies_checking.html` — True Lies on checking_balance

## 6. Key takeaway for interviews

> "I use semantic metrics (BERTScore, True Lies) to catch paraphrases and wording changes, but I always pair them with factual validation for domain-critical fields like amounts and account types. In my portfolio, 11 of 23 candidates passed BERTScore but failed factual checks."

## 7. What is next in Week 4?

Drift testing — run the same golden set over time and track if pass rates drop when the model changes.
