"""Week 8 — Go/no-go decision pack tests."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PACK_DIR = ROOT / "week12-go-no-go"
sys.path.insert(0, str(PACK_DIR))

from go_no_go_pack import (  # noqa: E402
    build_pack,
    evaluate_all_categories,
    overall_decision,
    CategoryResult,
)


def test_evaluate_all_categories_count():
    cats = evaluate_all_categories()
    assert len(cats) == 7


def test_calibration_category_fails_ece_gate():
    cats = evaluate_all_categories()
    cal = next(c for c in cats if c.name == "Confidence calibration")
    assert cal.status == "FAIL"
    assert float(cal.value) > 0.25


def test_retrieval_category_passes():
    cats = evaluate_all_categories()
    ret = next(c for c in cats if "retrieval" in c.name.lower())
    assert ret.status == "PASS"


def test_overall_decision_no_go_when_calibration_fails():
    cats = evaluate_all_categories()
    decision = overall_decision(cats, pytest_ok=True)
    assert decision == "NO-GO"


def test_overall_decision_no_go_when_pytest_fails():
    cats = evaluate_all_categories()
    decision = overall_decision(cats, pytest_ok=False)
    assert decision == "NO-GO"


def test_build_pack_writes_html_and_json(tmp_path, monkeypatch):
    import go_no_go_pack as pack

    monkeypatch.setattr(pack, "REPORTS_DIR", tmp_path)
    html_path, json_path = build_pack(run_pytest=False)
    assert html_path.exists()
    assert json_path.exists()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["decision"] in {"GO", "NO-GO", "GO-WITH-CONDITIONS"}
    assert "categories" in data
    assert "AI QA Go/No-Go" in html_path.read_text(encoding="utf-8")
