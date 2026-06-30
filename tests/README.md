# pytest test suite — Week 1 (Job Prep)

Automated tests for the banking golden set. Maps to JD: **"Build automated test suites"**.

## Run

```powershell
cd C:\Users\dell\ai-qa-portfolio
.\venv\Scripts\Activate.ps1
pip install pytest
pytest tests/ -v
```

## Files

| File | Purpose |
|------|---------|
| `conftest.py` | Fixtures: scenarios, candidates, golden_set_rows |
| `test_factual_unit.py` | Unit tests for extractors + Week 1 cases |
| `test_golden_set_factual.py` | All 23 candidates + baseline regression |
| `test_expected_outcomes.py` | Documented PASS/FAIL with reasons (Jira-style) |

## Markers

```powershell
pytest tests/ -m regression -v    # baseline 12/23 only
pytest tests/ -m integration -v   # all parametrized rows
pytest tests/ -m "not slow" -v    # skip ML tests (none yet in week 1)
```

## Week 1 checklist

- [ ] `pytest tests/ -v` — all green
- [ ] Understand one `@pytest.mark.parametrize` example
- [ ] Read `test_expected_outcomes.py` — same idea as test cases in Jira
- [ ] Continue to Week 2 in `PLAN-8-WEEKS-JOB-PREP.md`
