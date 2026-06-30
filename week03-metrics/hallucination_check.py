"""
Factual validation vs True Lies — hallucination / fact-error comparison.

True Lies failure reasons:
  - "Possible hallucination found in the candidate" → low semantic similarity
  - "Factual accuracy issues detected" → wrong extracted facts

Our factual validator (Week 1–2) flags wrong amounts, account types, etc.

Usage:
  cd week03-metrics
  python hallucination_check.py                  # banking portfolio
  python hallucination_check.py --retail         # retailco-day1-practice
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from true_lies import create_scenario, validate_against_reference_dynamic

from factual import validate_factual

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

PORTFOLIO_ROOT = Path(__file__).resolve().parent.parent
RETAIL_ROOT = Path(r"C:\Users\dell\retailco-day1-practice")
REPORTS_DIR = PORTFOLIO_ROOT / "reports"
THRESHOLD = 0.65


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_banking_scenario(scenario: dict):
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


def build_retail_scenario(key: str, scenario: dict):
    ref = scenario["reference"]
    if key == "return_policy":
        return create_scenario(
            facts={
                "days": {
                    "expected": "30",
                    "extractor": "regex",
                    "pattern": r"\b30\b",
                }
            },
            semantic_reference=ref,
        )
    if key == "shipping_cost":
        return create_scenario(
            facts={
                "amount": {
                    "expected": "$5.99",
                    "extractor": "regex",
                    "pattern": r"\$\s*[0-9]+\.\d{2}",
                }
            },
            semantic_reference=ref,
        )
    if key == "order_status":
        return create_scenario(
            facts={
                "order_id": {
                    "expected": "ORD-78421",
                    "extractor": "regex",
                    "pattern": r"ORD-78421",
                },
                "status": {
                    "expected": "shipped",
                    "extractor": "regex",
                    "pattern": r"(?i)shipped",
                },
            },
            semantic_reference=ref,
        )
    raise ValueError(f"Unknown retail scenario: {key}")


def retail_factual_pass(key: str, reference: str, candidate: str) -> bool:
    sys.path.insert(0, str(RETAIL_ROOT))
    from evaluate_day1 import validate_scenario  # noqa: WPS433

    return validate_scenario(key, reference, candidate)["pass"]


def evaluate_all(
    scenarios: dict,
    candidates: dict,
    domain: str,
) -> list[dict]:
    rows = []

    for scenario_key, scenario in scenarios.items():
        reference = scenario["reference"]
        if domain == "banking":
            tl_scenario = build_banking_scenario(scenario)
        else:
            tl_scenario = build_retail_scenario(scenario_key, scenario)

        for cand in candidates.get(scenario_key, []):
            text = cand["text"]
            if domain == "banking":
                factual_pass = validate_factual(reference, text)["pass"]
            else:
                factual_pass = retail_factual_pass(scenario_key, reference, text)

            tl = validate_against_reference_dynamic(
                text, tl_scenario, similarity_threshold=THRESHOLD
            )
            reason = tl.get("failure_reason") or ""
            reason_lower = reason.lower()

            rows.append(
                {
                    "scenario": scenario_key,
                    "id": cand["id"],
                    "text": text,
                    "factual_pass": factual_pass,
                    "true_lies_pass": tl.get("is_valid", False),
                    "tl_factual_ok": tl.get("factual_accuracy", False),
                    "semantic_f1": round(tl.get("semantic_f1", 0), 3),
                    "failure_reason": reason or "-",
                    "hallucination_flag": "hallucination" in reason_lower,
                    "factual_issue_flag": "factual accuracy" in reason_lower,
                    "gap_semantic_ok_fact_wrong": (
                        tl.get("is_valid", False) and not factual_pass
                    ),
                }
            )

    return rows


def print_report(rows: list[dict], title: str) -> None:
    print(title)
    print("=" * 70)
    print(f"Threshold (True Lies semantic): {THRESHOLD}")
    print()

    factual_ok = sum(1 for r in rows if r["factual_pass"])
    tl_ok = sum(1 for r in rows if r["true_lies_pass"])
    hallu = sum(1 for r in rows if r["hallucination_flag"])
    fact_issues = sum(1 for r in rows if r["factual_issue_flag"])
    gaps = sum(1 for r in rows if r["gap_semantic_ok_fact_wrong"])

    print(f"Candidates: {len(rows)}")
    print(f"Our factual PASS:     {factual_ok}/{len(rows)}")
    print(f"True Lies PASS:       {tl_ok}/{len(rows)}")
    print(f"TL 'hallucination':   {hallu}  (low semantic similarity)")
    print(f"TL 'factual issues':  {fact_issues}  (wrong extracted facts)")
    print(f"GAP (TL pass, factual fail): {gaps}")
    print()

    print("DETAIL")
    print("-" * 70)
    for r in rows:
        f = "PASS" if r["factual_pass"] else "FAIL"
        t = "PASS" if r["true_lies_pass"] else "FAIL"
        flags = []
        if r["hallucination_flag"]:
            flags.append("HALLUCINATION?")
        if r["factual_issue_flag"]:
            flags.append("FACTUAL")
        if r["gap_semantic_ok_fact_wrong"]:
            flags.append("GAP")

        print(f"[{r['scenario']}] {r['id']}")
        print(f"  Text: {r['text']}")
        print(f"  Factual: {f} | True Lies: {t} | F1: {r['semantic_f1']}")
        print(f"  Reason: {r['failure_reason']}")
        if flags:
            print(f"  Flags: {', '.join(flags)}")
        print()


def save_html(rows: list[dict], path: Path, title: str) -> None:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    factual_ok = sum(1 for r in rows if r["factual_pass"])
    tl_ok = sum(1 for r in rows if r["true_lies_pass"])
    hallu = sum(1 for r in rows if r["hallucination_flag"])
    fact_issues = sum(1 for r in rows if r["factual_issue_flag"])

    body_rows = []
    for r in rows:
        cls = ""
        if r["gap_semantic_ok_fact_wrong"]:
            cls = "gap"
        elif r["hallucination_flag"]:
            cls = "hallu"
        elif r["factual_issue_flag"]:
            cls = "factual"
        elif r["factual_pass"] and r["true_lies_pass"]:
            cls = "ok"

        body_rows.append(
            f"""<tr class="{cls}">
<td>{r['scenario']}</td><td>{r['id']}</td><td>{r['text']}</td>
<td>{'PASS' if r['factual_pass'] else 'FAIL'}</td>
<td>{'PASS' if r['true_lies_pass'] else 'FAIL'}</td>
<td>{r['semantic_f1']}</td>
<td>{r['failure_reason']}</td>
</tr>"""
        )

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>{title}</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; }}
.summary {{ background: #f4f6f8; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; }}
table {{ border-collapse: collapse; width: 100%; font-size: 0.85rem; }}
th, td {{ border: 1px solid #ccc; padding: 0.4rem 0.5rem; text-align: left; vertical-align: top; }}
th {{ background: #2c3e50; color: #fff; }}
tr.ok {{ background: #d4edda; }}
tr.gap {{ background: #fff3cd; }}
tr.hallu {{ background: #f8d7da; }}
tr.factual {{ background: #ffe8cc; }}
</style></head><body>
<h1>{title}</h1>
<p>Generated {generated}</p>
<div class="summary">
<p><b>Factual PASS:</b> {factual_ok}/{len(rows)}</p>
<p><b>True Lies PASS:</b> {tl_ok}/{len(rows)}</p>
<p><b>TL hallucination label:</b> {hallu}</p>
<p><b>TL factual issues label:</b> {fact_issues}</p>
</div>
<table>
<thead><tr>
<th>Scenario</th><th>ID</th><th>Text</th>
<th>Factual</th><th>True Lies</th><th>F1</th><th>Reason</th>
</tr></thead>
<tbody>{''.join(body_rows)}</tbody>
</table>
<p><b>Note:</b> True Lies uses "hallucination" for low semantic similarity, and
"factual accuracy issues" for wrong facts. Use both layers in AI QA.</p>
</body></html>"""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--retail",
        action="store_true",
        help="Run on retailco-day1-practice instead of banking portfolio",
    )
    args = parser.parse_args()

    if args.retail:
        scenarios = load_json(RETAIL_ROOT / "golden_scenarios.json")
        candidates = load_json(RETAIL_ROOT / "candidates.json")
        domain = "retail"
        title = "Hallucination check — RetailCo Day 1"
        html_name = "hallucination_check_retailco.html"
    else:
        scenarios = load_json(PORTFOLIO_ROOT / "data" / "golden_scenarios.json")
        candidates = load_json(PORTFOLIO_ROOT / "data" / "candidates.json")
        domain = "banking"
        title = "Hallucination check — Banking portfolio"
        html_name = "hallucination_check_banking.html"

    rows = evaluate_all(scenarios, candidates, domain)
    print_report(rows, title)

    html_path = REPORTS_DIR / html_name
    save_html(rows, html_path, title)
    print(f"HTML report: {html_path}")


if __name__ == "__main__":
    main()
