"""Week 3 — Citation correctness and grounding validation tests."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
HARNESS = ROOT / "week07-rag-harness"
sys.path.insert(0, str(HARNESS))

from grounding import validate_citations, validate_grounding, validate_rag_response  # noqa: E402
from retriever import load_corpus  # noqa: E402
from rag_mock import simple_rag_answer  # noqa: E402

GOLDEN_FILE = ROOT / "data" / "rag_citation_grounding_golden.json"
_CORPUS = load_corpus()


def _load_golden():
    with open(GOLDEN_FILE, encoding="utf-8") as f:
        return json.load(f)


def _chunks_by_id(chunk_ids: list[str]) -> list[dict]:
    lookup = {c["chunk_id"]: c for c in _CORPUS}
    return [lookup[cid] for cid in chunk_ids if cid in lookup]


_GOLDEN = _load_golden()


@pytest.mark.parametrize("case", _GOLDEN, ids=[c["id"] for c in _GOLDEN])
def test_citation_validation(case):
    retrieved = _chunks_by_id(case["retrieved_chunks"])
    result = validate_citations(case["citations"], retrieved, _CORPUS)
    assert result["pass"] is case["expected_citation_pass"], case.get("note", "")


@pytest.mark.parametrize("case", _GOLDEN, ids=[c["id"] for c in _GOLDEN])
def test_grounding_validation(case):
    retrieved = _chunks_by_id(case["retrieved_chunks"])
    source = retrieved[0]["text"] if retrieved else ""
    result = validate_grounding(case["answer"], source)
    assert result["pass"] is case["expected_grounding_pass"], case.get("note", "")


@pytest.mark.parametrize("case", _GOLDEN, ids=[c["id"] for c in _GOLDEN])
def test_full_rag_response_validation(case):
    retrieved = _chunks_by_id(case["retrieved_chunks"])
    result = validate_rag_response(
        case["answer"], case["citations"], retrieved, _CORPUS
    )
    expected = case["expected_citation_pass"] and case["expected_grounding_pass"]
    assert result["pass"] is expected, case.get("note", "")


@pytest.mark.integration
def test_simple_rag_mock_has_valid_citation_and_grounding():
    """End-to-end: mock RAG output should cite retrieved chunk and stay grounded."""
    response = simple_rag_answer("checking account balance demo", _CORPUS)
    result = validate_rag_response(
        response["answer"],
        response["citations"],
        response["retrieved_chunks"],
        _CORPUS,
    )
    assert result["citation"]["pass"]
    assert result["grounding"]["pass"]


@pytest.mark.regression
def test_grounding_golden_baseline_counts():
    citation_pass = sum(1 for c in _GOLDEN if c["expected_citation_pass"])
    grounding_pass = sum(1 for c in _GOLDEN if c["expected_grounding_pass"])
    full_pass = sum(
        1 for c in _GOLDEN if c["expected_citation_pass"] and c["expected_grounding_pass"]
    )
    assert len(_GOLDEN) == 6
    assert citation_pass == 4
    assert grounding_pass == 4
    assert full_pass == 2
