# Demo Presentation Script

## 1. Opening

This project is called ComplaintRisk Queue. It helps a small e-commerce support lead decide which customer complaints should be handled first.

## 2. Problem

Start with three examples:

- "Great product and fast delivery."
- "Tracking is late and the courier marked it delivered, but nothing arrived."
- "The adapter sparked and the product looks fake. I want a refund."

The point is that all three are customer messages, but they should not be handled with the same urgency. The third one combines safety, authenticity, and refund risk, so it should move to the front of the queue.

## 3. Repository

Show the GitHub repository. Point out:

- `src/ecrisk`: source code.
- `data`: synthetic dataset and challenge set.
- `reports`: evaluation and batch-analysis outputs.
- `docs`: report, data explainer, evals explainer, product documentation, and demo notes.
- `scripts`: run scripts for the full pipeline and demo.

## 4. Pipeline

Run:

```bash
python scripts/run_pipeline.py
```

Say that this regenerates data, trains the model, runs evaluation, creates batch reports, and runs unit tests. This shows the project is a reproducible workflow, not just a web page.

## 5. Single Review Demo

Open `http://127.0.0.1:8000`.

Paste:

```text
The adapter sparked and the product looks fake. I want a refund.
```

Point out the result:

- Risk: high
- Complaint type: counterfeit_or_safety
- Evidence terms such as sparked, fake, and refund
- SLA: escalate within two hours
- Recommended action and customer reply frame
- Responsible-use note

Say clearly that the tool does not automatically refund, penalize sellers, or remove listings. It only helps a human decide what to inspect first.

## 6. Batch Queue Demo

Open `http://127.0.0.1:8000/queue`.

Explain that this is closer to the real workflow. A support lead normally has a queue of messages, not one isolated review. The page summarizes all analyzed reviews and displays the top-priority cases first.

## 7. Evaluation

Open `reports/evaluation.json`.

Mention:

- Synthetic held-out split: model macro F1 1.000, baseline 0.907.
- Challenge set: model macro F1 0.675, baseline 0.454.
- Leakage probe: model macro F1 0.550, baseline 0.144.
- Abstention: 3 of 40 challenge cases, with 2 of those 3 otherwise wrong.

Explain that the synthetic score proves the pipeline works, but the challenge set and leakage probe are more honest about limitations.

## 8. Close

The current system is not production-ready, mainly because the data is still synthetic. The next step would be real consented or licensed review data, followed by RAG over store policies and optional LLM response drafting. The main contribution of this version is a transparent end-to-end triage workflow with baseline comparison, evaluation, leakage testing, and responsible-use guardrails.

