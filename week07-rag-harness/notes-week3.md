# Week 3 notes — Citations + grounding

## Three layers of RAG QA (so far)

| Layer | Week | Question |
|-------|------|----------|
| Retrieval | 2 | Did we fetch the right chunk? |
| Citation | 3 | Does the answer point to that chunk? |
| Grounding | 3 | Is every fact in the answer supported by the chunk? |

All three can fail **independently**.

## Citation correctness

A citation is valid when:

1. `doc_id` + `chunk_id` exist in the corpus
2. The cited chunk was actually **retrieved** for this query

**Failure example (`cg_003`):** answer about shipping cites `ret_01` (returns) but retrieval returned `ship_01`.

In production, users click citations to verify sources — wrong citation = trust failure.

## Grounding

**Grounding** = the answer does not add facts beyond the source.

Our demo rule: every **$ amount** in the answer must appear in the retrieved chunk text.

| Case | Citation | Grounding | Why |
|------|----------|-----------|-----|
| cg_001 | PASS | PASS | Good response |
| cg_002 | PASS | FAIL | Cites shipping but says $8.99 (source: $5.99) |
| cg_003 | FAIL | PASS | Amount OK but wrong citation |
| cg_006 | FAIL | PASS | No citation at all |

This mirrors your banking portfolio: BERTScore can pass while factual validation fails.

## Connection to the job description

> "validation harness for RAG output quality: retrieval accuracy, citation correctness, and grounding"

You now have pytest coverage for all three on fictional data.

## Week 4 preview

Confidence scores: when the system says 95% sure, is it right 95% of the time?
