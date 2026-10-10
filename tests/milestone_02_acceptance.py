"""Task 1/2 checks and evidence; run with .venv311/bin/python -m tests.milestone_02_acceptance.

Use --report PATH to save a JSON report after successful checks. Repeating this
command in a fresh process provides independent deterministic-regeneration evidence.
"""

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import random
import re
import sys
import unittest

from smoke_tests.runtime import (
    FORBIDDEN_PROCESS_ATTEMPTS, NETWORK_ATTEMPTS, install_offline_audit, prepare_runtime,
)

prepare_runtime()
install_offline_audit()

import dataset  # noqa: E402 — intentionally imported after offline controls

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CATEGORIES = {"Billing", "Technical Issue", "Account Access", "Product Defect", "General Inquiry"}
EXPECTED_STATUSES = {"Open", "In Progress", "Escalated", "Resolved", "Closed"}
FIELD_TYPES = {
    "record_id": str, "category": str, "status": str,
    "resolution_time_hours": int, "days_since_created": int, "escalated": bool,
}
# Independent topic/meaning anchors; headings alone do not satisfy coverage.
TOPICS = {
    "01_ticket_priority.md": ("ticket-priority classification rules", ["P1", "P2", "P3", "P4", "highest priority"]),
    "02_severity_sla.md": ("SLA-by-severity policy", ["15 elapsed minutes", "24 support hours", "72 support hours", "120 support hours"]),
    "03_escalation_matrix.md": ("escalation matrix", ["billing specialist", "technical specialist", "account-security specialist", "duty incident lead", "handoff"]),
    "04_refund_compensation.md": ("refund/compensation policy", ["duplicate charge", "original payment method", "5 to 7 business days", "INR 200", "approval"]),
    "05_communication_channels.md": ("customer-communication-channel policy", ["in-app support", "email", "consents", "account-verification", "password"]),
    "06_business_hours.md": ("business-hours/holiday-support policy", ["09:00 to 18:00", "Asia/Kolkata", "holidays", "on-call", "pause"]),
    "07_repeat_complaints.md": ("repeat-complaint-handling policy", ["30 days", "reopen", "root cause", "second repeat"]),
    "08_service_credit.md": ("service-credit policy", ["noncash", "INR 150", "30 days", "cannot be transferred", "approval"]),
    "09_feedback.md": ("feedback-collection process", ["optional", "1 to 5", "48 hours", "supervisor review", "aggregated"]),
    "10_vip_handling.md": ("VIP-customer handling policy", ["verified account flag", "named support owner", "4 support hours", "does not change safety priority"]),
    "11_outage_communication.md": ("outage-communication protocol", ["incident record", "15 elapsed minutes", "30 elapsed minutes", "no unconfirmed", "recovery"]),
    "12_ticket_retention.md": ("data-retention policy for tickets", ["180 days", "delete identifying details", "masked phone", "legal hold", "30 days"]),
}


def policy_report() -> list[dict]:
    report = []
    for filename, (topic, anchors) in TOPICS.items():
        path = ROOT / "knowledge_base" / filename
        lines = path.read_text(encoding="utf-8").splitlines()
        body = " ".join(line.strip() for line in lines if line.strip() and not line.startswith("#"))
        # These policies use no dotted abbreviations or decimal amounts.
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", body) if s.strip()]
        report.append({"topic": topic, "path": path.relative_to(ROOT).as_posix(),
                       "sentence_count": len(sentences), "sentences": sentences,
                       "required_content_anchors": anchors,
                       "content_anchors_present": all(a.casefold() in body.casefold() for a in anchors),
                       "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    return report


class MilestoneTwoTests(unittest.TestCase):
    def test_01_fields_types_ids_and_ranges(self):
        tickets = dataset.SUPPORT_TICKETS
        self.assertIs(type(tickets), list)
        self.assertGreaterEqual(len(tickets), 40)
        self.assertEqual(len({t["record_id"] for t in tickets}), len(tickets))
        for ticket in tickets:
            for field, expected in FIELD_TYPES.items():
                self.assertIs(type(ticket[field]), expected, field)
            self.assertRegex(ticket["record_id"], r"^OLA-\d{4}$")
            self.assertIn(ticket["category"], EXPECTED_CATEGORIES)
            self.assertIn(ticket["status"], EXPECTED_STATUSES)
            self.assertTrue(1 <= ticket["resolution_time_hours"] <= 168)
            self.assertTrue(0 <= ticket["days_since_created"] <= 30)
            self.assertIs(type(ticket["amount_inr"]), int)
            self.assertTrue(0 <= ticket["amount_inr"] <= 5000)
            self.assertEqual(ticket["escalated"], ticket["status"] == "Escalated")
            if ticket["status"] in ("Closed", "Resolved"):
                self.assertGreaterEqual(ticket["days_since_created"] * 24, ticket["resolution_time_hours"])

    def test_02_distribution_acceptance(self):
        tickets = dataset.SUPPORT_TICKETS
        categories = Counter(t["category"] for t in tickets)
        statuses = Counter(t["status"] for t in tickets)
        for category in EXPECTED_CATEGORIES:
            self.assertGreaterEqual(categories[category], 3)
        for status in EXPECTED_STATUSES:
            self.assertGreaterEqual(statuses[status], 1)
        percentage = 100 * sum(t["escalated"] for t in tickets) / len(tickets)
        self.assertTrue(10 <= percentage <= 30)
        self.assertEqual(dataset.validate_tickets(tickets)["escalated_percentage"], percentage)

    def test_03_regeneration_and_global_rng_isolation(self):
        global_state = random.getstate()
        try:
            first = dataset.generate_tickets(seed=42)
            random.seed(917)
            state_before = random.getstate()
            second = dataset.generate_tickets(seed=42)
            self.assertEqual(random.getstate(), state_before)
            self.assertEqual(first, second)
            self.assertEqual(first, dataset.SUPPORT_TICKETS)
            self.assertIsNot(first, second)
            self.assertIsNot(first[0], second[0])
            self.assertNotEqual(first, dataset.generate_tickets(seed=43))
        finally:
            random.setstate(global_state)

    def test_04_invalid_fields_and_ranges_rejected(self):
        # Mutated copies are negative test fixtures, never source record repairs.
        mutations = [("days_since_created", True), ("days_since_created", -1),
                     ("days_since_created", 31), ("escalated", 1),
                     ("resolution_time_hours", 169), ("resolution_time_hours", 0),
                     ("amount_inr", 5001), ("category", "Unknown"), ("status", "Unknown")]
        for field, value in mutations:
            with self.subTest(field=field, value=value):
                tickets = deepcopy(dataset.SUPPORT_TICKETS)
                tickets[0][field] = value
                with self.assertRaises(ValueError):
                    dataset.validate_tickets(tickets)
        tickets = deepcopy(dataset.SUPPORT_TICKETS)
        del tickets[0]["record_id"]
        with self.assertRaisesRegex(ValueError, "record_id"):
            dataset.validate_tickets(tickets)
        tickets = deepcopy(dataset.SUPPORT_TICKETS)
        tickets[1]["record_id"] = tickets[0]["record_id"]
        with self.assertRaisesRegex(ValueError, "unique"):
            dataset.validate_tickets(tickets)
        with self.assertRaisesRegex(ValueError, "at least 40"):
            dataset.validate_tickets(dataset.SUPPORT_TICKETS[:39])

    def test_05_bad_distributions_rejected(self):
        tickets = deepcopy(dataset.SUPPORT_TICKETS)
        for t in tickets:
            t["category"] = "Billing"
            t["resolution_time_hours"] = 24
        with self.assertRaisesRegex(ValueError, "category"):
            dataset.validate_tickets(tickets)
        tickets = deepcopy(dataset.SUPPORT_TICKETS)
        for t in tickets:
            if t["status"] == "Closed":
                t["status"] = "Resolved"
        with self.assertRaisesRegex(ValueError, "status"):
            dataset.validate_tickets(tickets)
        for target in ("low", "high"):
            tickets = deepcopy(dataset.SUPPORT_TICKETS)
            preserved_statuses = set()
            for t in tickets:
                if t["status"] not in preserved_statuses:
                    preserved_statuses.add(t["status"])
                    continue
                if target == "high":
                    t["status"] = "Escalated"
                    t["escalated"] = True
                elif t["status"] == "Escalated":
                    t["status"] = "Open"
                    t["escalated"] = False
            with self.subTest(escalation=target), self.assertRaisesRegex(ValueError, "percentage"):
                dataset.validate_tickets(tickets)

    def test_06_policy_topics_sentences_and_content(self):
        files = {p.name for p in (ROOT / "knowledge_base").glob("*.md")}
        self.assertGreaterEqual(len(files), 12)
        self.assertTrue(set(TOPICS).issubset(files))
        for entry in policy_report():
            with self.subTest(topic=entry["topic"]):
                self.assertTrue(2 <= entry["sentence_count"] <= 5)
                self.assertTrue(entry["content_anchors_present"])
                for sentence in entry["sentences"]:
                    self.assertTrue(sentence.endswith((".", "!", "?")))
                    self.assertGreater(len(sentence.split()), 5)

    def test_07_documented_design_and_preserved_statement(self):
        self.assertEqual(sys.version_info[:2], (3, 11))
        self.assertEqual(Path(sys.prefix).name, ".venv311")
        self.assertEqual(hashlib.sha256((ROOT / "Problem_Statement.md").read_bytes()).hexdigest(),
                         "81e2d0ca4499c1865cf8c9fee41c1ce90825440f3eb7f91593c4c2ab9d89dbd6")
        readme = (ROOT / "README.md").read_text()
        for detail in ("**42**", "**60**", "20, 20, 20, 20, 20", "20, 25, 20, 20, 15", "1–168", "0–5000", "Range rationale", "fabricated capstone policies"):
            self.assertIn(detail, readme)

    def test_08_no_network_or_child_process_attempts(self):
        self.assertEqual(NETWORK_ATTEMPTS, [])
        self.assertEqual(FORBIDDEN_PROCESS_ATTEMPTS, [])


def make_report(result) -> dict:
    tickets = dataset.SUPPORT_TICKETS
    report = dataset.validate_tickets(tickets)
    report.update({
        "python_version": sys.version.split()[0],
        "seed": dataset.SEED,
        "category_weights": dict(zip(dataset.CATEGORIES, dataset.CATEGORY_WEIGHTS)),
        "status_weights": dict(zip(dataset.STATUSES, dataset.STATUS_WEIGHTS)),
        "field_types_observed": {f: sorted({type(t[f]).__name__ for t in tickets}) for f in (*FIELD_TYPES, "amount_inr")},
        "observed_ranges": {f: {"minimum": min(t[f] for t in tickets), "maximum": max(t[f] for t in tickets)} for f in ("resolution_time_hours", "days_since_created", "amount_inr")},
        "regeneration_sha256": dataset.dataset_fingerprint(dataset.generate_tickets()),
        "all_records": tickets,
        "policies": policy_report(),
        "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
        "network_attempts": NETWORK_ATTEMPTS, "child_process_attempts": FORBIDDEN_PROCESS_ATTEMPTS,
        "result": "PASSED",
    })
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(MilestoneTwoTests))
    if not result.wasSuccessful():
        sys.exit(1)
    report = make_report(result)
    if args.report:
        path = args.report.resolve()
        if not path.is_relative_to(ROOT):
            parser.error("Evidence report must be inside the project")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"REPORT {path.relative_to(ROOT).as_posix()}")
    print(json.dumps({k: report[k] for k in ("record_count", "category_counts", "status_counts", "escalated_percentage", "sha256", "tests_run", "result")}, indent=2, sort_keys=True))
