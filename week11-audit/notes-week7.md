# Week 7 notes — Audit + lifecycle

## Why audit tests matter

Regulated industries (banking, health) require proof of **who did what, when, on which document**.

If `document_indexed` is missing from the log, you cannot prove the answer came from an approved source.

## Complete vs incomplete lifecycle

| Complete | Incomplete (bug) |
|----------|------------------|
| 5 events | Skip `index` → only 4 events |
| Traceable query → response | Cannot prove which index version was used |

## Link to Week 6

Ingestion changes the index. Audit log should show:

1. `document_ingested` version=2
2. Later `document_queried` returns v2 text

Week 8 go/no-go pack will combine: retrieval + grounding + calibration + audit completeness.

## Interview line

> "I validate document lifecycle traceability: every stage from upload to response emits an audit event, and pytest fails if any required action is missing."
