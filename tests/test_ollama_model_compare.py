"""Tests for Ollama model comparison summary logic (no live API)."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "week06-llm-judge"))

from compare_models import summarize_comparison  # noqa: E402


def test_summarize_dry_run():
    rows = [{"factual_pass": True}, {"factual_pass": False}]
    s = summarize_comparison(rows, dry_run=True)
    assert s["count"] == 2
    assert s["factual_pass"] == 1
    assert s["model_a_judge_pass"] is None


def test_summarize_models_agreement():
    rows = [
        {
            "factual_pass": True,
            "judge_a_pass": True,
            "judge_b_pass": True,
            "agree_a": True,
            "agree_b": True,
            "models_agree": True,
            "judge_a_verdict": "PASS",
            "judge_b_verdict": "PASS",
            "scenario": "checking_balance",
            "id": "cand1",
        },
        {
            "factual_pass": False,
            "judge_a_pass": False,
            "judge_b_pass": True,
            "agree_a": True,
            "agree_b": False,
            "models_agree": False,
            "judge_a_verdict": "FAIL",
            "judge_b_verdict": "PASS",
            "scenario": "checking_balance",
            "id": "cand2",
        },
    ]
    s = summarize_comparison(rows, dry_run=False)
    assert s["model_a_agreement"] == 2
    assert s["model_b_agreement"] == 1
    assert s["models_agree_with_each_other"] == 1
    assert len(s["disagreement_cases"]) == 1
    assert s["disagreement_cases"][0]["id"] == "cand2"
