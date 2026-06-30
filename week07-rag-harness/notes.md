# Week 2 notes — Retrieval accuracy

## Why test retrieval first?

A RAG answer can only be grounded if the **right document chunk** was retrieved. Testing only the final answer misses failures where:

- Wrong chunk retrieved → right-sounding wrong answer
- No chunk retrieved → model hallucinates from parametric memory

## Metrics used this week

| Metric | Meaning |
|--------|---------|
| **Hit@1** | Expected chunk is rank #1 |
| **Hit@3** | Expected chunk appears in top 3 |
| **Retrieval accuracy** | % of golden queries with Hit@1 |

## Simple vs keyword retriever

This week uses **keyword overlap** (no embeddings) so tests run fast without GPU. In production you might use vector search (OpenSearch, Pinecone, Bedrock KB). The **test pattern is the same**: golden queries + expected `chunk_id`.

## Connection to your banking portfolio

| Banking golden set | RAG retrieval golden |
|--------------------|----------------------|
| `golden_scenarios.json` | `rag_retrieval_golden.json` |
| Expected facts in answer | Expected chunk in top-k |
| Factual PASS/FAIL | Hit@1 true/false |

Week 3 adds: citation correctness + answer grounded in retrieved text only.
