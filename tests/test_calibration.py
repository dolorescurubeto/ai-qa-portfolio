"""Week 4 — Confidence calibration and source weighting tests."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CALIB = ROOT / "week08-calibration"
HARNESS = ROOT / "week07-rag-harness"
sys.path.insert(0, str(CALIB))
sys.path.insert(0, str(HARNESS))

from calibration import (  # noqa: E402
    calibration_report,
    expected_calibration_error,
    high_confidence_miscalibration,
    sample_pass,
    to_samples,
)
from retriever import load_corpus, retrieve  # noqa: E402
from source_weighting import load_source_weights, retrieve_weighted  # noqa: E402

CONFIDENCE_FILE = ROOT / "data" / "rag_confidence_samples.json"
MAX_ECE = 0.25  # go/no-go threshold in production
EXPECTED_ECE = 0.258  # locked baseline — intentionally miscalibrated demo data


def _load_confidence_records():
    with open(CONFIDENCE_FILE, encoding="utf-8") as f:
        return json.load(f)


_RECORDS = _load_confidence_records()
_SAMPLES = to_samples(_RECORDS)
_REPORT = calibration_report(_SAMPLES)


def test_confidence_samples_loaded():
    assert len(_RECORDS) == 12


def test_sample_pass_requires_citation_and_grounding():
    assert sample_pass(_RECORDS[0]) is True
    assert sample_pass(_RECORDS[3]) is False  # conf_004 grounding fail


def test_calibration_report_has_four_bins():
    assert len(_REPORT) == 4
    assert sum(r["count"] for r in _REPORT) == 12


@pytest.mark.regression
def test_expected_calibration_error_baseline():
    """Demo data is intentionally miscalibrated — ECE above go/no-go threshold."""
    ece = expected_calibration_error(_REPORT)
    assert ece == EXPECTED_ECE
    assert ece > MAX_ECE, "Harness should flag overconfidence for go/no-go"


def test_high_confidence_bin_has_miscalibration_flag():
    """0.9-1.0 bin: high confidence but not all answers pass (realistic drift signal)."""
    issues = high_confidence_miscalibration(_REPORT, threshold=0.9)
    assert issues, "Expected miscalibration in high-confidence bin for demo dataset"


@pytest.mark.parametrize("record", _RECORDS, ids=[r["id"] for r in _RECORDS])
def test_confidence_in_valid_range(record):
    assert 0.0 <= record["confidence"] <= 1.0


def test_source_weights_official_higher_than_faq():
    weights = load_source_weights()
    assert weights["checking_balance_policy"] > weights["shipping_policy"]
    assert weights["returns_policy"] == weights["shipping_policy"]


def test_weighted_retrieval_prefers_official_on_ambiguous_query():
    corpus = load_corpus()
    weights = load_source_weights()
    query = "savings minimum balance requirement monthly fee"
    weighted = retrieve_weighted(query, corpus, weights, top_k=1)[0]
    assert weighted["doc_id"] == "minimum_balance_policy"
    assert weighted["source_weight"] == 1.0


def test_weighted_scores_include_raw_and_weight():
    results = retrieve_weighted("checking account balance", load_corpus(), top_k=1)
    assert "raw_score" in results[0]
    assert "source_weight" in results[0]
    assert results[0]["chunk_id"] == "chk_bal_01"
