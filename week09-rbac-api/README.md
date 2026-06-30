# Week 5 — RBAC + REST API testing

## Roles

| Role | Can access |
|------|------------|
| **analyst** | Balance, document summary (no $ amount) |
| **manager** | Balance, transfer limit, full document, audit logs |
| **auditor** | Audit logs, document metadata only |
| **guest** | Nothing (403) |

Tokens in `data/rbac_users.json`.

## Run API locally (optional)

```powershell
cd C:\Users\dell\ai-qa-portfolio\week09-rbac-api
pip install flask
python app.py
```

Then in another terminal:

```powershell
curl -H "Authorization: Bearer analyst-demo-token" http://127.0.0.1:5050/api/v1/account/balance
```

## Run pytest (recommended)

Uses Flask test client — same assertions as `requests` against a live server.

```powershell
cd C:\Users\dell\ai-qa-portfolio
pip install flask
pytest tests/test_rbac_api.py -v
```

## What you test (JD mapping)

- **RBAC enforcement** — 401 / 403 for wrong role
- **Role-specific filtered views** — same `/documents/{id}`, different JSON fields per role

## Checklist

- [ ] `pytest tests/test_rbac_api.py -v` all green
- [ ] Read `notes-week5.md`
- [ ] Week 6: ingestion pipeline
