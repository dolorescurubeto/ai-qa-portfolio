# RAG retrieval — hard cases (Priority 2)

Added **10 hard queries** to `data/rag_retrieval_golden.json` (`ret_008`–`ret_017`).

## Why these are harder

| Challenge | Example |
|-----------|---------|
| Amount in query | `1847.32 checking` — must not pick savings |
| Overlapping tokens | `checking` + `limit` vs balance chunk |
| Word order | Same intent, different phrasing than baseline |
| Cross-domain | `retail not banking` vs bank policies |
| Similar accounts | savings **balance** vs savings **minimum** |

## Regression

```powershell
pytest tests/test_rag_retrieval.py -m regression -v
```

- `test_retrieval_accuracy_baseline` → 17/17 Hit@1
- `test_hard_retrieval_cases_hit_at_1` → 10/10 hard only

## Exercise

Change one query to target the wrong chunk → pytest should fail → revert.
