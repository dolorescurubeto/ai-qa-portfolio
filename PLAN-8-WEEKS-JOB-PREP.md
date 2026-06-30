# 8-Week Job Prep Plan — RAG / Enterprise AI QA

Target role skills: RAG validation harness, pytest suites, calibration, RBAC, audit logs, ingestion pipeline, go/no-go packs.

| Week | Focus | Folder / artifact | Status |
|------|--------|-----------------|--------|
| 1 | **pytest** on existing portfolio | `tests/`, `pytest.ini` | Done |
| 2 | RAG mock + retrieval accuracy | `week07-rag-harness/` | Done |
| 3 | Citation + grounding tests | `week07-rag-harness/` | Done |
| 4 | Confidence calibration + source weighting | `week08-calibration/` | Done |
| 5 | RBAC API mock + pytest | `week09-rbac-api/` | Done |
| 6 | Incremental ingestion pipeline | `week10-ingestion/` | Done |
| 7 | Audit logging + document lifecycle | `week11-audit/` | Done |
| 8 | Go/no-go decision pack | `week12-go-no-go/`, `reports/go_no_go/` | Done |

## Week 1 — pytest (this week)

**Goal:** Turn portfolio validations into an automated **pytest** suite (JD: "Build automated test suites").

### Tasks

- [ ] Install pytest: `pip install pytest`
- [ ] Run fast tests: `pytest tests/ -m "not slow"`
- [ ] Run full suite: `pytest tests/`
- [ ] Read `tests/README.md`
- [ ] Optional: run with report `pytest tests/ --html=reports/pytest_report.html` (needs pytest-html)

### What you learn

- `@pytest.mark.parametrize` — one test, many candidates
- Fixtures (`conftest.py`) — shared data loading
- Regression baseline — lock expected PASS counts so drift in *tests* is caught
- How this maps to CI/CD and Jira test cases in a real job

### Commands

```powershell
cd C:\Users\dell\ai-qa-portfolio
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest tests/ -v
pytest tests/ -m "not slow" -v
```

When Week 1 is done, continue to Week 2 in this file.

---

## Week 2 — RAG mock + retrieval accuracy

**Goal:** Test that the retriever returns the **correct chunk** before testing answers.

### Commands

```powershell
pytest tests/test_rag_retrieval.py -v
```

---

## Week 3 — Citations + grounding (current)

**Goal:** Validate that answers **cite the right chunk** and **do not hallucinate facts** beyond the source.

### Tasks

- [ ] Read `week07-rag-harness/notes-week3.md`
- [ ] Open `data/rag_citation_grounding_golden.json` — 6 cases (pass/fail mix)
- [ ] Run `pytest tests/test_rag_citations_grounding.py -v`
- [ ] Compare `cg_002` (bad amount) with your banking cand2 (wrong amount)

### Commands

```powershell
pytest tests/test_rag_citations_grounding.py -v
pytest tests/ -v
```

### Files

| File | Role |
|------|------|
| `grounding.py` | `validate_citations`, `validate_grounding` |
| `rag_citation_grounding_golden.json` | Test cases with expected pass/fail |
| `test_rag_citations_grounding.py` | pytest suite |

---

## Week 4 — Confidence calibration + source weighting

**Goal:** Detect **overconfident** wrong answers and verify **official sources** rank above FAQ.

### Commands

```powershell
pytest tests/test_calibration.py -v
```

---

## Week 5 — RBAC + REST API

**Goal:** Test **401/403** enforcement and **role-filtered** document views.

### Commands

```powershell
pytest tests/test_rbac_api.py -v
```

---

## Week 6 — Incremental ingestion (current)

**Goal:** Updates replace stale chunks; removed docs disappear from index.

### Tasks

- [ ] `pytest tests/test_ingestion_pipeline.py -v`
- [ ] Demo script in `week10-ingestion/README.md`
- [ ] Read `notes-week6.md`

### Commands

```powershell
pytest tests/test_ingestion_pipeline.py -v
pytest tests/ -v
```

---

## Week 3 (old outline)

- Answer must cite `doc_id` + chunk
- Tests: citation points to real chunk; answer facts appear in retrieved context only

---

## Week 4 — Confidence calibration

- Candidates carry `confidence` score
- Plot / assert calibration bins (e.g. 0.9+ bucket should have ~90% accuracy)

---

## Week 5 — RBAC + REST API

- FastAPI or Flask mock with roles
- pytest + `requests`: 403 for wrong role, filtered fields per role

---

## Week 6 — Incremental ingestion

- v1 doc indexed → v2 update → re-index
- Tests: answers use new content; stale chunks removed

---

## Week 7 — Audit + lifecycle

- Log chain: upload → ingest → index → query → response
- Tests: every step has audit event with `doc_id`, `user_id`, `timestamp`

---

## Week 8 — Go/no-go pack

- Single HTML/Markdown report: accuracy by category, regression vs baseline, risks, recommendation
