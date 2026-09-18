import json
import math
from collections import Counter, defaultdict
from pathlib import Path

from ecrisk.text import normalize_label, tokenize


LABELS = ("low", "medium", "high")


class NaiveBayesRiskModel:
    def __init__(self) -> None:
        self.label_counts: Counter[str] = Counter()
        self.token_counts: dict[str, Counter[str]] = {label: Counter() for label in LABELS}
        self.total_tokens: Counter[str] = Counter()
        self.vocabulary: set[str] = set()

    def fit(self, texts: list[str], labels: list[str]) -> None:
        if len(texts) != len(labels):
            raise ValueError("texts and labels must have the same length")
        for text, label in zip(texts, labels):
            label = normalize_label(label)
            self.label_counts[label] += 1
            for token in tokenize(text):
                self.token_counts[label][token] += 1
                self.total_tokens[label] += 1
                self.vocabulary.add(token)

    def predict_proba(self, text: str) -> dict[str, float]:
        if not self.label_counts:
            raise ValueError("Model has not been fitted")
        tokens = tokenize(text)
        vocab_size = max(1, len(self.vocabulary))
        total_docs = sum(self.label_counts.values())
        log_scores = {}
        for label in LABELS:
            prior = (self.label_counts[label] + 1) / (total_docs + len(LABELS))
            score = math.log(prior)
            denom = self.total_tokens[label] + vocab_size
            for token in tokens:
                score += math.log((self.token_counts[label][token] + 1) / denom)
            log_scores[label] = score
        max_score = max(log_scores.values())
        exp_scores = {label: math.exp(score - max_score) for label, score in log_scores.items()}
        normalizer = sum(exp_scores.values())
        return {label: exp_scores[label] / normalizer for label in LABELS}

    def predict(self, text: str, abstain_threshold: float = 0.50) -> tuple[str, float, bool]:
        probabilities = self.predict_proba(text)
        label = max(probabilities, key=probabilities.get)
        confidence = probabilities[label]
        return label, confidence, confidence < abstain_threshold

    def top_tokens(self, label: str, limit: int = 5) -> list[str]:
        label = normalize_label(label)
        return [token for token, _ in self.token_counts[label].most_common(limit)]

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "label_counts": dict(self.label_counts),
            "token_counts": {label: dict(counts) for label, counts in self.token_counts.items()},
            "total_tokens": dict(self.total_tokens),
            "vocabulary": sorted(self.vocabulary),
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "NaiveBayesRiskModel":
        payload = json.loads(path.read_text(encoding="utf-8"))
        model = cls()
        model.label_counts = Counter(payload["label_counts"])
        model.token_counts = defaultdict(Counter)
        for label in LABELS:
            model.token_counts[label] = Counter(payload["token_counts"].get(label, {}))
        model.total_tokens = Counter(payload["total_tokens"])
        model.vocabulary = set(payload["vocabulary"])
        return model

