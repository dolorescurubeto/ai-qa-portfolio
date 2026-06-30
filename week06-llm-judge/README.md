# Week 6 — LLM-as-judge (Ollama)

## What is LLM-as-judge?

After your earlier layers:

| Layer | Tool | What it checks |
|-------|------|----------------|
| 1 | Manual test cases | Does the bot respond? |
| 2 | Golden set (JSON) | Structured scenarios + references |
| 3 | Factual validator (`factual.py`) | Regex on amounts, account types |
| 3b | Semantic metrics (BERTScore, True Lies) | Wording similarity |
| **4** | **LLM judge (this week)** | Model reads reference + candidate and decides PASS/FAIL |

An LLM judge can catch nuanced factual errors that regex misses, but it can also hallucinate or disagree with your deterministic checks. This week you **compare** judge vs factual validator and look at agreement.

## Prerequisites

- Python 3.10+ (portfolio venv is fine — no new pip packages)
- [Ollama](https://ollama.com/download) installed and running locally

### Install Ollama on Windows

1. Download from https://ollama.com/download
2. Run the installer (Ollama starts in the system tray)
3. Open PowerShell and pull the default model:

```powershell
ollama pull llama3.2
```

Verify:

```powershell
ollama list
```

## Usage

```powershell
cd C:\Users\dell\ai-qa-portfolio\week06-llm-judge
```

### Step 1 — Dry run (no Ollama needed)

Prints judge prompts and runs factual validation only:

```powershell
python llm_judge_ollama.py --dry-run --limit 3
```

### Step 2 — Real run (Ollama required)

Start with a small batch:

```powershell
python llm_judge_ollama.py --limit 3
```

Then run all banking candidates:

```powershell
python llm_judge_ollama.py --all
```

### Optional flags

| Flag | Description |
|------|-------------|
| `--dry-run` | Print prompts, skip API calls |
| `--limit N` | First N candidates (default: 5) |
| `--all` | All candidates |
| `--model NAME` | Ollama model (default: `llama3.2`) |
| `--retail` | Use `retailco-day1-practice` data |

Retail example:

```powershell
python llm_judge_ollama.py --retail --limit 3
```

## Output

- **Console:** factual PASS count, judge PASS count, agreement rate
- **HTML:** `reports/llm_judge_banking.html` (or `llm_judge_retailco.html`)

Green rows = factual and judge agree. Yellow = factual PASS but judge FAIL (review these).

## Week 6 deliverable

- [ ] Ran `--dry-run --limit 3`
- [ ] Installed Ollama and pulled `llama3.2`
- [ ] Ran with `--limit 3` against live Ollama
- [ ] Opened HTML report and noted any disagreements
- [ ] Read `notes.md`
