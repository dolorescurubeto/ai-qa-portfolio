"""
Week 4 — Long-term drift testing on the golden set.

Simulates a banking chatbot that degrades over time (higher error rate).
Runs factual validation after each simulated "day" and appends results
to drift_results.json. Compares consecutive runs to detect drift.

Usage:
  cd week04-drift
  python drift_test.py                    # single run (10% error rate)
  python drift_test.py --error-rate 0.20  # single run with 20% errors
  python drift_test.py --simulate-days 3  # demo: 3 runs with rising error rate
"""

import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS_FILE = ROOT / "data" / "golden_scenarios.json"
CANDIDATES_FILE = ROOT / "data" / "candidates.json"
RESULTS_FILE = Path(__file__).resolve().parent / "drift_results.json"

sys.path.insert(0, str(ROOT / "week03-metrics"))
from factual import validate_factual  # noqa: E402

DRIFT_THRESHOLD = 10.0  # alert if accuracy drops by 10+ points


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def pick_response(reference: str, candidates: list, error_rate: float) -> str:
    passing = [c for c in candidates if validate_factual(reference, c["text"])["pass"]]
    failing = [c for c in candidates if not validate_factual(reference, c["text"])["pass"]]

    if random.random() < error_rate and failing:
        return random.choice(failing)["text"]
    if passing:
        return random.choice(passing)["text"]
    return reference


def run_test_suite(scenarios: dict, all_candidates: dict, error_rate: float) -> tuple[float, list]:
    results = []
    correct = 0

    for scenario_key, scenario in scenarios.items():
        candidates = all_candidates.get(scenario_key, [])
        if not candidates:
            continue

        reference = scenario["reference"]
        output = pick_response(reference, candidates, error_rate)
        is_correct = validate_factual(reference, output)["pass"]

        results.append(
            {
                "scenario": scenario_key,
                "reference": reference,
                "output": output,
                "correct": is_correct,
            }
        )
        if is_correct:
            correct += 1

    accuracy = correct / len(results) * 100 if results else 0.0
    return accuracy, results


def save_results(accuracy: float, results: list, error_rate: float) -> None:
    run_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "error_rate_simulated": error_rate,
        "accuracy": round(accuracy, 2),
        "passed": sum(1 for r in results if r["correct"]),
        "total": len(results),
        "results": results,
    }

    try:
        history = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        history = []

    history.append(run_data)
    RESULTS_FILE.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")


def detect_drift() -> str | None:
    if not RESULTS_FILE.exists():
        return None

    history = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    if len(history) < 2:
        return "[INFO] Need at least 2 runs to compare drift."

    last = history[-1]["accuracy"]
    prev = history[-2]["accuracy"]
    drop = prev - last

    if drop >= DRIFT_THRESHOLD:
        return f"[DRIFT] Accuracy dropped {drop:.2f} pts ({prev:.2f}% -> {last:.2f}%)"
    if drop <= -DRIFT_THRESHOLD:
        return f"[RECOVERED] Accuracy improved {-drop:.2f} pts ({prev:.2f}% -> {last:.2f}%)"
    return f"[OK] No significant drift vs previous run (last: {last:.2f}%)"


def print_baseline_trend() -> None:
    if not RESULTS_FILE.exists():
        return

    history = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
    if len(history) < 2:
        return

    first = history[0]["accuracy"]
    last = history[-1]["accuracy"]
    change = last - first
    print(f"Baseline trend: {first:.2f}% (day 1) -> {last:.2f}% (latest) = {change:+.2f} pts")
    if first - last >= DRIFT_THRESHOLD:
        print(f"[DRIFT] Model degraded {first - last:.2f} pts vs baseline")


def print_run_summary(accuracy: float, results: list, error_rate: float) -> None:
    passed = sum(1 for r in results if r["correct"])
    print(f"Simulated error rate: {error_rate:.0%}")
    print(f"Accuracy: {accuracy:.2f}% ({passed}/{len(results)} scenarios passed)")
    print()
    for r in results:
        status = "PASS" if r["correct"] else "FAIL"
        print(f"  [{status}] {r['scenario']}")
        print(f"    Output: {r['output']}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Drift test on banking golden set")
    parser.add_argument(
        "--error-rate",
        type=float,
        default=0.10,
        help="Probability the model returns a failing response (default: 0.10)",
    )
    parser.add_argument(
        "--simulate-days",
        type=int,
        default=0,
        help="Run N simulated days with rising error rates (demo mode)",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()

    random.seed(args.seed)
    scenarios = load_json(SCENARIOS_FILE)
    all_candidates = load_json(CANDIDATES_FILE)

    print("WEEK 4 — Drift testing")
    print("=" * 60)

    if args.simulate_days > 0:
        rates = [0.05, 0.25, 0.45][: args.simulate_days]
        if args.simulate_days > 3:
            rates = [0.05 + i * 0.12 for i in range(args.simulate_days)]

        for day, rate in enumerate(rates, start=1):
            print(f"\n--- Simulated day {day} (error rate {rate:.0%}) ---")
            accuracy, results = run_test_suite(scenarios, all_candidates, rate)
            print_run_summary(accuracy, results, rate)
            save_results(accuracy, results, rate)
    else:
        accuracy, results = run_test_suite(scenarios, all_candidates, args.error_rate)
        print_run_summary(accuracy, results, args.error_rate)
        save_results(accuracy, results, args.error_rate)

    drift_report = detect_drift()
    if drift_report:
        print(drift_report)
    if args.simulate_days > 0:
        print_baseline_trend()
    print(f"\nHistory saved: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
