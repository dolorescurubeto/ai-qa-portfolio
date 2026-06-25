"""Shared factual validation helpers (same logic as week02)."""

import re


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
