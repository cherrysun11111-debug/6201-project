# Problem Statement

Small e-commerce sellers receive more reviews and support messages than a small team can manually triage with consistent urgency. The problem is not general sentiment analysis; it is deciding which complaints need fast human attention because they may become refund disputes, delivery escalations, counterfeit claims, product-safety incidents, or visible reputation damage.

The primary user is a marketplace support lead at a small online store. This person starts the day with a queue of customer messages and needs to decide what to handle first, what can wait, and which cases need human confirmation before any customer-facing action.

The proposed system classifies each review or support message into low, medium, or high complaint risk. It also identifies a likely complaint type, extracts evidence terms, assigns an SLA, and suggests the next support action. The system is explicitly not a final decision maker: it must not automatically issue refunds, penalize sellers, remove listings, or make safety decisions without human review.

Success means the tool helps the support lead prioritize risky complaints faster than a keyword-only checklist while remaining transparent enough to audit. The first working version accepts one review and returns one risk label, one complaint type, evidence terms, an action recommendation, and a human-review warning for sensitive cases. The expanded demo also analyzes a CSV of reviews and displays a high-priority queue.

