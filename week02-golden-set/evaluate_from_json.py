"""
Week 2 — Evaluate ALL scenarios from JSON.

Reads:
  - data/golden_scenarios.json  (references and expected facts)
  - data/candidates.json        (simulated responses per scenario)

Usage:
  cd week02-golden-set
  python evaluate_from_json.py
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS_FILE = ROOT / "data" / "golden_scenarios.json"
CANDIDATES_FILE = ROOT / "data" / "candidates.json"


def extract_amount(text: str):
    match = re.search(r"\$\s*([0-9,]+\.\d{2})", text)
    if match:
        return f"${match.group(1)}"
    return None


def extract_account_type(text: str):
    text_lower = text.lower()
    for acc_type in ["term deposit", "checking", "savings"]:
        if acc_type in text_lower:
            return acc_type
    return None


def validate_factual(reference: str, candidate: str) -> dict:
    ref_amount = extract_amount(reference)
    cand_amount = extract_amount(candidate)
    ref_acc = extract_account_type(reference)
    cand_acc = extract_account_type(candidate)

    amount_match = ref_amount == cand_amount if ref_amount and cand_amount else False
    account_match = ref_acc == cand_acc if ref_acc and cand_acc else False

    return {
        "amount_match": amount_match,
        "account_type_match": account_match,
        "pass": amount_match and account_match,
    }


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def candidate_note(cand: dict) -> str | None:
    return cand.get("note") or cand.get("nota")


def evaluate_scenario(scenario_key: str, scenario: dict, candidates: list) -> dict:
    reference = scenario["reference"]
    passed = 0
    results = []

    print(f"\n{'=' * 60}")
    print(f"SCENARIO: {scenario_key}")
    print(f"Description: {scenario.get('description', '-')}")
    print(f"Reference: {reference}")
    print(f"Expected: {scenario.get('facts', {})}")
    print("-" * 60)

    for cand in candidates:
        result = validate_factual(reference, cand["text"])
        status = "PASS" if result["pass"] else "FAIL"
        if result["pass"]:
            passed += 1

        print(f"[{status}] {cand['id']}")
        print(f"  Text: {cand['text']}")
        print(
            f"  Amount OK: {result['amount_match']} | "
            f"Account OK: {result['account_type_match']}"
        )
        note = candidate_note(cand)
        if note:
            print(f"  Note: {note}")
        print()

        results.append({"id": cand["id"], "status": status, **result})

    total = len(candidates)
    print(f"Subtotal: {passed}/{total} PASS")
    return {"key": scenario_key, "passed": passed, "total": total, "results": results}


def main():
    scenarios = load_json(SCENARIOS_FILE)
    all_candidates = load_json(CANDIDATES_FILE)

    print("WEEK 2 — Evaluation from JSON")
    print(f"Scenarios loaded: {len(scenarios)}")

    grand_passed = 0
    grand_total = 0
    summary = []

    for scenario_key, scenario in scenarios.items():
        candidates = all_candidates.get(scenario_key, [])
        if not candidates:
            print(f"\n[WARNING] No candidates in candidates.json for: {scenario_key}")
            continue

        report = evaluate_scenario(scenario_key, scenario, candidates)
        summary.append(report)
        grand_passed += report["passed"]
        grand_total += report["total"]

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for item in summary:
        print(f"  {item['key']}: {item['passed']}/{item['total']} PASS")
    print("-" * 60)
    if grand_total:
        pct = grand_passed / grand_total * 100
        print(f"TOTAL: {grand_passed}/{grand_total} PASS ({pct:.0f}%)")
    else:
        print("No candidates to evaluate.")
        sys.exit(1)


if __name__ == "__main__":
    main()
