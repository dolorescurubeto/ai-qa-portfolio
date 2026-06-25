# Week 1 — Practice notes

## 1. What does this script validate?

It checks that chatbot responses have the **correct amount** ($1,847.32) and **correct account type** (checking), compared against a reference answer. It does not care if the response "sounds good" — only concrete data.

## 2. Why does cand2 fail even though it sounds fine?

Because it says $1,800.32 instead of $1,847.32. The sentence is similar and mentions checking, but the **numeric value is wrong**. In banking that would be a serious error even if the wording is correct.

## 3. What is the difference between `text` and `note`?

- **`text`**: the response the script evaluates (defines PASS or FAIL).
- **`note`**: a comment for me; it is only printed and **does not change** the test result.

## 4. What does PASS mean for a banking chatbot?

The response has the **correct facts**: exact amount and correct account type. Sounding professional or similar to the reference is not enough.

## 5. What did I add this week?

- In `golden_scenarios.json`: **transfer_limit** scenario (daily limit $3,000).
- In `evaluate_factual.py`:
  - **cand5**: amount OK but missing "checking" → FAIL (incomplete response).
  - **cand6**: alternate wording with checking and correct amount → PASS.
- Final result: **3/6 PASS**.
