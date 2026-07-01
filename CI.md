# CI — GitHub Actions

Automated regression on every push to `main`.

## Workflow

File: `.github/workflows/pytest.yml`

| Step | What |
|------|------|
| Checkout | Clone repo |
| Python 3.12 | Same as local |
| `pip install -r requirements-ci.txt` | pytest + flask only (fast, no torch) |
| `pytest tests/ -v` | Full job-prep + adversarial suite |
| `go_no_go_pack.py` | Generate decision pack artifact |

## Why `requirements-ci.txt`?

Full `requirements.txt` includes `torch` and `bert-score` for week03 scripts run locally. CI only needs the **pytest harness** — keeps runs under ~1 minute.

## Badge (add to README after first green run)

```markdown
![AI QA Tests](https://github.com/dolorescurubeto/ai-qa-portfolio/actions/workflows/pytest.yml/badge.svg)
```

## Local equivalent

```powershell
pip install -r requirements-ci.txt
pytest tests/ -v
```

## Interview line

> "Regression is automated in GitHub Actions — every push runs 160+ pytest cases across RAG, RBAC, ingestion, audit, adversarial, and go/no-go evidence."
