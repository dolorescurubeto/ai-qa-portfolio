# Week 6 — Learning notes

## When to trust the judge vs the factual validator

| Situation | Trust |
|-----------|-------|
| Dollar amount or account type must be exact | **Factual validator** — deterministic, fast, auditable |
| Wording varies but facts are the same | **Judge** may be better at "same meaning, different words" |
| Production gate / compliance | **Factual validator** (or structured extraction), not judge alone |
| Exploratory QA / triage | **Judge** — good second opinion before human review |

**Rule of thumb:** use factual checks as the hard gate; use the LLM judge as an advisory layer or for cases regex cannot express (e.g. "does this answer the user's question?").

## Limitations

- **Judges hallucinate too.** The model can PASS a wrong amount or FAIL a correct paraphrase.
- **Non-deterministic.** Same input can get different verdicts across runs or models.
- **Slow and local.** Each candidate is an API call; not ideal for thousands of rows without batching.
- **Agreement is the metric.** High agreement with `validate_factual()` builds confidence; disagreements need human review — that is where the learning happens.

## What I observed

_(Fill in after your first live run: agreement rate, one disagreement example, whether judge caught something factual missed or vice versa.)_
