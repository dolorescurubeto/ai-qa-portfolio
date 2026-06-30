# Week 2 — RAG harness (job prep)

Week 2 of `PLAN-8-WEEKS-JOB-PREP.md`: **retrieval accuracy** for Simple RAG.

## What this is

Before testing if an LLM answer is correct, RAG systems must **retrieve the right source chunk**.

```
User query → Retriever → Top-k chunks → (later) LLM answer + citation
                ↑
         we test THIS first
```

## Files

| File | Role |
|------|------|
| `retriever.py` | Keyword retriever + `retrieval_hit_at_k` |
| `rag_mock.py` | Simple RAG: retrieve → templated answer |
| `data/rag_corpus/chunks.json` | Fictional policy chunks |
| `data/rag_retrieval_golden.json` | Queries + expected chunk |
| `tests/test_rag_retrieval.py` | pytest retrieval accuracy |

## Run retrieval demo

```powershell
cd C:\Users\dell\ai-qa-portfolio\week07-rag-harness
python -c "from retriever import load_corpus, retrieve; c=load_corpus(); print(retrieve('checking account balance', c))"
```

## Run tests

```powershell
cd C:\Users\dell\ai-qa-portfolio
pytest tests/test_rag_retrieval.py -v
```

## Week 3 — Citations + grounding

```powershell
pytest tests/test_rag_citations_grounding.py -v
```

See `week07-rag-harness/notes-week3.md`.

## Week 2 checklist

- [ ] Run `pytest tests/test_rag_retrieval.py -v` — all green
- [ ] Open `data/rag_retrieval_golden.json` — each row is a retrieval test case
- [ ] Try one wrong expected chunk in a copy — see test fail (learning exercise)
- [ ] Read `notes.md`
- [ ] Week 3: citations + grounding

## Job interview line

> "I built a RAG validation harness starting with retrieval Hit@1 on a golden query set before testing generation quality."
