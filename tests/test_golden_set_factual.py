"""Parametrized factual validation over the full banking golden set."""

import json
from pathlib import Path

import pytest

from conftest import EXPECTED_FACTUAL_PASS, EXPECTED_TOTAL_CANDIDATES
from factual import validate_factual

_ROOT = Path(__file__).resolve().parent.parent


def _load_golden_rows() -> list[dict]:
    with open(_ROOT / "data" / "golden_scenarios.json", encoding="utf-8") as f:
        scenarios = json.load(f)
    with open(_ROOT / "data" / "candidates.json", encoding="utf-8") as f:
        candidates = json.load(f)
    rows = []
    for scenario_key, scenario in scenarios.items():
        for cand in candidates.get(scenario_key, []):
            rows.append(
                {
                    "scenario_key": scenario_key,
                    "candidate_id": cand["id"],
                    "reference": scenario["reference"],
                    "text": cand["text"],
                }
            )
    return rows


_GOLDEN_ROWS = _load_golden_rows()
_ROW_IDS = [f"{r['scenario_key']}/{r['candidate_id']}" for r in _GOLDEN_ROWS]


@pytest.mark.integration
def test_golden_set_row_count():
    assert len(_GOLDEN_ROWS) == EXPECTED_TOTAL_CANDIDATES


@pytest.mark.integration
@pytest.mark.parametrize("row", _GOLDEN_ROWS, ids=_ROW_IDS)
def test_factual_validation_runs(row):
    result = validate_factual(row["reference"], row["text"])
    assert isinstance(result["pass"], bool)


@pytest.mark.regression
def test_golden_set_baseline_pass_rate():
    """Regression lock: 12/23 factual PASS on current banking data."""
    passed = sum(
        1 for row in _GOLDEN_ROWS if validate_factual(row["reference"], row["text"])["pass"]
    )
    assert len(_GOLDEN_ROWS) == EXPECTED_TOTAL_CANDIDATES
    assert passed == EXPECTED_FACTUAL_PASS
