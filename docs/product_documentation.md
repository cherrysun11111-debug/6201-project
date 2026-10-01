# Product Documentation

## Persona

Mei is a support lead at a small e-commerce store. She starts the day with a queue of customer reviews and support messages. She needs to decide which cases must be escalated before normal tickets.

## Input

The system accepts:

- A single review/support message in the web demo.
- A CSV batch of reviews using `data/reviews.csv` and `src/ecrisk/batch.py`.

## Output

For a single review, the system returns:

- Risk label: `low`, `medium`, or `high`
- Confidence
- Complaint type
- Evidence terms
- SLA guidance
- Recommended action
- Customer reply frame
- Responsible-use note

For batch analysis, the system returns:

- Risk distribution
- Complaint type distribution
- Top-priority reviews
- Batch CSV output in `reports/batch_analysis.csv`
- Batch summary in `reports/batch_summary.json`

## High-Level Architecture

```text
Customer review text / CSV batch
        |
        v
Text tokenization and normalization
        |
        +--------------------------+
        |                          |
        v                          v
Keyword baseline             Naive Bayes model
        |                          |
        +------------+-------------+
                     |
                     v
Risk label + confidence
                     |
                     v
Rule layer: complaint type, evidence terms, SLA, abstention, human review guardrails
                     |
                     v
Single-review web result OR batch priority queue
                     |
                     v
Evaluation reports: baseline comparison, challenge set, leakage probe, abstention metrics
```

## External Intelligence

The current implementation does not call an external LLM or hosted AI service. This is intentional: the decision path is local, auditable, and reproducible. A future version may rent an LLM/RAG layer for policy-grounded response drafting, while keeping risk classification local.

## Metrics Targeted

- Primary metric: macro F1 across low, medium, and high risk.
- Baseline comparison: keyword classifier.
- Responsible-use metric: abstention count/rate and whether abstained cases would otherwise have been wrong.
- Leakage check: performance after masking obvious risk keywords.

## Metrics Reached

- Synthetic held-out: model macro F1 `1.000`, baseline `0.907`.
- Challenge set: model macro F1 `0.675`, baseline `0.454`.
- Leakage probe: model macro F1 `0.550`, baseline `0.144`.
- Challenge-set abstention: `3/40`, with `2/3` abstentions catching cases that would otherwise have been wrong.

