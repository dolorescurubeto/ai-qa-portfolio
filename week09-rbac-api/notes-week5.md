# Week 5 notes — RBAC + REST API

## RBAC in one sentence

**Role-Based Access Control** = what you can see/do depends on **who you are**.

## Status codes under test

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Allowed | Analyst reads balance |
| 401 | No valid token | Missing Authorization header |
| 403 | Authenticated but not allowed | Auditor tries balance |

## Filtered views

Same endpoint, different payload:

```
GET /api/v1/documents/doc_checking_001

analyst  → title, summary (no balance)
manager  → everything including balance + risk flag
auditor  → doc_id, title, audit_trail_id only
```

This is common in enterprise doc/RAG portals.

## Flask test client vs requests

- **pytest + Flask test client** — fast, no server needed (what we use)
- **requests + live server** — same tests, closer to production

In interviews both count as REST API testing.

## Interview line

> "I automated RBAC regression with pytest: verify 403 for unauthorized roles and assert role-specific field filtering on document endpoints."
