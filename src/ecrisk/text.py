import re


TOKEN_RE = re.compile(r"[a-z0-9']+")


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from",
    "had", "has", "have", "i", "in", "is", "it", "my", "of", "on", "or",
    "so", "that", "the", "this", "to", "was", "we", "were", "with", "you",
}


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(text.lower()) if t not in STOPWORDS]


def normalize_label(label: str) -> str:
    label = label.strip().lower()
    if label not in {"low", "medium", "high"}:
        raise ValueError(f"Unknown risk label: {label}")
    return label

