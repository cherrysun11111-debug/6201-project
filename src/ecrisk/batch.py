import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from ecrisk.predict import classify


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "data" / "reviews.csv"
DEFAULT_OUTPUT = ROOT / "reports" / "batch_analysis.csv"
DEFAULT_SUMMARY = ROOT / "reports" / "batch_summary.json"
RISK_ORDER = {"high": 0, "medium": 1, "low": 2}


def read_reviews(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return []
    if "review_text" not in rows[0]:
        raise ValueError("Input CSV must contain a review_text column")
    return rows


def analyze_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    analyzed = []
    for row in rows:
        result = classify(row["review_text"])
        analyzed.append(
            {
                **row,
                "predicted_risk": str(result["risk"]),
                "confidence": str(result["confidence"]),
                "abstain": str(result["abstain"]),
                "complaint_type": str(result["complaint_type"]),
                "evidence_terms": ", ".join(result["evidence_terms"]),
                "sla": str(result["sla"]),
                "recommended_action": str(result["recommended_action"]),
            }
        )
    return sorted(
        analyzed,
        key=lambda r: (RISK_ORDER.get(r["predicted_risk"], 9), r["complaint_type"], r.get("id", "")),
    )


def summarize(rows: list[dict[str, str]]) -> dict[str, object]:
    risk_counts = Counter(r["predicted_risk"] for r in rows)
    type_counts = Counter(r["complaint_type"] for r in rows)
    abstentions = sum(1 for r in rows if r["abstain"] == "True")
    top_queue = [
        {
            "id": r.get("id", ""),
            "predicted_risk": r["predicted_risk"],
            "complaint_type": r["complaint_type"],
            "sla": r["sla"],
            "review_text": r["review_text"],
        }
        for r in rows[:10]
    ]
    return {
        "total_reviews": len(rows),
        "risk_counts": dict(risk_counts),
        "complaint_type_counts": dict(type_counts),
        "abstention_count": abstentions,
        "top_priority_queue": top_queue,
    }


def write_csv(rows: list[dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        output.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a CSV of e-commerce reviews.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    args = parser.parse_args()
    rows = analyze_rows(read_reviews(args.input))
    write_csv(rows, args.output)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summarize(rows), indent=2), encoding="utf-8")
    print(f"Wrote {len(rows)} analyzed rows to {args.output}")
    print(f"Wrote summary to {args.summary}")


if __name__ == "__main__":
    main()
