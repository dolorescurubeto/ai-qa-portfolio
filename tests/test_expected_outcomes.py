"""Explicit expected PASS/FAIL for selected high-value cases (documentation + guard)."""

import pytest

from factual import validate_factual

# scenario_key, candidate_id, expected_pass, reason (for test report / Jira-style traceability)
DOCUMENTED_CASES = [
    ("checking_balance", "cand1", True, "Exact reference match"),
    ("checking_balance", "cand2", False, "Wrong amount — must fail factual"),
    ("checking_balance", "cand3", False, "Wrong account type"),
    ("checking_balance", "cand4", True, "Paraphrase with correct facts"),
    ("transfer_limit", "cand4", False, "Wrong limit amount"),
    ("minimum_balance_savings", "cand3", False, "Wrong account on minimum balance"),
]


@pytest.mark.regression
@pytest.mark.parametrize(
    "scenario_key,candidate_id,expected_pass,reason",
    DOCUMENTED_CASES,
    ids=[f"{s}/{c}" for s, c, _, _ in DOCUMENTED_CASES],
)
def test_documented_outcomes(scenarios, candidates, scenario_key, candidate_id, expected_pass, reason):
    scenario = scenarios[scenario_key]
    cand = next(c for c in candidates[scenario_key] if c["id"] == candidate_id)
    result = validate_factual(scenario["reference"], cand["text"])
    assert result["pass"] is expected_pass, reason
