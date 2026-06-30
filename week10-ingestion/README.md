# Week 6 — Incremental ingestion pipeline

## Flow under test

```
v1 full ingest     → 2 docs indexed
v2 incremental     → updated text (new amounts), same chunk_ids
v3 incremental     → remove transfer_limit_policy entirely
```

## Run tests

```powershell
pytest tests/test_ingestion_pipeline.py -v
```

## Demo script

```powershell
cd week10-ingestion
python -c "
from pathlib import Path
from ingestion_pipeline import full_ingest, apply_incremental_batch, get_chunk, CORPUS_ROOT
idx = full_ingest(CORPUS_ROOT/'v1')
print('v1:', get_chunk(idx,'chk_bal_01').text)
apply_incremental_batch(idx, CORPUS_ROOT/'v2')
print('v2:', get_chunk(idx,'chk_bal_01').text)
apply_incremental_batch(idx, CORPUS_ROOT/'v3')
print('v3 xfer gone:', get_chunk(idx,'xfer_01'))
"
```

## JD mapping

> "Build and maintain the incremental ingestion pipeline test suite"

You verify: update replaces stale chunks, removed docs disappear, ingest log is complete.

## Checklist

- [ ] pytest green
- [ ] Read `notes-week6.md`
- [ ] Week 7: audit + lifecycle
