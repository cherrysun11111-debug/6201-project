import argparse
import json
from pathlib import Path

from ecrisk.baseline import predict_risk as baseline_predict
from ecrisk.metrics import confusion_matrix, macro_f1, per_label_scores
from ecrisk.model import LABELS, NaiveBayesRiskModel
from ecrisk.train import DEFAULT_DATA, DEFAULT_MODEL, read_rows, split_rows


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = ROOT / "reports" / "evaluation.json"
DEFAULT_CHALLENGE = ROOT / "data" / "challenge_reviews.csv"


def evaluate_split(rows: list[dict[str, str]], model: NaiveBayesRiskModel) -> dict[str, object]:
    y_true = [r["risk"] for r in rows]
    baseline_pred = [baseline_predict(r["review_text"]) for r in rows]
    model_results = [model.predict(r["review_text"]) for r in rows]
    model_pred = [label for label, _confidence, abstain in model_results]
    abstentions = [result for result in model_results if result[2]]
    return {
        "rows": len(rows),
        "baseline": {
            "macro_f1": macro_f1(y_true, baseline_pred, LABELS),
            "per_label": per_label_scores(y_true, baseline_pred, LABELS),
            "confusion_matrix": confusion_matrix(y_true, baseline_pred, LABELS),
        },
        "model": {
            "macro_f1": macro_f1(y_true, model_pred, LABELS),
            "per_label": per_label_scores(y_true, model_pred, LABELS),
            "confusion_matrix": confusion_matrix(y_true, model_pred, LABELS),
            "abstention_rate": len(abstentions) / len(rows) if rows else 0.0,
        },
    }


def evaluate(
    data_path: Path = DEFAULT_DATA,
    model_path: Path = DEFAULT_MODEL,
    report_path: Path = DEFAULT_REPORT,
    challenge_path: Path = DEFAULT_CHALLENGE,
):
    rows = read_rows(data_path)
    _, test_rows = split_rows(rows)
    model = NaiveBayesRiskModel.load(model_path)
    heldout = evaluate_split(test_rows, model)
    report = {
        "dataset": str(data_path),
        "labels": list(LABELS),
        "heldout_synthetic": heldout,
    }
    heldout["model"]["beats_baseline_by"] = heldout["model"]["macro_f1"] - heldout["baseline"]["macro_f1"]
    if challenge_path.exists():
        challenge = evaluate_split(read_rows(challenge_path), model)
        challenge["model"]["beats_baseline_by"] = (
            challenge["model"]["macro_f1"] - challenge["baseline"]["macro_f1"]
        )
        report["challenge_set"] = {
            "dataset": str(challenge_path),
            **challenge,
            "note": "Hand-written ambiguous cases used to expose synthetic-data ceiling.",
        }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate baseline and model.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--challenge", type=Path, default=DEFAULT_CHALLENGE)
    args = parser.parse_args()
    report = evaluate(args.data, args.model, args.report, args.challenge)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
