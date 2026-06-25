"""
Week 1 — Simple factual validation (no API, no BERT).

Simulates responses from a banking chatbot and verifies:
  - correct amount
  - correct account type

Usage:
  python evaluate_factual.py
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS_FILE = ROOT / "data" / "golden_scenarios.json"

# Simulated "model" responses for the checking scenario
CANDIDATES_CHECKING = [
    {
        "id": "cand1",
        "text": "Your checking account balance is $1,847.32.",
        "note": "Correct — exact copy of reference",
    },
    {
        "id": "cand2",
        "text": "The balance in your checking account is $1,800.32.",
        "note": "Similar wording but wrong amount",
    },
    {
        "id": "cand3",
        "text": "Your savings account balance is $1,847.32.",
        "note": "Amount OK but wrong account type",
    },
    {
        "id": "cand4",
        "text": "You have $1,847.32 in your checking account.",
        "note": "Correct — different wording",
    },
    {
        "id": "cand5",
        "text": "You have $1,847.32 in your account.",
        "note": "Amount OK but missing checking — incomplete",
    },
]


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


def load_scenario(key: str) -> dict:
    with open(SCENARIOS_FILE, encoding="utf-8") as f:
        scenarios = json.load(f)
    return scenarios[key]


def main():
    scenario = load_scenario("checking_balance")
    reference = scenario["reference"]

    print("=" * 60)
    print("WEEK 1 — Factual validation (fictional banking chatbot)")
    print("=" * 60)
    print(f"Scenario: checking_balance")
    print(f"Reference: {reference}")
    print(f"Expected: {scenario['facts']}")
    print()

    passed = 0
    for cand in CANDIDATES_CHECKING:
        result = validate_factual(reference, cand["text"])
        status = "PASS" if result["pass"] else "FAIL"
        if result["pass"]:
            passed += 1

        print(f"[{status}] {cand['id']}")
        print(f"  Text: {cand['text']}")
        print(f"  Amount OK: {result['amount_match']} | Account OK: {result['account_type_match']}")
        print(f"  Note: {cand['note']}")
        print()

    print("-" * 60)
    print(f"Result: {passed}/{len(CANDIDATES_CHECKING)} PASS")
    print()
    print("Key idea: cand2 may 'sound fine' but FAILS on amount.")
    print("Key idea: cand3 has the right amount but FAILS on account type.")
    print("That is real AI testing — not just reading the response once.")


if __name__ == "__main__":
    main()
