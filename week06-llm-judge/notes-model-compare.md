# Priority 3 — Compare two Ollama models

## Setup

```powershell
ollama pull llama3.2
ollama pull mistral
```

## Run

```powershell
cd C:\Users\dell\ai-qa-portfolio\week06-llm-judge
python compare_models.py --dry-run --limit 3
python compare_models.py --limit 5
python compare_models.py --model-a llama3.2 --model-b mistral --limit 5
```

## What you learn

| Metric | Meaning |
|--------|---------|
| Judge PASS A vs B | Which model is stricter/looser |
| Agreement with factual | Which model matches regex checks |
| Models disagree | Cases needing **human** SME review |

## Reports

`reports/ollama_compare_llama3.2_vs_mistral.html`  
`reports/ollama_compare_llama3.2_vs_mistral.json`

## Interview line

> "I regression-compare multiple local judge models on the same golden set and flag disagreement cases for human review before release."

## pytest

```powershell
pytest tests/test_ollama_model_compare.py -v
```
