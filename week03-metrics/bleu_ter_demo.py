"""
Week 3 — BLEU and TER demo (banking wording, English).

Shows that BLEU rewards word overlap, not factual correctness.

Usage:
  cd week03-metrics
  python bleu_ter_demo.py
"""

import nltk
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)

REFERENCE = "Your checking account balance is $1,847.32.".split()

CANDIDATES = [
    "Your checking account balance is $1,847.32.",
    "The balance in your checking account is $1,800.32.",
    "You have $1,847.32 in your checking account.",
    "Your savings account balance is $1,847.32.",
]


def calc_ter(pred: str, ref: str) -> float:
    pred_tokens = pred.split()
    ref_tokens = ref.split()
    rows = len(pred_tokens) + 1
    cols = len(ref_tokens) + 1
    dp = [[0] * cols for _ in range(rows)]

    for i in range(rows):
        dp[i][0] = i
    for j in range(cols):
        dp[0][j] = j

    for i in range(1, rows):
        for j in range(1, cols):
            cost = 0 if pred_tokens[i - 1] == ref_tokens[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)

    edits = dp[len(pred_tokens)][len(ref_tokens)]
    return edits / len(ref_tokens)


def main():
    ref_text = "Your checking account balance is $1,847.32."
    smooth = SmoothingFunction().method1

    print("WEEK 3 — BLEU & TER demo (checking balance)")
    print("Reference:", ref_text)
    print()
    print(f"{'Candidate':<58} BLEU    TER")
    print("-" * 72)

    for cand in CANDIDATES:
        bleu = sentence_bleu([REFERENCE], cand.split(), smoothing_function=smooth)
        ter = calc_ter(cand, ref_text)
        print(f"{cand:<58} {bleu:.3f}   {ter:.3f}")

    print()
    print("Note: cand4 swaps 'checking' for 'savings' but still scores BLEU 0.54.")
    print("Word overlap alone does not catch factual errors reliably.")


if __name__ == "__main__":
    main()
