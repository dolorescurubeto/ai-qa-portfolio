"""Shared fixtures for portfolio pytest suite."""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS_FILE = ROOT / "data" / "golden_scenarios.json"
CANDIDATES_FILE = ROOT / "data" / "candidates.json"

# Locked baseline — update only when golden_scenarios.json or candidates.json change on purpose
EXPECTED_TOTAL_CANDIDATES = 23
EXPECTED_FACTUAL_PASS = 12


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def portfolio_root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def scenarios() -> dict:
    return load_json(SCENARIOS_FILE)


@pytest.fixture(scope="session")
def candidates() -> dict:
    return load_json(CANDIDATES_FILE)


@pytest.fixture(scope="session")
def golden_set_rows(scenarios, candidates) -> list[dict]:
    """Flat list of {scenario_key, candidate_id, reference, text, ...}."""
    rows = []
    for scenario_key, scenario in scenarios.items():
        for cand in candidates.get(scenario_key, []):
            rows.append(
                {
                    "scenario_key": scenario_key,
                    "candidate_id": cand["id"],
                    "reference": scenario["reference"],
                    "text": cand["text"],
                    "note": cand.get("note"),
                    "facts": scenario.get("facts", {}),
                }
            )
    return rows
