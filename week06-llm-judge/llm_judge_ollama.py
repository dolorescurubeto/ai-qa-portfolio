"""
LLM-as-judge with Ollama — factual validation vs local LLM judge.

Layer 4: after regex factual checks (week01–03), ask a local model to judge
whether a candidate response is factually accurate vs the reference.

Usage:
  cd week06-llm-judge
  python llm_judge_ollama.py --dry-run --limit 3
  python llm_judge_ollama.py --limit 3
  python llm_judge_ollama.py --all
  python llm_judge_ollama.py --retail --limit 3
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

WEEK06_ROOT = Path(__file__).resolve().parent
PORTFOLIO_ROOT = WEEK06_ROOT.parent
WEEK03_DIR = PORTFOLIO_ROOT / "week03-metrics"
RETAIL_ROOT = Path(r"C:\Users\dell\retailco-day1-practice")
REPORTS_DIR = PORTFOLIO_ROOT / "reports"

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "llama3.2"

sys.path.insert(0, str(WEEK03_DIR))
from factual import validate_factual  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def retail_factual_pass(key: str, reference: str, candidate: str) -> bool:
    sys.path.insert(0, str(RETAIL_ROOT))
    from evaluate_day1 import validate_scenario  # noqa: WPS433

    return validate_scenario(key, reference, candidate)["pass"]


def build_judge_prompt(description: str, reference: str, candidate: str) -> str:
    return f"""You are a QA judge for a chatbot. Compare the candidate response to the reference answer.

Scenario: {description}

Reference answer (ground truth):
{reference}

Candidate response:
{candidate}

Focus on factual accuracy: dollar amounts, account types, policy facts, order IDs, dates.
Ignore minor wording differences if the facts are correct.

Return ONLY valid JSON with this exact shape:
{{"verdict": "PASS" or "FAIL", "reason": "one short sentence"}}"""


def check_ollama_reachable() -> bool:
    try:
        req = urllib.request.Request(
            "http://localhost:11434/api/tags",
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def print_ollama_install_help() -> None:
    print("Ollama is not running or not installed.")
    print()
    print("Install on Windows:")
    print("  1. Download from https://ollama.com/download")
    print("  2. Install and start Ollama")
    print("  3. Pull the model:  ollama pull llama3.2")
    print("  4. Re-run this script (without --dry-run)")
    print()


def call_ollama_judge(model: str, prompt: str) -> dict:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a strict factual QA judge. "
                    "Reply with JSON only: {\"verdict\": \"PASS\"|\"FAIL\", \"reason\": \"...\"}"
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "format": "json",
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read().decode("utf-8"))

    content = body.get("message", {}).get("content", "")
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return {
            "verdict": "FAIL",
            "reason": f"Judge returned invalid JSON: {content[:120]}",
            "parse_error": True,
        }

    verdict = str(parsed.get("verdict", "")).upper()
    if verdict not in ("PASS", "FAIL"):
        verdict = "FAIL"
    return {
        "verdict": verdict,
        "reason": str(parsed.get("reason", "")).strip() or "No reason given",
        "parse_error": False,
    }


def collect_candidates(
    scenarios: dict,
    candidates: dict,
    limit: int | None,
) -> list[dict]:
    items = []
    for scenario_key, scenario in scenarios.items():
        for cand in candidates.get(scenario_key, []):
            items.append(
                {
                    "scenario": scenario_key,
                    "description": scenario.get("description", scenario_key),
                    "reference": scenario["reference"],
                    "id": cand["id"],
                    "text": cand["text"],
                }
            )
            if limit is not None and len(items) >= limit:
                return items
    return items


def evaluate_item(
    item: dict,
    domain: str,
    model: str,
    dry_run: bool,
) -> dict:
    reference = item["reference"]
    text = item["text"]
    scenario_key = item["scenario"]

    if domain == "banking":
        factual_pass = validate_factual(reference, text)["pass"]
    else:
        factual_pass = retail_factual_pass(scenario_key, reference, text)

    prompt = build_judge_prompt(item["description"], reference, text)

    if dry_run:
        return {
            **item,
            "factual_pass": factual_pass,
            "judge_verdict": None,
            "judge_pass": None,
            "judge_reason": "(dry-run — no API call)",
            "agreement": None,
            "prompt": prompt,
        }

    judge = call_ollama_judge(model, prompt)
    judge_pass = judge["verdict"] == "PASS"
    agreement = factual_pass == judge_pass

    return {
        **item,
        "factual_pass": factual_pass,
        "judge_verdict": judge["verdict"],
        "judge_pass": judge_pass,
        "judge_reason": judge["reason"],
        "agreement": agreement,
    }


def print_console_report(rows: list[dict], title: str, model: str, dry_run: bool) -> None:
    print(title)
    print("=" * 70)
    if dry_run:
        print("Mode: DRY-RUN (prompts only, no Ollama calls)")
    else:
        print(f"Model: {model}")
    print()

    factual_ok = sum(1 for r in rows if r["factual_pass"])
    print(f"Factual PASS: {factual_ok}/{len(rows)}")

    if not dry_run:
        judge_ok = sum(1 for r in rows if r["judge_pass"])
        agree = sum(1 for r in rows if r["agreement"])
        print(f"Judge PASS:   {judge_ok}/{len(rows)}")
        print(f"Agreement:    {agree}/{len(rows)} ({100 * agree / len(rows):.0f}%)")
    print()

    for r in rows:
        f = "PASS" if r["factual_pass"] else "FAIL"
        print(f"[{r['scenario']}] {r['id']}")
        print(f"  Text: {r['text']}")
        print(f"  Factual: {f}")
        if dry_run:
            print("  --- Judge prompt ---")
            print(r["prompt"])
            print("  --- end prompt ---")
        else:
            j = r["judge_verdict"]
            agree = "yes" if r["agreement"] else "NO"
            print(f"  Judge: {j} — {r['judge_reason']}")
            print(f"  Agreement: {agree}")
        print()


def save_html(rows: list[dict], path: Path, title: str, model: str, dry_run: bool) -> None:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    factual_ok = sum(1 for r in rows if r["factual_pass"])

    if dry_run:
        judge_ok = 0
        agree = 0
        agree_pct = "N/A"
    else:
        judge_ok = sum(1 for r in rows if r["judge_pass"])
        agree = sum(1 for r in rows if r["agreement"])
        agree_pct = f"{100 * agree / len(rows):.0f}%"

    body_rows = []
    for r in rows:
        if dry_run:
            cls = "ok" if r["factual_pass"] else "fail"
        elif r["agreement"]:
            cls = "ok"
        elif r["factual_pass"] and not r["judge_pass"]:
            cls = "gap"
        elif not r["factual_pass"] and r["judge_pass"]:
            cls = "disagree"
        else:
            cls = "fail"

        judge_cell = "DRY-RUN" if dry_run else r["judge_verdict"]
        agree_cell = "—" if dry_run else ("yes" if r["agreement"] else "no")

        body_rows.append(
            f"""<tr class="{cls}">
<td>{r['scenario']}</td><td>{r['id']}</td><td>{r['text']}</td>
<td>{'PASS' if r['factual_pass'] else 'FAIL'}</td>
<td>{judge_cell}</td>
<td>{r['judge_reason']}</td>
<td>{agree_cell}</td>
</tr>"""
        )

    mode_note = "DRY-RUN — judge column skipped" if dry_run else f"Model: {model}"

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
tr.fail {{ background: #f8d7da; }}
tr.gap {{ background: #fff3cd; }}
tr.disagree {{ background: #ffe8cc; }}
</style></head><body>
<h1>{title}</h1>
<p>Generated {generated} — {mode_note}</p>
<div class="summary">
<p><b>Factual PASS:</b> {factual_ok}/{len(rows)}</p>
<p><b>Judge PASS:</b> {judge_ok if not dry_run else 'N/A (dry-run)'}/{len(rows) if not dry_run else len(rows)}</p>
<p><b>Agreement rate:</b> {agree}/{len(rows)} ({agree_pct})</p>
</div>
<table>
<thead><tr>
<th>Scenario</th><th>ID</th><th>Text</th>
<th>Factual</th><th>Judge</th><th>Reason</th><th>Agree</th>
</tr></thead>
<tbody>{''.join(body_rows)}</tbody>
</table>
<p><b>Note:</b> Compare regex factual checks (week01–03) with an LLM judge.
Disagreements deserve human review.</p>
</body></html>"""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="LLM-as-judge with Ollama")
    parser.add_argument(
        "--retail",
        action="store_true",
        help="Use retailco-day1-practice data instead of banking portfolio",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Ollama model name (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Max candidates to evaluate (default: 5)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Evaluate all candidates (ignore --limit)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print judge prompts only; no Ollama API calls",
    )
    args = parser.parse_args()

    if args.retail:
        scenarios = load_json(RETAIL_ROOT / "golden_scenarios.json")
        candidates = load_json(RETAIL_ROOT / "candidates.json")
        domain = "retail"
        title = "LLM judge — RetailCo Day 1"
        html_name = "llm_judge_retailco.html"
    else:
        scenarios = load_json(PORTFOLIO_ROOT / "data" / "golden_scenarios.json")
        candidates = load_json(PORTFOLIO_ROOT / "data" / "candidates.json")
        domain = "banking"
        title = "LLM judge — Banking portfolio"
        html_name = "llm_judge_banking.html"

    limit = None if args.all else args.limit
    items = collect_candidates(scenarios, candidates, limit)

    if not args.dry_run and not check_ollama_reachable():
        print_ollama_install_help()
        sys.exit(1)

    rows = [evaluate_item(item, domain, args.model, args.dry_run) for item in items]

    print_console_report(rows, title, args.model, args.dry_run)

    html_path = REPORTS_DIR / html_name
    save_html(rows, html_path, title, args.model, args.dry_run)
    print(f"HTML report: {html_path}")


if __name__ == "__main__":
    main()
