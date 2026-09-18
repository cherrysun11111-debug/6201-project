import argparse
import csv
import random
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "data" / "reviews.csv"


@dataclass(frozen=True)
class Template:
    risk: str
    complaint_type: str
    phrases: tuple[str, ...]
    products: tuple[str, ...]
    impacts: tuple[str, ...]


TEMPLATES = [
    Template(
        "high",
        "refund_dispute",
        (
            "I asked for a refund three times and nobody replied",
            "The seller refused my refund after the item failed",
            "I was charged twice and support keeps closing the ticket",
            "The refund status has been pending for weeks",
        ),
        ("phone charger", "running shoes", "coffee machine", "gaming headset"),
        ("I may file a chargeback", "I need this escalated today", "this feels fraudulent"),
    ),
    Template(
        "high",
        "counterfeit_or_safety",
        (
            "The product looks fake and the serial number is invalid",
            "The battery overheated after one use",
            "The label is different from the listing and may be counterfeit",
            "The adapter sparked when I plugged it in",
        ),
        ("power bank", "skin cream", "baby monitor", "laptop adapter"),
        ("this may be unsafe", "I want the listing investigated", "other buyers should be warned"),
    ),
    Template(
        "medium",
        "damaged_or_wrong_item",
        (
            "The box arrived crushed and the item was cracked",
            "I ordered a black medium but received a white small",
            "The package was missing parts",
            "The screen has scratches although it was sold as new",
        ),
        ("desk lamp", "winter jacket", "tablet case", "air fryer"),
        ("I need a replacement", "I cannot use it as delivered", "please send the correct item"),
    ),
    Template(
        "medium",
        "delivery_delay",
        (
            "Delivery is five days late with no useful update",
            "The tracking page has not moved since last week",
            "The courier marked it delivered but nothing arrived",
            "The promised two day shipping did not happen",
        ),
        ("birthday gift", "printer ink", "kitchen scale", "school bag"),
        ("I needed it this week", "please tell me where it is", "I may cancel the order"),
    ),
    Template(
        "medium",
        "service_failure",
        (
            "Customer service keeps sending copy paste replies",
            "The chat agent ended the conversation before solving it",
            "Support promised a callback but never called",
            "I have repeated the same issue to three agents",
        ),
        ("smart watch", "bookshelf", "vacuum cleaner", "wireless mouse"),
        ("I am frustrated", "please escalate to a human", "the answer does not address my problem"),
    ),
    Template(
        "low",
        "minor_negative_or_no_complaint",
        (
            "The color is slightly different but the product works",
            "Shipping was a little slow but the item arrived fine",
            "The packaging could be better",
            "It is okay for the price",
            "Great product and fast delivery",
            "Works as expected",
        ),
        ("notebook", "water bottle", "phone stand", "yoga mat"),
        ("not a big issue", "I will keep it", "overall acceptable", "happy with the purchase"),
    ),
]


def make_review(template: Template, rng: random.Random) -> str:
    phrase = rng.choice(template.phrases)
    product = rng.choice(template.products)
    impact = rng.choice(template.impacts)
    order_id = rng.randint(10000, 99999)
    review = f"Order {order_id}: {phrase} for my {product}. {impact}."
    return add_realistic_variation(review, template.risk, rng)


def add_realistic_variation(review: str, risk: str, rng: random.Random) -> str:
    """Add ambiguity so the task is not only keyword matching."""
    prefixes = [
        "I usually like this store, but",
        "Maybe this is a courier issue, but",
        "Not sure who is responsible, but",
        "I waited before writing this review.",
        "This is my second order from you.",
    ]
    suffixes = {
        "high": [
            "I do not want an automated reply.",
            "Please have a real person check this.",
            "This may affect whether I buy again.",
        ],
        "medium": [
            "I can wait if someone gives me a clear update.",
            "It is fixable, but I need a concrete answer.",
            "Please do not send another generic template.",
        ],
        "low": [
            "This is not urgent.",
            "I am mostly leaving feedback for improvement.",
            "No need to replace it unless this happens again.",
        ],
    }
    typos = {
        "refund": "refnd",
        "delivery": "delivry",
        "tracking": "trackng",
        "support": "suport",
        "replacement": "replacment",
    }
    if rng.random() < 0.35:
        review = f"{rng.choice(prefixes)} {review[0].lower()}{review[1:]}"
    if rng.random() < 0.45:
        review = f"{review} {rng.choice(suffixes[risk])}"
    if rng.random() < 0.16:
        for original, typo in typos.items():
            if original in review:
                review = review.replace(original, typo, 1)
                break
    if rng.random() < 0.18 and risk != "low":
        review = f"{review} The product itself is otherwise fine."
    if rng.random() < 0.12 and risk == "low":
        review = f"{review} I am not asking for a refund."
    return review


def generate_rows(count: int, seed: int) -> list[dict[str, str]]:
    rng = random.Random(seed)
    rows = []
    weights = [0.18, 0.12, 0.18, 0.20, 0.12, 0.20]
    for idx in range(1, count + 1):
        template = rng.choices(TEMPLATES, weights=weights, k=1)[0]
        rows.append(
            {
                "id": f"R{idx:04d}",
                "review_text": make_review(template, rng),
                "risk": template.risk,
                "complaint_type": template.complaint_type,
            }
        )
    return rows


def write_csv(rows: list[dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "review_text", "risk", "complaint_type"])
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate reproducible synthetic e-commerce review data.")
    parser.add_argument("--rows", type=int, default=360)
    parser.add_argument("--seed", type=int, default=6201)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    rows = generate_rows(args.rows, args.seed)
    write_csv(rows, args.output)
    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
