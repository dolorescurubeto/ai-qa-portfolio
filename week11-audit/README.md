# Week 7 — Audit logging + document lifecycle

## Lifecycle under test

```
upload → ingest → index → query → response
  ↓        ↓       ↓       ↓        ↓
 audit   audit   audit   audit    audit
```

Each step **must** produce an audit event with:

- `event_id`
- `action`
- `user_id`
- `doc_id`
- `timestamp`

## Run tests

```powershell
pytest tests/test_audit_lifecycle.py -v
```

## JD mapping

> "Validate audit logging completeness and document lifecycle traceability"

`test_incomplete_lifecycle_detected_when_index_skipped` proves the harness catches **missing steps**.

## Checklist

- [ ] pytest green
- [ ] Read `notes-week7.md`
- [ ] Week 8: go/no-go pack
