from ecrisk.text import tokenize


HIGH_TERMS = {
    "refund", "charged", "chargeback", "fraudulent", "fake", "counterfeit",
    "unsafe", "overheated", "sparked", "investigated", "warned",
}

MEDIUM_TERMS = {
    "late", "tracking", "delivered", "cancel", "crushed", "cracked", "missing",
    "wrong", "replacement", "scratches", "support", "agent", "escalate",
}

COMPLAINT_KEYWORDS = {
    "refund_dispute": {
        "refund", "charged", "chargeback", "pending", "refused", "fraudulent",
    },
    "counterfeit_or_safety": {
        "fake", "counterfeit", "serial", "unsafe", "overheated", "sparked",
        "adapter", "battery", "investigated", "warned",
    },
    "damaged_or_wrong_item": {
        "crushed", "cracked", "wrong", "missing", "scratches", "replacement",
        "received", "correct",
    },
    "delivery_delay": {
        "delivery", "late", "tracking", "courier", "delivered", "shipping",
        "cancel",
    },
    "service_failure": {
        "support", "service", "agent", "chat", "callback", "escalate",
        "conversation", "repeated",
    },
    "minor_negative_or_no_complaint": {
        "slightly", "okay", "acceptable", "great", "works", "happy",
    },
}


def predict_risk(text: str) -> str:
    tokens = set(tokenize(text))
    if tokens & HIGH_TERMS:
        return "high"
    if tokens & MEDIUM_TERMS:
        return "medium"
    return "low"


def explain(text: str) -> str:
    tokens = set(tokenize(text))
    high = sorted(tokens & HIGH_TERMS)
    medium = sorted(tokens & MEDIUM_TERMS)
    if high:
        return f"High risk keyword(s): {', '.join(high)}"
    if medium:
        return f"Medium risk keyword(s): {', '.join(medium)}"
    return "No high or medium risk keyword found"


def predict_complaint_type(text: str) -> tuple[str, list[str]]:
    tokens = set(tokenize(text))
    scored = []
    for complaint_type, keywords in COMPLAINT_KEYWORDS.items():
        matches = sorted(tokens & keywords)
        scored.append((len(matches), complaint_type, matches))
    scored.sort(reverse=True)
    score, complaint_type, matches = scored[0]
    if score == 0:
        return "unknown", []
    return complaint_type, matches
