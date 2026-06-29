# Week 5 — Practice notes

## 1. What is self-attention?

Each token looks at every other token. The result is a **matrix**: one row per token (query), one column per token (key).

## 2. Course vs portfolio

| AutoAtencion.py | attention_explorer.py |
|-----------------|----------------------|
| Prints raw tensor | Shows **token names** |
| Last layer only | Top attention **pairs** |
| No interpretation | QA-oriented notes |

## 3. Special BERT tokens

- `[CLS]` — gathers sentence context
- `[SEP]` — separator
- `##ing`, `##ance` — subword pieces

## 4. Semantic filter (v2)

Raw attention is noisy — `[SEP]` and `.` dominate. The script now shows a **semantic** section that ignores:
- `[CLS]`, `[SEP]`
- punctuation (`.`, `,`, `$`)
- number fragments (`1`, `84`, `32`)

Look at **Banking-relevant links** for `checking` → `account` → `balance`.

## 5. Interview one-liner

> "I explored BERT attention matrices to see which tokens the model links — alongside factual validation in my portfolio."
