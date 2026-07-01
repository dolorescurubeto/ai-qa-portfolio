# Priority 4 — E2E Playwright + factual validation

## Setup (one time)

```powershell
cd C:\Users\dell\ai-qa-portfolio
pip install -r requirements-e2e.txt
playwright install chromium
```

If `playwright install` fails (SSL/Avast), run API-only tests (no browser):

```powershell
pytest tests/test_e2e_banking_chat.py -m integration -v
```

## Run E2E tests (browser)

```powershell
pytest tests/test_e2e_banking_chat.py -m e2e -v
```

Starts `chat_app.py` automatically, opens Chromium, sends messages, validates with `factual.py`.

## Run chat manually

```powershell
cd week14-e2e-chat
python chat_app.py
```

Open http://127.0.0.1:5051

## Flow under test

```
Browser (Playwright) → chat UI → bot response text → validate_factual() in Python
```

## CI note

E2E tests are marked `@pytest.mark.e2e` and **excluded from GitHub Actions** (need browser). Run locally before release.

## Interview line

> "I automate UI chat flows with Playwright and pipe responses into the same factual validation harness used for offline golden-set regression."
