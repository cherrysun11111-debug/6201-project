# Evals Explainer

## Evaluation Goals

The evaluation checks whether the system can prioritize complaint risk better than a simple keyword rule baseline. It also checks whether the model is too dependent on shortcut words and whether abstention catches uncertain cases.

## Main Metric

The primary metric is macro F1 across `low`, `medium`, and `high` risk.

Macro F1 is used because all classes matter. A system that only performs well on the majority class would not be useful for support triage.

## Baseline

The non-AI baseline is `src/ecrisk/baseline.py`. It uses keyword rules for terms such as refund, chargeback, fake, sparked, tracking, missing, and support.

## Evaluation Splits

`reports/evaluation.json` contains three main checks:

1. `heldout_synthetic`: test split from the generated 420-row dataset.
2. `challenge_set`: 40 hand-written harder cases.
3. `leakage_probe`: challenge set after masking obvious risk and complaint keywords.

## Current Results

- Synthetic held-out: model macro F1 `1.000`, baseline macro F1 `0.907`.
- Challenge set: model macro F1 `0.675`, baseline macro F1 `0.454`.
- Leakage probe: model macro F1 `0.550`, baseline macro F1 `0.144`.

## Abstention

The model abstains when confidence is below the configured threshold. On the challenge set:

- Abstention count: `3/40`
- Abstention rate: `0.075`
- Abstained cases that would otherwise have been wrong: `2/3`

This supports the responsible-use design: uncertain cases should be routed to human review.

## Interpretation

The synthetic split proves the pipeline works, but it is too clean to stand alone. The challenge set and leakage probe are more honest indicators of project limitations. The model improves over the keyword baseline, but it still needs more realistic data before deployment.

