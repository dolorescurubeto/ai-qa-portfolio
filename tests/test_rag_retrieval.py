"""Week 2 — RAG retrieval accuracy tests (Hit@1, Hit@3)."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
HARNESS = ROOT / "week07-rag-harness"
sys.path.insert(0, str(HARNESS))

from retriever import load_corpus, retrieval_hit_at_k, retrieve  # noqa: E402

GOLDEN_FILE = ROOT / "data" / "rag_retrieval_golden.json"
EXPECTED_HIT_AT_1 = 17  # 7 baseline + 10 hard
EXPECTED_HARD_CASES = 10


def _load_golden():
    with open(GOLDEN_FILE, encoding="utf-8") as f:
        return json.load(f)


_GOLDEN = _load_golden()
_CORPUS = load_corpus()


@pytest.fixture(scope="module")
def corpus():
    return _CORPUS


@pytest.fixture(scope="module")
def golden_queries():
    return _GOLDEN


@pytest.mark.parametrize("case", _GOLDEN, ids=[c["id"] for c in _GOLDEN])
def test_retrieval_hit_at_1(case, corpus):
    assert retrieval_hit_at_k(case["query"], case["expected_chunk_id"], corpus, k=1)


@pytest.mark.parametrize("case", _GOLDEN, ids=[c["id"] for c in _GOLDEN])
def test_retrieval_hit_at_3(case, corpus):
    assert retrieval_hit_at_k(case["query"], case["expected_chunk_id"], corpus, k=3)


@pytest.mark.regression
def test_retrieval_accuracy_baseline(golden_queries, corpus):
    hits = sum(
        1
        for case in golden_queries
        if retrieval_hit_at_k(case["query"], case["expected_chunk_id"], corpus, k=1)
    )
    assert len(golden_queries) == EXPECTED_HIT_AT_1
    assert hits == EXPECTED_HIT_AT_1


@pytest.mark.regression
def test_hard_retrieval_cases_hit_at_1(golden_queries, corpus):
    hard = [c for c in golden_queries if c.get("difficulty") == "hard"]
    hits = sum(
        1
        for case in hard
        if retrieval_hit_at_k(case["query"], case["expected_chunk_id"], corpus, k=1)
    )
    assert len(hard) == EXPECTED_HARD_CASES
    assert hits == EXPECTED_HARD_CASES


def test_top_result_has_positive_score(corpus):
    results = retrieve("checking account balance", corpus, top_k=1)
    assert results
    assert results[0]["score"] > 0
    assert results[0]["chunk_id"] == "chk_bal_01"
