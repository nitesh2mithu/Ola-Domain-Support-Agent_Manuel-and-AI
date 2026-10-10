"""Fabricated support tickets for the Ola capstone; no real customer data.

Run `.venv311/bin/python dataset.py` for validated counts, or add `--json`
to export the complete deterministic record list to stdout.
"""

import argparse
from collections import Counter
import hashlib
import json
import random

SEED = 42
RECORD_COUNT = 60
CATEGORIES = ("Billing", "Technical Issue", "Account Access", "Product Defect", "General Inquiry")
CATEGORY_WEIGHTS = (20, 20, 20, 20, 20)
STATUSES = ("Open", "In Progress", "Escalated", "Resolved", "Closed")
STATUS_WEIGHTS = (20, 25, 20, 20, 15)
RESOLUTION_RANGES = {
    "Billing": (4, 72),
    "Technical Issue": (4, 120),
    "Account Access": (1, 48),
    "Product Defect": (12, 168),
    "General Inquiry": (1, 24),
}
AMOUNT_RANGE_INR = (0, 5000)


def generate_tickets(seed: int = SEED, count: int = RECORD_COUNT) -> list[dict]:
    """Generate from a local RNG, never modify draws to force acceptance counts.

    resolution_time_hours is a planned total resolution duration, not elapsed
    time or a promise to a user. Resolved/Closed ages are at least that duration.
    escalated records are currently in the Escalated status, not historical flags.
    """
    if type(seed) is not int or type(count) is not int or count < 40:
        raise ValueError("seed must be an integer and count must be an integer >=40")
    rng = random.Random(seed)
    tickets = []
    for number in range(1, count + 1):
        category = rng.choices(CATEGORIES, weights=CATEGORY_WEIGHTS, k=1)[0]
        status = rng.choices(STATUSES, weights=STATUS_WEIGHTS, k=1)[0]
        hours = rng.randint(*RESOLUTION_RANGES[category])
        minimum_age = (hours + 23) // 24 if status in ("Resolved", "Closed") else 0
        tickets.append({
            "record_id": f"OLA-{number:04d}",
            "category": category,
            "status": status,
            "resolution_time_hours": hours,
            "days_since_created": rng.randint(minimum_age, 30),
            "escalated": status == "Escalated",
            "amount_inr": rng.randint(*AMOUNT_RANGE_INR),
        })
    return tickets


def dataset_fingerprint(tickets: list[dict]) -> str:
    """Stable SHA-256 of UTF-8 JSON with sorted keys and compact separators."""
    canonical = json.dumps(tickets, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_tickets(tickets: list[dict]) -> dict:
    """Reject malformed data or a seed whose draws fail official thresholds."""
    if type(tickets) is not list or len(tickets) < 40:
        raise ValueError("Expected a list with at least 40 tickets")
    required_types = {
        "record_id": str, "category": str, "status": str,
        "resolution_time_hours": int, "days_since_created": int,
        "escalated": bool, "amount_inr": int,
    }
    ids = set()
    for ticket in tickets:
        if type(ticket) is not dict:
            raise ValueError("Every ticket must be a dictionary")
        for field, expected in required_types.items():
            if field not in ticket or type(ticket[field]) is not expected:
                raise ValueError(f"Invalid or missing field: {field}")
        if not ticket["record_id"] or ticket["record_id"] in ids:
            raise ValueError("record_id must be nonempty and unique")
        ids.add(ticket["record_id"])
        if ticket["category"] not in CATEGORIES or ticket["status"] not in STATUSES:
            raise ValueError("Unknown category or status")
        low, high = RESOLUTION_RANGES[ticket["category"]]
        if not low <= ticket["resolution_time_hours"] <= high:
            raise ValueError("resolution_time_hours outside category range")
        if not 0 <= ticket["days_since_created"] <= 30:
            raise ValueError("days_since_created outside 0–30")
        if ticket["escalated"] != (ticket["status"] == "Escalated"):
            raise ValueError("Active escalation must match Escalated status")
        if ticket["status"] in ("Resolved", "Closed") and ticket["days_since_created"] * 24 < ticket["resolution_time_hours"]:
            raise ValueError("Terminal ticket age shorter than resolution duration")
        if not AMOUNT_RANGE_INR[0] <= ticket["amount_inr"] <= AMOUNT_RANGE_INR[1]:
            raise ValueError("amount_inr outside configured range")
    categories = Counter(t["category"] for t in tickets)
    statuses = Counter(t["status"] for t in tickets)
    if any(categories[c] < 3 for c in CATEGORIES):
        raise ValueError("Every required category needs at least 3 records")
    if any(statuses[s] < 1 for s in STATUSES):
        raise ValueError("Every required status needs at least 1 record")
    escalated_count = sum(t["escalated"] for t in tickets)
    percentage = 100 * escalated_count / len(tickets)
    if not 10 <= percentage <= 30:
        raise ValueError("Escalated percentage must be between 10 and 30; change seed/weights and regenerate")
    return {
        "record_count": len(tickets),
        "category_counts": {c: categories[c] for c in CATEGORIES},
        "status_counts": {s: statuses[s] for s in STATUSES},
        "escalated_count": escalated_count,
        "escalated_percentage": percentage,
        "sha256": dataset_fingerprint(tickets),
    }


SUPPORT_TICKETS = generate_tickets()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print complete validated dataset")
    args = parser.parse_args()
    report = validate_tickets(SUPPORT_TICKETS)
    print(json.dumps(SUPPORT_TICKETS if args.json else report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
