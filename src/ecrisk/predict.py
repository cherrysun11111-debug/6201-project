import argparse
import json
from pathlib import Path

from ecrisk.baseline import explain as baseline_explain
from ecrisk.baseline import predict_complaint_type
from ecrisk.model import NaiveBayesRiskModel
from ecrisk.train import DEFAULT_MODEL


def classify(text: str, model_path: Path = DEFAULT_MODEL) -> dict[str, object]:
    model = NaiveBayesRiskModel.load(model_path)
    label, confidence, abstain = model.predict(text)
    probabilities = model.predict_proba(text)
    complaint_type, evidence_terms = predict_complaint_type(text)
    return {
        "risk": label,
        "confidence": round(confidence, 3),
        "abstain": abstain,
        "complaint_type": complaint_type,
        "evidence_terms": evidence_terms,
        "probabilities": {k: round(v, 3) for k, v in probabilities.items()},
        "baseline_explanation": baseline_explain(text),
        "top_model_tokens_for_risk": model.top_tokens(label),
        "recommended_action": action_for(label, abstain),
        "sla": sla_for(label, abstain),
        "customer_reply_frame": reply_frame_for(label, complaint_type, abstain),
        "responsible_use_note": (
            "This is a triage aid. A human should confirm high-risk, safety, refund, or low-confidence cases."
        ),
    }


def action_for(label: str, abstain: bool) -> str:
    if abstain:
        return "Ask a human reviewer to inspect this case because model confidence is below threshold."
    if label == "high":
        return "Escalate to a human agent, prioritize refund/safety checks, and respond within SLA."
    if label == "medium":
        return "Route to support queue and prepare replacement, delivery, or service recovery response."
    return "Handle with standard response flow and monitor for repeated complaints."


def sla_for(label: str, abstain: bool) -> str:
    if abstain:
        return "Human review before customer action"
    if label == "high":
        return "Escalate within 2 hours"
    if label == "medium":
        return "Respond within 1 business day"
    return "Standard queue"


def reply_frame_for(label: str, complaint_type: str, abstain: bool) -> str:
    if abstain:
        return "Acknowledge the issue and tell the customer a specialist will review the case."
    if label == "high":
        return "Apologize, confirm order details, avoid blame, and route to refund or safety investigation."
    if complaint_type == "delivery_delay":
        return "Acknowledge the delay, check tracking, and offer a clear next update time."
    if complaint_type == "damaged_or_wrong_item":
        return "Ask for photo/order confirmation and offer replacement or return instructions."
    if complaint_type == "service_failure":
        return "Acknowledge repeated contact and move the case to a human support owner."
    return "Use a concise standard response and monitor whether the customer follows up."


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict complaint risk for one review.")
    parser.add_argument("text")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    args = parser.parse_args()
    print(json.dumps(classify(args.text, args.model), indent=2))


if __name__ == "__main__":
    main()
