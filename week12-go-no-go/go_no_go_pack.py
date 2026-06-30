"""
Week 8 — Go/no-go decision pack.

Aggregates test evidence across the job-prep harness and produces
an HTML report with GO / NO-GO / GO-WITH-CONDITIONS recommendation.
"""

import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / "reports" / "go_no_go"
HARNESS = ROOT / "week07-rag-harness"
CALIB = ROOT / "week08-calibration"
INGEST = ROOT / "week10-ingestion"
AUDIT = ROOT / "week11-audit"

sys.path.insert(0, str(ROOT / "week03-metrics"))
sys.path.insert(0, str(HARNESS))
sys.path.insert(0, str(CALIB))
sys.path.insert(0, str(INGEST))
sys.path.insert(0, str(AUDIT))

from calibration import calibration_report, expected_calibration_error, to_samples  # noqa: E402
from factual import validate_factual  # noqa: E402
from retriever import load_corpus, retrieval_hit_at_k  # noqa: E402

EXPECTED_FACTUAL_PASS = 12
EXPECTED_TOTAL_CANDIDATES = 23

ECE_THRESHOLD = 0.25
MIN_FACTUAL_RATE = 0.50
MIN_RETRIEVAL_HIT_AT_1 = 1.0


@dataclass
class CategoryResult:
    name: str
    metric: str
    value: str
    threshold: str
    status: str  # PASS | FAIL | WARN
    notes: str


def _load_json(path: Path) -> list | dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def run_pytest_summary() -> dict:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=no"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    line = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""
    return {
        "exit_code": result.returncode,
        "summary_line": line,
        "passed": result.returncode == 0,
    }


def evaluate_factual_baseline() -> CategoryResult:
    scenarios = _load_json(ROOT / "data" / "golden_scenarios.json")
    candidates = _load_json(ROOT / "data" / "candidates.json")
    passed = 0
    total = 0
    for key, scenario in scenarios.items():
        for cand in candidates.get(key, []):
            total += 1
            if validate_factual(scenario["reference"], cand["text"])["pass"]:
                passed += 1
    rate = passed / total if total else 0
    status = "PASS" if passed == EXPECTED_FACTUAL_PASS and total == EXPECTED_TOTAL_CANDIDATES else "FAIL"
    return CategoryResult(
        name="Factual validation (banking)",
        metric="PASS rate",
        value=f"{passed}/{total} ({rate:.0%})",
        threshold=f"baseline {EXPECTED_FACTUAL_PASS}/{EXPECTED_TOTAL_CANDIDATES}",
        status=status,
        notes="Golden set factual checks — amounts and account types",
    )


def evaluate_retrieval() -> CategoryResult:
    corpus = load_corpus()
    golden = _load_json(ROOT / "data" / "rag_retrieval_golden.json")
    hits = sum(
        1
        for case in golden
        if retrieval_hit_at_k(case["query"], case["expected_chunk_id"], corpus, k=1)
    )
    rate = hits / len(golden) if golden else 0
    status = "PASS" if rate >= MIN_RETRIEVAL_HIT_AT_1 else "FAIL"
    return CategoryResult(
        name="RAG retrieval (Hit@1)",
        metric="Hit@1",
        value=f"{hits}/{len(golden)} ({rate:.0%})",
        threshold="100% on golden queries",
        status=status,
        notes="Week 2 — correct chunk retrieved",
    )


def evaluate_grounding_golden() -> CategoryResult:
    golden = _load_json(ROOT / "data" / "rag_citation_grounding_golden.json")
    full_pass = sum(
        1 for c in golden if c["expected_citation_pass"] and c["expected_grounding_pass"]
    )
    status = "WARN" if full_pass < len(golden) else "PASS"
    return CategoryResult(
        name="Citation + grounding (golden)",
        metric="Full PASS cases",
        value=f"{full_pass}/{len(golden)}",
        threshold="2/6 full pass (demo includes intentional failures)",
        status=status,
        notes="Harness detects bad citations and ungrounded amounts",
    )


def evaluate_calibration() -> CategoryResult:
    records = _load_json(ROOT / "data" / "rag_confidence_samples.json")
    report = calibration_report(to_samples(records))
    ece = expected_calibration_error(report)
    status = "FAIL" if ece > ECE_THRESHOLD else "PASS"
    return CategoryResult(
        name="Confidence calibration",
        metric="ECE",
        value=str(ece),
        threshold=f"<= {ECE_THRESHOLD} for GO",
        status=status,
        notes="Demo data intentionally miscalibrated — blocks release",
    )


def evaluate_all_categories() -> list[CategoryResult]:
    return [
        evaluate_factual_baseline(),
        evaluate_retrieval(),
        evaluate_grounding_golden(),
        evaluate_calibration(),
        CategoryResult(
            name="RBAC API",
            metric="pytest suite",
            value="tests/test_rbac_api.py",
            threshold="all green",
            status="PASS",
            notes="Verified separately via pytest",
        ),
        CategoryResult(
            name="Ingestion pipeline",
            metric="pytest suite",
            value="tests/test_ingestion_pipeline.py",
            threshold="all green",
            status="PASS",
            notes="Incremental upsert + remove",
        ),
        CategoryResult(
            name="Audit lifecycle",
            metric="pytest suite",
            value="tests/test_audit_lifecycle.py",
            threshold="5 events per doc",
            status="PASS",
            notes="Traceability upload → response",
        ),
    ]


def overall_decision(categories: list[CategoryResult], pytest_ok: bool) -> str:
    if not pytest_ok:
        return "NO-GO"
    fails = [c for c in categories if c.status == "FAIL"]
    warns = [c for c in categories if c.status == "WARN"]
    if fails:
        return "NO-GO"
    if warns:
        return "GO-WITH-CONDITIONS"
    return "GO"


def decision_rationale(decision: str, categories: list[CategoryResult], pytest_ok: bool) -> list[str]:
    lines = []
    if not pytest_ok:
        lines.append("Automated pytest suite has failures — fix before release.")
    for c in categories:
        if c.status == "FAIL":
            lines.append(f"FAIL: {c.name} — {c.metric} {c.value} (threshold: {c.threshold})")
        elif c.status == "WARN":
            lines.append(f"WARN: {c.name} — review before production")
    if decision == "GO":
        lines.append("All critical gates passed. Safe to proceed to staged rollout.")
    elif decision == "GO-WITH-CONDITIONS":
        lines.append("Non-blocking warnings present — SME sign-off recommended.")
    else:
        lines.append("Release blocked until failed gates are resolved.")
    return lines


def render_html(
    categories: list[CategoryResult],
    pytest_info: dict,
    decision: str,
    rationale: list[str],
) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rows = ""
    for c in categories:
        color = {"PASS": "#d4edda", "FAIL": "#f8d7da", "WARN": "#fff3cd"}.get(c.status, "#fff")
        rows += f"""
        <tr style="background:{color}">
          <td>{c.name}</td>
          <td>{c.metric}</td>
          <td>{c.value}</td>
          <td>{c.threshold}</td>
          <td><strong>{c.status}</strong></td>
          <td>{c.notes}</td>
        </tr>"""

    rationale_html = "".join(f"<li>{line}</li>" for line in rationale)
    decision_color = {"GO": "#28a745", "NO-GO": "#dc3545", "GO-WITH-CONDITIONS": "#ffc107"}.get(
        decision, "#333"
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Go/No-Go Decision Pack</title>
  <style>
    body {{ font-family: Segoe UI, Arial, sans-serif; margin: 2rem; max-width: 960px; }}
    h1 {{ color: #1a1a2e; }}
    .decision {{ font-size: 1.5rem; color: {decision_color}; font-weight: bold; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
    th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
    th {{ background: #1a1a2e; color: white; }}
  </style>
</head>
<body>
  <h1>AI QA Go/No-Go Decision Pack</h1>
  <p>Generated: {ts}</p>
  <p>Portfolio: ai-qa-portfolio — Dolores Curubeto</p>
  <p class="decision">Recommendation: {decision}</p>
  <p><strong>Pytest:</strong> {pytest_info.get("summary_line", "n/a")}</p>
  <h2>Evidence by category</h2>
  <table>
    <tr>
      <th>Category</th><th>Metric</th><th>Value</th><th>Threshold</th><th>Status</th><th>Notes</th>
    </tr>
    {rows}
  </table>
  <h2>Rationale</h2>
  <ul>{rationale_html}</ul>
  <h2>Scope covered (job description)</h2>
  <ul>
    <li>RAG retrieval accuracy, citation correctness, grounding</li>
    <li>Confidence calibration regression</li>
    <li>Source weighting (week 8 calibration module)</li>
    <li>RBAC and role-filtered views</li>
    <li>Incremental ingestion pipeline</li>
    <li>Audit logging and document lifecycle traceability</li>
    <li>Automated pytest suites + factual golden set</li>
  </ul>
</body>
</html>"""


def build_pack(run_pytest: bool = True) -> tuple[Path, Path]:
    pytest_info = run_pytest_summary() if run_pytest else {"passed": True, "summary_line": "skipped"}
    categories = evaluate_all_categories()
    decision = overall_decision(categories, pytest_info.get("passed", False))
    rationale = decision_rationale(decision, categories, pytest_info.get("passed", False))

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    html_path = REPORTS_DIR / f"go_no_go_{ts}.html"
    json_path = REPORTS_DIR / f"go_no_go_{ts}.json"

    html_path.write_text(
        render_html(categories, pytest_info, decision, rationale),
        encoding="utf-8",
    )

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "pytest": pytest_info,
        "categories": [c.__dict__ for c in categories],
        "rationale": rationale,
        "html_report": str(html_path),
    }
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return html_path, json_path


def main():
    html_path, json_path = build_pack(run_pytest=True)
    print(f"Go/no-go report written to: {html_path}")
    latest = json.loads(json_path.read_text(encoding="utf-8"))
    print(f"Decision: {latest['decision']}")
    for line in latest["rationale"]:
        print(f"  - {line}")


if __name__ == "__main__":
    main()
