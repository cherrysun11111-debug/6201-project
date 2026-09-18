from collections import Counter


def confusion_matrix(y_true: list[str], y_pred: list[str], labels: tuple[str, ...]) -> dict[str, dict[str, int]]:
    matrix = {actual: {pred: 0 for pred in labels} for actual in labels}
    for actual, pred in zip(y_true, y_pred):
        matrix[actual][pred] += 1
    return matrix


def per_label_scores(y_true: list[str], y_pred: list[str], labels: tuple[str, ...]) -> dict[str, dict[str, float]]:
    scores = {}
    for label in labels:
        tp = sum(1 for a, p in zip(y_true, y_pred) if a == label and p == label)
        fp = sum(1 for a, p in zip(y_true, y_pred) if a != label and p == label)
        fn = sum(1 for a, p in zip(y_true, y_pred) if a == label and p != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        scores[label] = {"precision": precision, "recall": recall, "f1": f1, "support": Counter(y_true)[label]}
    return scores


def macro_f1(y_true: list[str], y_pred: list[str], labels: tuple[str, ...]) -> float:
    scores = per_label_scores(y_true, y_pred, labels)
    return sum(scores[label]["f1"] for label in labels) / len(labels)

