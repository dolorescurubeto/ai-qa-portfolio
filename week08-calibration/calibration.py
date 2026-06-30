"""
Week 4 — Confidence score calibration analysis.

Compares model-reported confidence vs actual pass rate per bin.
"""

from dataclasses import dataclass


@dataclass
class CalibrationSample:
    id: str
    confidence: float
    actual_pass: bool


def sample_pass(record: dict) -> bool:
    return record["citation_pass"] and record["grounding_pass"]


def to_samples(records: list[dict]) -> list[CalibrationSample]:
    return [
        CalibrationSample(
            id=r["id"],
            confidence=r["confidence"],
            actual_pass=sample_pass(r),
        )
        for r in records
    ]


def assign_bin(confidence: float, edges: list[float] | None = None) -> str:
    if edges is None:
        edges = [0.0, 0.5, 0.7, 0.9, 1.01]
    for i in range(len(edges) - 1):
        low, high = edges[i], edges[i + 1]
        if low <= confidence < high:
            return f"{low:.1f}-{min(high, 1.0):.1f}"
    return "unknown"


def calibration_report(
    samples: list[CalibrationSample],
    edges: list[float] | None = None,
) -> list[dict]:
    if edges is None:
        edges = [0.0, 0.5, 0.7, 0.9, 1.01]

    bins: dict[str, list[CalibrationSample]] = {}
    for s in samples:
        label = assign_bin(s.confidence, edges)
        bins.setdefault(label, []).append(s)

    rows = []
    for i in range(len(edges) - 1):
        low, high = edges[i], edges[i + 1]
        label = f"{low:.1f}-{min(high, 1.0):.1f}"
        bucket = bins.get(label, [])
        if not bucket:
            rows.append(
                {
                    "bin": label,
                    "count": 0,
                    "avg_confidence": None,
                    "actual_accuracy": None,
                    "gap": None,
                }
            )
            continue
        avg_conf = sum(s.confidence for s in bucket) / len(bucket)
        accuracy = sum(1 for s in bucket if s.actual_pass) / len(bucket)
        rows.append(
            {
                "bin": label,
                "count": len(bucket),
                "avg_confidence": round(avg_conf, 3),
                "actual_accuracy": round(accuracy, 3),
                "gap": round(abs(avg_conf - accuracy), 3),
            }
        )
    return rows


def expected_calibration_error(rows: list[dict]) -> float:
    """Weighted mean absolute gap between confidence and accuracy per bin."""
    total = sum(r["count"] for r in rows if r["count"])
    if total == 0:
        return 0.0
    error = 0.0
    for r in rows:
        if r["count"] and r["gap"] is not None:
            error += r["gap"] * r["count"]
    return round(error / total, 3)


def high_confidence_miscalibration(rows: list[dict], threshold: float = 0.9) -> list[dict]:
    """Bins at or above threshold where confidence overshoots accuracy."""
    issues = []
    for r in rows:
        if r["count"] == 0 or r["avg_confidence"] is None:
            continue
        low = float(r["bin"].split("-")[0])
        if low >= threshold and r["actual_accuracy"] < r["avg_confidence"]:
            issues.append(r)
    return issues
