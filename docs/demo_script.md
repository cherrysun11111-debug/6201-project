# Demo Presentation Script

## 1. Opening

This project helps a small e-commerce support lead prioritize customer complaints. The goal is not to replace customer service agents. The goal is to decide which messages need fast human review.

## 2. Problem

Show three messages:

- "Great product and fast delivery."
- "Tracking is late and the courier marked it delivered, but nothing arrived."
- "The adapter sparked and the product looks fake. I want a refund."

Explain that all are customer messages, but only the third is urgent because it combines safety, authenticity, and refund risk.

## 3. Baseline

Explain the keyword baseline. It is fast and transparent, but brittle. It catches obvious words such as refund or fake, but struggles with paraphrase, typos, and mixed reviews.

## 4. Model And Workflow

Run:

```powershell
$env:PYTHONPATH="src"
python -m ecrisk.evaluate
python -m ecrisk.app
```

Open `http://127.0.0.1:8000`.

## 5. Single Review Demo

Paste:

```text
The adapter sparked and the product looks fake. I want a refund.
```

Point out:

- Risk: high
- Complaint type: counterfeit_or_safety
- Evidence terms
- SLA
- Recommended action
- Responsible-use note

## 6. Batch Queue Demo

Click Priority queue. Show that the system sorts the sample CSV into a triage queue and surfaces high-risk cases first. Explain that this is closer to the real support-lead workflow than a single classifier form.

## 7. Evaluation

Open `reports/evaluation.json`. Mention both scores:

- Synthetic held-out split: model macro F1 1.000, baseline 0.907.
- Challenge set: model macro F1 0.675, baseline 0.454.
- Leakage probe after masking obvious risk keywords: model macro F1 0.550, baseline 0.144.

Explain that the challenge set is intentionally harder and reveals the limitation of synthetic data. Also mention that the leakage probe checks whether the system depends too heavily on shortcut words such as refund, fake, or tracking.

## 8. Responsible Use

State that the tool does not automatically refund, delist, or penalize sellers. High-risk and low-confidence outputs require human confirmation.

## 9. Future Work

Next steps:

- Add real consented or public review data.
- Add RAG over store return and safety policies.
- Add optional LLM drafting with policy citations.
- Track human corrections and retrain.
