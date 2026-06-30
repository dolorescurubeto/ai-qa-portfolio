"""
Week 4 — Source weighting in retrieval.

Official policy sources should rank above FAQ snippets when scores are close.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HARNESS = ROOT / "week07-rag-harness"
sys.path.insert(0, str(HARNESS))

from retriever import load_corpus, tokenize  # noqa: E402

WEIGHTS_FILE = ROOT / "data" / "rag_source_weights.json"
DEFAULT_MIN_GAP_TO_PREFER_LOWER_WEIGHT = 0.5


def load_source_weights(path: Path = WEIGHTS_FILE) -> dict[str, float]:
    with open(path, encoding="utf-8") as f:
        items = json.load(f)
    return {item["doc_id"]: item["weight"] for item in items}


def base_score(query: str, chunk: dict) -> float:
    query_tokens = set(tokenize(query))
    if not query_tokens:
        return 0.0
    title_tokens = tokenize(chunk.get("title", ""))
    body_tokens = tokenize(
        " ".join([chunk.get("text", ""), chunk.get("doc_id", "").replace("_", " ")])
    )
    title_hits = sum(1 for t in query_tokens if t in title_tokens)
    body_hits = sum(1 for t in query_tokens if t in body_tokens)
    return (title_hits * 2 + body_hits) / len(query_tokens)


def weighted_score(query: str, chunk: dict, weights: dict[str, float]) -> float:
    raw = base_score(query, chunk)
    weight = weights.get(chunk["doc_id"], 0.5)
    return round(raw * weight, 4)


def retrieve_weighted(
    query: str,
    corpus: list[dict] | None = None,
    weights: dict[str, float] | None = None,
    top_k: int = 3,
) -> list[dict]:
    if corpus is None:
        corpus = load_corpus()
    if weights is None:
        weights = load_source_weights()

    scored = []
    for chunk in corpus:
        raw = base_score(query, chunk)
        w = weights.get(chunk["doc_id"], 0.5)
        scored.append(
            {
                **chunk,
                "raw_score": round(raw, 4),
                "source_weight": w,
                "score": round(raw * w, 4),
            }
        )
    scored.sort(key=lambda c: c["score"], reverse=True)
    return scored[:top_k]
