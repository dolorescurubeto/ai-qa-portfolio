"""
Week 3 — Compare factual validation vs BERTScore on the golden set.

Reads the same JSON files as week02, scores every candidate with:
  - factual pass/fail (amount + account type)
  - BERTScore F1 (semantic similarity)

Flags cases where semantic passes but factual fails — the key Week 3 lesson.

Usage:
  cd week03-metrics
  python compare_all.py

Output:
  Console summary + HTML report in reports/
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from bert_score import score

from factual import validate_factual

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS_FILE = ROOT / "data" / "golden_scenarios.json"
CANDIDATES_FILE = ROOT / "data" / "candidates.json"
REPORTS_DIR = ROOT / "reports"

BERTSCORE_THRESHOLD = 0.85
MODEL_TYPE = "distilroberta-base"


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def bertscore_batch(reference: str, texts: list[str]) -> list[float]:
    refs = [reference] * len(texts)
    _, _, f1 = score(texts, refs, lang="en", model_type=MODEL_TYPE, verbose=False)
    return [round(v.item(), 4) for v in f1]


def evaluate_all(scenarios: dict, all_candidates: dict) -> list[dict]:
    rows = []

    for scenario_key, scenario in scenarios.items():
        candidates = all_candidates.get(scenario_key, [])
        if not candidates:
            continue

        reference = scenario["reference"]
        texts = [c["text"] for c in candidates]
        f1_scores = bertscore_batch(reference, texts)

        for cand, f1 in zip(candidates, f1_scores):
            factual = validate_factual(reference, cand["text"])
            semantic_pass = f1 >= BERTSCORE_THRESHOLD
            factual_pass = factual["pass"]
            gap = semantic_pass and not factual_pass

            rows.append(
                {
                    "scenario": scenario_key,
                    "id": cand["id"],
                    "text": cand["text"],
                    "note": cand.get("note") or cand.get("nota", ""),
                    "factual_pass": factual_pass,
                    "amount_ok": factual["amount_match"],
                    "account_ok": factual["account_type_match"],
                    "bertscore_f1": f1,
                    "semantic_pass": semantic_pass,
                    "gap": gap,
                }
            )

    return rows


def print_console(rows: list[dict]) -> None:
    print("WEEK 3 — Factual vs BERTScore comparison")
    print(f"BERTScore threshold: {BERTSCORE_THRESHOLD} | Model: {MODEL_TYPE}")
    print("=" * 70)

    gaps = [r for r in rows if r["gap"]]
    factual_pass = sum(1 for r in rows if r["factual_pass"])
    semantic_pass = sum(1 for r in rows if r["semantic_pass"])

    print(f"Candidates evaluated: {len(rows)}")
    print(f"Factual PASS:  {factual_pass}/{len(rows)}")
    print(f"Semantic PASS: {semantic_pass}/{len(rows)} (F1 >= {BERTSCORE_THRESHOLD})")
    print(f"Semantic PASS + Factual FAIL (gap): {len(gaps)}")
    print()

    if gaps:
        print("KEY FINDINGS — passes semantic but fails factual:")
        print("-" * 70)
        for r in gaps:
            print(f"  [{r['scenario']}] {r['id']}")
            print(f"    Text: {r['text']}")
            print(f"    BERTScore F1: {r['bertscore_f1']:.4f} | Factual: FAIL")
            print(
                f"    Amount OK: {r['amount_ok']} | Account OK: {r['account_ok']}"
            )
            print()
    else:
        print("No gap cases found at this threshold.")

    print("=" * 70)
    print("Per-scenario breakdown:")
    scenarios_seen = []
    for r in rows:
        if r["scenario"] not in scenarios_seen:
            scenarios_seen.append(r["scenario"])

    for scenario_key in scenarios_seen:
        subset = [r for r in rows if r["scenario"] == scenario_key]
        f_ok = sum(1 for r in subset if r["factual_pass"])
        s_ok = sum(1 for r in subset if r["semantic_pass"])
        g_ok = sum(1 for r in subset if r["gap"])
        print(
            f"  {scenario_key}: factual {f_ok}/{len(subset)} | "
            f"semantic {s_ok}/{len(subset)} | gaps {g_ok}"
        )


def build_html(rows: list[dict]) -> str:
    gaps = [r for r in rows if r["gap"]]
    factual_pass = sum(1 for r in rows if r["factual_pass"])
    semantic_pass = sum(1 for r in rows if r["semantic_pass"])
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    def row_class(r: dict) -> str:
        if r["gap"]:
            return "gap"
        if r["factual_pass"] and r["semantic_pass"]:
            return "both-pass"
        if not r["factual_pass"] and not r["semantic_pass"]:
            return "both-fail"
        return ""

    table_rows = []
    for r in rows:
        cls = row_class(r)
        factual_cell = "PASS" if r["factual_pass"] else "FAIL"
        semantic_cell = "PASS" if r["semantic_pass"] else "FAIL"
        gap_cell = "YES" if r["gap"] else ""
        table_rows.append(
            f"""<tr class="{cls}">
  <td>{r['scenario']}</td>
  <td>{r['id']}</td>
  <td>{r['text']}</td>
  <td>{factual_cell}</td>
  <td>{r['bertscore_f1']:.4f}</td>
  <td>{semantic_cell}</td>
  <td><strong>{gap_cell}</strong></td>
</tr>"""
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Week 3 — Factual vs Semantic Report</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #1a1a1a; }}
    h1 {{ font-size: 1.5rem; }}
    .summary {{ background: #f4f6f8; padding: 1rem 1.25rem; border-radius: 8px; margin-bottom: 1.5rem; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 0.9rem; }}
    th, td {{ border: 1px solid #ccc; padding: 0.5rem 0.65rem; text-align: left; vertical-align: top; }}
    th {{ background: #2c3e50; color: #fff; }}
    tr.gap {{ background: #fff3cd; }}
    tr.both-pass {{ background: #d4edda; }}
    tr.both-fail {{ background: #f8d7da; }}
    .legend span {{ display: inline-block; padding: 0.2rem 0.5rem; margin-right: 0.5rem; border-radius: 4px; }}
    .legend .gap {{ background: #fff3cd; }}
    .legend .both-pass {{ background: #d4edda; }}
    .legend .both-fail {{ background: #f8d7da; }}
  </style>
</head>
<body>
  <h1>Week 3 — Factual vs BERTScore Report</h1>
  <p>AI QA Portfolio | Generated {generated}</p>

  <div class="summary">
    <p><strong>Candidates:</strong> {len(rows)}</p>
    <p><strong>Factual PASS:</strong> {factual_pass}/{len(rows)}</p>
    <p><strong>Semantic PASS (F1 &ge; {BERTSCORE_THRESHOLD}):</strong> {semantic_pass}/{len(rows)}</p>
    <p><strong>Gap (semantic PASS + factual FAIL):</strong> {len(gaps)}</p>
    <p><strong>Model:</strong> {MODEL_TYPE}</p>
  </div>

  <div class="legend">
    <span class="gap">Gap — dangerous</span>
    <span class="both-pass">Both pass</span>
    <span class="both-fail">Both fail</span>
  </div>

  <table>
    <thead>
      <tr>
        <th>Scenario</th>
        <th>ID</th>
        <th>Text</th>
        <th>Factual</th>
        <th>BERTScore F1</th>
        <th>Semantic</th>
        <th>Gap?</th>
      </tr>
    </thead>
    <tbody>
      {"".join(table_rows)}
    </tbody>
  </table>

  <h2>Why the gap matters</h2>
  <p>
    A response can look semantically similar to the reference (high BERTScore)
    but still contain wrong facts. Banking chatbots need <strong>factual checks</strong>
    in addition to semantic metrics.
  </p>
</body>
</html>"""


def save_html(rows: list[dict]) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = REPORTS_DIR / f"week03_factual_vs_bertscore_{timestamp}.html"
    path.write_text(build_html(rows), encoding="utf-8")
    return path


def main():
    scenarios = load_json(SCENARIOS_FILE)
    all_candidates = load_json(CANDIDATES_FILE)

    print("Loading BERTScore model (first run may take a minute)...")
    rows = evaluate_all(scenarios, all_candidates)
    print_console(rows)

    report_path = save_html(rows)
    print()
    print(f"HTML report saved: {report_path}")


if __name__ == "__main__":
    main()
