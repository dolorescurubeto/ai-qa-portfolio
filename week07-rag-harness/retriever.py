"""
Simple RAG retriever — keyword overlap scoring (no external API).

Week 2 job prep: measure retrieval accuracy before answer generation.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CORPUS = ROOT / "data" / "rag_corpus" / "chunks.json"


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def load_corpus(path: Path = DEFAULT_CORPUS) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def score_chunk(query_tokens: set[str], chunk: dict) -> float:
    title_tokens = tokenize(chunk.get("title", ""))
    body_tokens = tokenize(
        " ".join([chunk.get("text", ""), chunk.get("doc_id", "").replace("_", " ")])
    )
    if not query_tokens:
        return 0.0
    title_hits = sum(1 for t in query_tokens if t in title_tokens)
    body_hits = sum(1 for t in query_tokens if t in body_tokens)
    # Title matches weighted higher — common simple RAG tuning lever
    return (title_hits * 2 + body_hits) / len(query_tokens)


def retrieve(query: str, corpus: list[dict], top_k: int = 3) -> list[dict]:
    """Return top-k chunks ranked by keyword overlap score."""
    query_tokens = set(tokenize(query))
    scored = []
    for chunk in corpus:
        scored.append(
            {
                **chunk,
                "score": round(score_chunk(query_tokens, chunk), 4),
            }
        )
    scored.sort(key=lambda c: c["score"], reverse=True)
    return scored[:top_k]


def retrieval_hit_at_k(query: str, expected_chunk_id: str, corpus: list[dict], k: int = 1) -> bool:
    results = retrieve(query, corpus, top_k=k)
    return any(r["chunk_id"] == expected_chunk_id for r in results)
