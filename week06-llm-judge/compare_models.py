"""
Priority 3 — Compare two Ollama models as LLM judges on the same candidates.

Usage:
  python compare_models.py --dry-run --limit 3
  python compare_models.py --limit 5
  python compare_models.py --model-a llama3.2 --model-b mistral --limit 5
  python compare_models.py --all

Requires: ollama pull llama3.2 && ollama pull mistral
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

WEEK06_ROOT = Path(__file__).resolve().parent
PORTFOLIO_ROOT = WEEK06_ROOT.parent
REPORTS_DIR = PORTFOLIO_ROOT / "reports"

sys.path.insert(0, str(WEEK06_ROOT))
from llm_judge_ollama import (  # noqa: E402
    check_ollama_reachable,
    collect_candidates,
    evaluate_item,
    load_json,
    print_ollama_install_help,
)

DEFAULT_MODEL_A = "llama3.2"
DEFAULT_MODEL_B = "mistral"


def summarize_comparison(rows: list[dict], dry_run: bool) -> dict:
    n = len(rows)
    factual_ok = sum(1 for r in rows if r["factual_pass"])

    if dry_run or n == 0:
        return {
            "count": n,
            "factual_pass": factual_ok,
            "model_a_judge_pass": None,
            "model_b_judge_pass": None,
            "model_a_agreement": None,
            "model_b_agreement": None,
            "models_agree_with_each_other": None,
            "disagreement_cases": [],
        }

    a_judge = sum(1 for r in rows if r["judge_a_pass"])
    b_judge = sum(1 for r in rows if r["judge_b_pass"])
    a_agree = sum(1 for r in rows if r["agree_a"])
    b_agree = sum(1 for r in rows if r["agree_b"])
    models_agree = sum(1 for r in rows if r["models_agree"])

    disagreements = [
        {
            "scenario": r["scenario"],
            "id": r["id"],
            "factual": r["factual_pass"],
            "judge_a": r["judge_a_verdict"],
            "judge_b": r["judge_b_verdict"],
        }
        for r in rows
        if not r["models_agree"]
    ]

    return {
        "count": n,
        "factual_pass": factual_ok,
        "model_a_judge_pass": a_judge,
        "model_b_judge_pass": b_judge,
        "model_a_agreement": a_agree,
        "model_b_agreement": b_agree,
        "models_agree_with_each_other": models_agree,
        "disagreement_cases": disagreements,
    }


def compare_row(item: dict, domain: str, model_a: str, model_b: str, dry_run: bool) -> dict:
    ra = evaluate_item(item, domain, model_a, dry_run)
    rb = evaluate_item(item, domain, model_b, dry_run)

    row = {
        "scenario": item["scenario"],
        "id": item["id"],
        "text": item["text"],
        "factual_pass": ra["factual_pass"],
        "judge_a_verdict": ra.get("judge_verdict"),
        "judge_b_verdict": rb.get("judge_verdict"),
        "judge_a_reason": ra.get("judge_reason"),
        "judge_b_reason": rb.get("judge_reason"),
    }

    if dry_run:
        row.update(
            {
                "judge_a_pass": None,
                "judge_b_pass": None,
                "agree_a": None,
                "agree_b": None,
                "models_agree": None,
            }
        )
    else:
        row.update(
            {
                "judge_a_pass": ra["judge_pass"],
                "judge_b_pass": rb["judge_pass"],
                "agree_a": ra["agreement"],
                "agree_b": rb["agreement"],
                "models_agree": ra["judge_verdict"] == rb["judge_verdict"],
            }
        )
    return row


def print_report(rows: list[dict], summary: dict, model_a: str, model_b: str, dry_run: bool) -> None:
    print("Ollama model comparison — LLM-as-judge")
    print("=" * 70)
    if dry_run:
        print("Mode: DRY-RUN")
    else:
        print(f"Model A: {model_a}")
        print(f"Model B: {model_b}")
    print()
    print(f"Candidates: {summary['count']}")
    print(f"Factual PASS: {summary['factual_pass']}/{summary['count']}")

    if not dry_run:
        n = summary["count"]
        print(f"Judge PASS A: {summary['model_a_judge_pass']}/{n}")
        print(f"Judge PASS B: {summary['model_b_judge_pass']}/{n}")
        print(f"Agreement with factual A: {summary['model_a_agreement']}/{n}")
        print(f"Agreement with factual B: {summary['model_b_agreement']}/{n}")
        print(
            f"Models agree with each other: {summary['models_agree_with_each_other']}/{n}"
        )
        print()
        for d in summary["disagreement_cases"]:
            print(
                f"  DISAGREE [{d['scenario']}/{d['id']}] "
                f"factual={d['factual']} A={d['judge_a']} B={d['judge_b']}"
            )
    print()


def save_html(
    rows: list[dict],
    summary: dict,
    path: Path,
    model_a: str,
    model_b: str,
    dry_run: bool,
) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    trs = []
    for r in rows:
        if dry_run:
            cls = "ok" if r["factual_pass"] else "fail"
            ja, jb, ma = "DRY", "DRY", "—"
        else:
            cls = "ok" if r["models_agree"] else "disagree"
            ja, jb = r["judge_a_verdict"], r["judge_b_verdict"]
            ma = "yes" if r["models_agree"] else "no"
        trs.append(
            f"""<tr class="{cls}">
<td>{r['scenario']}</td><td>{r['id']}</td><td>{r['text']}</td>
<td>{'PASS' if r['factual_pass'] else 'FAIL'}</td>
<td>{ja}</td><td>{jb}</td><td>{ma}</td>
</tr>"""
        )

    n = summary["count"]
    extra = ""
    if not dry_run:
        extra = f"""
<p><b>Judge PASS A ({model_a}):</b> {summary['model_a_judge_pass']}/{n}</p>
<p><b>Judge PASS B ({model_b}):</b> {summary['model_b_judge_pass']}/{n}</p>
<p><b>Agree with factual A:</b> {summary['model_a_agreement']}/{n}</p>
<p><b>Agree with factual B:</b> {summary['model_b_agreement']}/{n}</p>
<p><b>Models agree:</b> {summary['models_agree_with_each_other']}/{n}</p>"""

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Ollama model comparison</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; }}
table {{ border-collapse: collapse; width: 100%; font-size: 0.85rem; }}
th, td {{ border: 1px solid #ccc; padding: 0.4rem; }}
th {{ background: #2c3e50; color: #fff; }}
tr.ok {{ background: #d4edda; }}
tr.fail {{ background: #f8d7da; }}
tr.disagree {{ background: #fff3cd; }}
</style></head><body>
<h1>Ollama LLM judge — model comparison</h1>
<p>{ts} — A: {model_a} | B: {model_b}</p>
<p><b>Factual PASS:</b> {summary['factual_pass']}/{n}</p>
{extra}
<table>
<thead><tr>
<th>Scenario</th><th>ID</th><th>Text</th><th>Factual</th>
<th>Judge A</th><th>Judge B</th><th>Models agree</th>
</tr></thead>
<tbody>{''.join(trs)}</tbody>
</table>
</body></html>"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two Ollama judge models")
    parser.add_argument("--model-a", default=DEFAULT_MODEL_A)
    parser.add_argument("--model-b", default=DEFAULT_MODEL_B)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    scenarios = load_json(PORTFOLIO_ROOT / "data" / "golden_scenarios.json")
    candidates = load_json(PORTFOLIO_ROOT / "data" / "candidates.json")
    limit = None if args.all else args.limit
    items = collect_candidates(scenarios, candidates, limit)

    if not args.dry_run and not check_ollama_reachable():
        print_ollama_install_help()
        print(f"Then pull both models:")
        print(f"  ollama pull {args.model_a}")
        print(f"  ollama pull {args.model_b}")
        sys.exit(1)

    rows = [compare_row(item, "banking", args.model_a, args.model_b, args.dry_run) for item in items]
    summary = summarize_comparison(rows, args.dry_run)
    print_report(rows, summary, args.model_a, args.model_b, args.dry_run)

    slug_a = args.model_a.replace(":", "_")
    slug_b = args.model_b.replace(":", "_")
    html_path = REPORTS_DIR / f"ollama_compare_{slug_a}_vs_{slug_b}.html"
    save_html(rows, summary, html_path, args.model_a, args.model_b, args.dry_run)
    print(f"HTML report: {html_path}")

    json_path = REPORTS_DIR / f"ollama_compare_{slug_a}_vs_{slug_b}.json"
    json_path.write_text(
        json.dumps({"summary": summary, "rows": rows}, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"JSON summary: {json_path}")


if __name__ == "__main__":
    main()
