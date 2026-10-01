# Data Explainer

## Data Files

- `data/reviews.csv`: 420 generated e-commerce review/support-message examples.
- `data/challenge_reviews.csv`: 40 hand-written ambiguous examples.

## Schema

Each row contains:

- `id`: stable row identifier.
- `review_text`: customer review or support message.
- `risk`: ground-truth label, one of `low`, `medium`, or `high`.
- `complaint_type`: ground-truth complaint category.

The main complaint categories are:

- `refund_dispute`
- `counterfeit_or_safety`
- `damaged_or_wrong_item`
- `delivery_delay`
- `service_failure`
- `minor_negative_or_no_complaint`

## How The Synthetic Data Is Generated

`src/ecrisk/data.py` defines templates for each complaint class, then adds controlled variation such as mixed sentiment, extra context, weak signals, and occasional misspellings. The generator is deterministic when called with the seed used in the README:

```bash
python -m ecrisk.data --rows 420 --seed 6201
```

## Why Synthetic Data Is Used

Synthetic data keeps the repository portable and avoids exposing real customer personal data. It also makes the pipeline reproducible for the instructor or TA.

## Known Limitations

Synthetic data can be too clean and may reflect the assumptions of the generator. To make this limitation visible, the project includes `data/challenge_reviews.csv`, a 40-row hand-written set with ambiguous, typo-heavy, and mixed-sentiment reviews.

## Privacy And Access

No real customer data is included. If the project later uses real customer messages, the data must be anonymized and collected from a licensed public source or with consent and a clear purpose notice.

