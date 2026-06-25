"""
Week 3 — True Lies validation on checking_balance from JSON.

Generates an HTML report via true-lies-validator.

Usage:
  cd week03-metrics
  python true_lies_report.py
"""

import json
import sys
from pathlib import Path

from true_lies import create_scenario, validate_llm_candidates

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS_FILE = ROOT / "data" / "golden_scenarios.json"
CANDIDATES_FILE = ROOT / "data" / "candidates.json"
REPORTS_DIR = ROOT / "reports"

SCENARIO_KEY = "checking_balance"
THRESHOLD = 0.65


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_scenario(scenario: dict):
    facts = scenario["facts"]
    return create_scenario(
        facts={
            "balance": {
                "expected": facts["balance"],
                "extractor": "regex",
                "pattern": r"\$\s*[0-9,]+\.\d{2}",
            },
            "account_type": {
                "expected": facts["account_type"],
                "extractor": "regex",
                "pattern": r"(?i)(checking|savings|term deposit)",
            },
        },
        semantic_reference=scenario["reference"],
    )


def main():
    scenarios = load_json(SCENARIOS_FILE)
    all_candidates = load_json(CANDIDATES_FILE)

    scenario = scenarios[SCENARIO_KEY]
    candidates = [c["text"] for c in all_candidates[SCENARIO_KEY]]

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_name = str(REPORTS_DIR / "week03_true_lies_checking.html")

    tl_scenario = build_scenario(scenario)
    result = validate_llm_candidates(
        scenario=tl_scenario,
        candidates=candidates,
        threshold=THRESHOLD,
        generate_html_report=True,
        html_title="Checking balance — True Lies validation",
        html_output_file=report_name,
    )

    summary = result["summary"]
    print("WEEK 3 — True Lies (checking_balance)")
    print("=" * 60)
    print(f"Candidates: {result['total_candidates']}")
    print(f"Fully valid (factual + semantic): {result['fully_valid']}")
    print(f"Factual accuracy: {summary['factual_accuracy']:.1%}")
    print(f"Overall accuracy: {summary['overall_accuracy']:.1%}")
    print()

    for item in result["results"]:
        status = "PASS" if item["is_valid"] else "FAIL"
        score = item["result"].get(
            "semantic_f1", item["result"].get("similarity_score", 0)
        )
        print(f"[{status}] f1={score:.3f}")
        print(f"  Text: {item['candidate']}")
        if not item["is_valid"] and item["result"].get("failure_reason"):
            print(f"  Reason: {item['result']['failure_reason']}")
        print()

    html_path = result.get("html_report_path") or report_name
    print(f"HTML report: {html_path}")


if __name__ == "__main__":
    main()
