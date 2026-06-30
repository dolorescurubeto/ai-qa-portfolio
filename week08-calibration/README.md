# Week 4 — Confidence calibration + source weighting

## Confidence calibration

When a RAG system returns `confidence: 0.92`, it should be right ~92% of the time **in that confidence band**.

We bin samples and compare:

| Bin | Avg confidence | Actual accuracy | Gap |
|-----|----------------|-----------------|-----|
| 0.9-1.0 | 0.93 | 0.67 | 0.26 ← problem |

**ECE** (Expected Calibration Error) = weighted average gap. Lower is better.

Run analysis:

```powershell
cd C:\Users\dell\ai-qa-portfolio\week08-calibration
python -c "
import json, sys
from pathlib import Path
sys.path.insert(0, '.')
from calibration import calibration_report, expected_calibration_error, to_samples
root = Path('..')
records = json.load(open(root/'data/rag_confidence_samples.json'))
report = calibration_report(to_samples(records))
for r in report:
    print(r)
print('ECE:', expected_calibration_error(report))
"
```

## Source weighting

Not all documents are equal:

| Tier | weight | Example |
|------|--------|---------|
| official_policy | 1.0 | checking_balance_policy |
| retail_faq | 0.6 | shipping_policy |

Weighted retrieval: `final_score = raw_score × source_weight`

Official sources win when keyword scores are ambiguous.

## Tests

```powershell
pytest tests/test_calibration.py -v
```

## Checklist

- [ ] Run pytest — all green
- [ ] Print calibration table (script above)
- [ ] Read `notes-week4.md`
- [ ] Week 5: RBAC API mock
