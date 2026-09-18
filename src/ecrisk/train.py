import argparse
import csv
import random
from pathlib import Path

from ecrisk.model import NaiveBayesRiskModel


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA = ROOT / "data" / "reviews.csv"
DEFAULT_MODEL = ROOT / "models" / "risk_model.json"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def split_rows(rows: list[dict[str, str]], seed: int = 6201, test_size: float = 0.25):
    rows = list(rows)
    random.Random(seed).shuffle(rows)
    cut = int(len(rows) * (1 - test_size))
    return rows[:cut], rows[cut:]


def train_model(data_path: Path = DEFAULT_DATA, model_path: Path = DEFAULT_MODEL) -> NaiveBayesRiskModel:
    rows = read_rows(data_path)
    train_rows, _ = split_rows(rows)
    model = NaiveBayesRiskModel()
    model.fit([r["review_text"] for r in train_rows], [r["risk"] for r in train_rows])
    model.save(model_path)
    return model


def main() -> None:
    parser = argparse.ArgumentParser(description="Train complaint risk model.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    args = parser.parse_args()
    train_model(args.data, args.model)
    print(f"Saved model to {args.model}")


if __name__ == "__main__":
    main()

