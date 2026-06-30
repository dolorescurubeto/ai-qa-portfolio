# Week 4 notes

## Why calibration matters for go/no-go

A system that says **95% confident** but is only right **67%** of the time is dangerous for release. Calibration testing catches **overconfidence** before production.

## Regression use

Re-run calibration after:

- Model upgrade
- Prompt change
- Corpus update

If ECE rises above threshold → **no-go** or more SME review.

## Source weighting vs retrieval accuracy

| Week 2 | Week 4 |
|--------|--------|
| Is the chunk factually relevant? | Should official policy beat FAQ when both match? |

Example: query about "account balance requirement" could hit savings FAQ or minimum balance policy. Weighting ensures **official_policy** wins.

## Interview line

> "I automate regression on confidence calibration bins and verify source-weighting rules so high-trust documents rank above FAQ content in retrieval."

## Connection to JD

> "Automate regression testing for confidence score calibration and source weighting behaviour"

You now have pytest coverage for both.
