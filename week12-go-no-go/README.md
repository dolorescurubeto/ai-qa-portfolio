# Week 8 — Go/no-go decision pack

Final deliverable for the 8-week job prep plan.

## Generate report

```powershell
cd C:\Users\dell\ai-qa-portfolio\week12-go-no-go
python go_no_go_pack.py
```

Opens: `reports/go_no_go/go_no_go_YYYYMMDD_HHMMSS.html`

## What it includes

| Section | Source |
|---------|--------|
| Factual baseline | banking golden set 12/23 |
| RAG Hit@1 | retrieval golden |
| Citation + grounding | week 3 golden |
| Calibration ECE | week 4 (demo blocks GO) |
| RBAC / ingestion / audit | pytest suites |
| **Recommendation** | GO / NO-GO / GO-WITH-CONDITIONS |

## Tests

```powershell
pytest tests/test_go_no_go_pack.py -v
```

## Expected decision (demo data)

**NO-GO** — because ECE 0.258 > 0.25 (intentional overconfidence in sample data).

This is correct behaviour: the pack blocks release when calibration fails.

## 8-week plan complete

You now have evidence documentation for the job description:

- RAG validation harness
- Automated pytest suites
- Calibration regression
- RBAC tests
- Ingestion pipeline tests
- Audit lifecycle
- Go/no-go pack

## Interview line

> "I produce go/no-go packs that aggregate retrieval, grounding, calibration, RBAC, ingestion, and audit test evidence with an explicit release recommendation."
