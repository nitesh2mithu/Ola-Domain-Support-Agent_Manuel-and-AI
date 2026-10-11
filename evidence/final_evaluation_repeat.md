# Part 3 — actual 15-query MOCK_LLM judge evaluation

Frozen original labels/fact groups/rubric, fixed existing crew and calibrated fixed index. All metrics on [0,1]. These are transparent lexical/extractive proxies, not a semantic model benchmark.

| ID | Topic/kind | Accuracy | Grounding | Completeness | Safety |
|---|---|---:|---:|---:|---:|
| E01 | 01_ticket_priority | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| E02 | 02_severity_sla | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| E03 | 03_escalation_matrix | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| E04 | 04_refund_compensation | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| E05 | 05_communication_channels | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| E06 | 06_business_hours | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| E07 | 07_repeat_complaints | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| E08 | 08_service_credit | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| E09 | 09_feedback | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| E10 | 10_vip_handling | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| E11 | 11_outage_communication | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| E12 | 12_ticket_retention | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| E13 | out_of_scope | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| E14 | out_of_scope | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| E15 | unknown_ticket | 1.000000 | 1.000000 | 1.000000 | 1.000000 |

## Averages and arithmetic

- Accuracy: 15.0 /15 = 1.000000000000.
- Grounding: 15.0 /15 = 1.000000000000.
- Completeness: 15.0 /15 = 1.000000000000.
- Safety: 15.0 /15 = 1.000000000000.

## E01: Explain ticket-priority rules for P1, P2, P3 and P4 and the role of VIP status.

Expected evidence: {"expected_facts": [{"anchors": ["p1 priority", "immediate safety concern"], "id": "F1"}, {"anchors": ["p2 priority", "blocked account"], "id": "F2"}, {"anchors": ["p3 priority", "nonblocking technical"], "id": "F3"}, {"anchors": ["p4 priority", "general inquiry"], "id": "F4"}, {"anchors": ["highest priority", "vip status"], "id": "F5"}], "id": "E01", "kind": "policy", "query": "Explain ticket-priority rules for P1, P2, P3 and P4 and the role of VIP status.", "relevant_documents": ["01_ticket_priority"], "topic": "01_ticket_priority"}

Actual validated answer:
```json
{
  "answer": "Retrieved policy excerpts:\n[01_ticket_priority] service use. Assign P3 priority to a nonblocking technical issue or product defect, and assign P4 priority to a general inquiry or feedback request. When several conditions apply, record the highest priority and the facts that justify it without treating VIP status as a safety severity.\n[01_ticket_priority] Assign P1 priority when a report describes an immediate safety concern or a widespread inability to use the ride service. Assign P2 priority to a blocked account or an incorrect charge that prevents a rider or driver from continuing normal service use. Assign P3 priority to a nonblocking technical i\n[10_vip_handling] Identify VIP eligibility only from a verified account flag rather than from a customer's claim in a message. Assign an eligible VIP ticket a named support owner and provide an update at least every 4 support hours while work remains open. VIP handling does not change safety priority, refund eligibil",
  "citations": [
    "01_ticket_priority",
    "10_vip_handling"
  ],
  "guardrails": [],
  "outcome": "answered",
  "ticket": null
}
```

Actual retrieved/lookup evidence:
- `01_ticket_priority:fixed:001:467e14d88ab04b30` parent `01_ticket_priority` cosine 0.77647883.
- `01_ticket_priority:fixed:000:f1252f8593080a60` parent `01_ticket_priority` cosine 0.69071752.
- `10_vip_handling:fixed:000:84af5ee5110bd235` parent `10_vip_handling` cosine 0.59247953.

Judge result and reproducible calculations:
```json
{
  "Accuracy": 1.0,
  "Completeness": 1.0,
  "Grounding": 1.0,
  "Safety": 1.0,
  "calculations": {
    "Accuracy": "5/(5+0)",
    "Completeness": "5/5",
    "Grounding": "3/3",
    "Safety": "0 if unsafe pattern/unmasked phone, otherwise 1"
  },
  "claim_checks": [
    {
      "cited_parent": "01_ticket_priority",
      "supported": true,
      "supporting_chunks": [
        "01_ticket_priority:fixed:001:467e14d88ab04b30"
      ],
      "text": "service use. Assign P3 priority to a nonblocking technical issue or product defect, and assign P4 priority to a general inquiry or feedback request. When several conditions apply, record the highest priority and the facts that justify it without treating VIP status as a safety severity."
    },
    {
      "cited_parent": "01_ticket_priority",
      "supported": true,
      "supporting_chunks": [
        "01_ticket_priority:fixed:000:f1252f8593080a60"
      ],
      "text": "Assign P1 priority when a report describes an immediate safety concern or a widespread inability to use the ride service. Assign P2 priority to a blocked account or an incorrect charge that prevents a rider or driver from continuing normal service use. Assign P3 priority to a nonblocking technical i"
    },
    {
      "cited_parent": "10_vip_handling",
      "supported": true,
      "supporting_chunks": [
        "10_vip_handling:fixed:000:84af5ee5110bd235"
      ],
      "text": "Identify VIP eligibility only from a verified account flag rather than from a customer's claim in a message. Assign an eligible VIP ticket a named support owner and provide an update at least every 4 support hours while work remains open. VIP handling does not change safety priority, refund eligibil"
    }
  ],
  "covered_facts": [
    "F1",
    "F2",
    "F3",
    "F4",
    "F5"
  ],
  "reasons": [
    "Declared evidence/rubric checks satisfied; bounded deterministic assessment"
  ]
}
```

## E02: Explain the acknowledgement and resolution SLA targets for P1, P2, P3 and P4 severity.

Expected evidence: {"expected_facts": [{"anchors": ["p1 severity", "15 elapsed minutes", "4 elapsed hours"], "id": "F1"}, {"anchors": ["p2 severity", "1 support hour", "24 support hours"], "id": "F2"}, {"anchors": ["p3 severity", "4 support hours", "72 support hours"], "id": "F3"}, {"anchors": ["p4 severity", "8 support hours", "120 support hours"], "id": "F4"}], "id": "E02", "kind": "policy", "query": "Explain the acknowledgement and resolution SLA targets for P1, P2, P3 and P4 severity.", "relevant_documents": ["02_severity_sla"], "topic": "02_severity_sla"}

Actual validated answer:
```json
{
  "answer": "Retrieved policy excerpts:\n[02_severity_sla] For P1 severity, acknowledge within 15 elapsed minutes and target resolution or a documented workaround within 4 elapsed hours. For P2 severity, acknowledge within 1 support hour and target resolution within 24 support hours. For P3 severity, acknowledge within 4 support hours and target resolution \n[02_severity_sla] y, acknowledge within 4 support hours and target resolution within 72 support hours; for P4 severity, acknowledge within 8 support hours and target resolution within 120 support hours. These SLA targets use the business-hours policy for support-hour calculations and require an update before a deadli\n[02_severity_sla] port-hour calculations and require an update before a deadline is missed, while external dependencies must be documented rather than presented as guaranteed completion times.",
  "citations": [
    "02_severity_sla"
  ],
  "guardrails": [],
  "outcome": "answered",
  "ticket": null
}
```

Actual retrieved/lookup evidence:
- `02_severity_sla:fixed:000:b78b055efceb846b` parent `02_severity_sla` cosine 0.72460610.
- `02_severity_sla:fixed:001:97d2fcf7d3f66970` parent `02_severity_sla` cosine 0.56678581.
- `02_severity_sla:fixed:002:62fc1a72f6be9210` parent `02_severity_sla` cosine 0.44369197.

Judge result and reproducible calculations:
```json
{
  "Accuracy": 1.0,
  "Completeness": 1.0,
  "Grounding": 1.0,
  "Safety": 1.0,
  "calculations": {
    "Accuracy": "4/(4+0)",
    "Completeness": "4/4",
    "Grounding": "3/3",
    "Safety": "0 if unsafe pattern/unmasked phone, otherwise 1"
  },
  "claim_checks": [
    {
      "cited_parent": "02_severity_sla",
      "supported": true,
      "supporting_chunks": [
        "02_severity_sla:fixed:000:b78b055efceb846b"
      ],
      "text": "For P1 severity, acknowledge within 15 elapsed minutes and target resolution or a documented workaround within 4 elapsed hours. For P2 severity, acknowledge within 1 support hour and target resolution within 24 support hours. For P3 severity, acknowledge within 4 support hours and target resolution"
    },
    {
      "cited_parent": "02_severity_sla",
      "supported": true,
      "supporting_chunks": [
        "02_severity_sla:fixed:001:97d2fcf7d3f66970"
      ],
      "text": "y, acknowledge within 4 support hours and target resolution within 72 support hours; for P4 severity, acknowledge within 8 support hours and target resolution within 120 support hours. These SLA targets use the business-hours policy for support-hour calculations and require an update before a deadli"
    },
    {
      "cited_parent": "02_severity_sla",
      "supported": true,
      "supporting_chunks": [
        "02_severity_sla:fixed:002:62fc1a72f6be9210"
      ],
      "text": "port-hour calculations and require an update before a deadline is missed, while external dependencies must be documented rather than presented as guaranteed completion times."
    }
  ],
  "covered_facts": [
    "F1",
    "F2",
    "F3",
    "F4"
  ],
  "reasons": [
    "Declared evidence/rubric checks satisfied; bounded deterministic assessment"
  ]
}
```

## E03: Explain the escalation matrix: specialist routing, P1 escalation, missed targets and handoff ownership.

Expected evidence: {"expected_facts": [{"anchors": ["billing specialist", "technical specialist", "account-security specialist"], "id": "F1"}, {"anchors": ["p1 safety report", "immediately", "duty incident lead"], "id": "F2"}, {"anchors": ["p2 ticket", "acknowledgement deadline"], "id": "F3"}, {"anchors": ["original owner", "acceptance is recorded"], "id": "F4"}], "id": "E03", "kind": "policy", "query": "Explain the escalation matrix: specialist routing, P1 escalation, missed targets and handoff ownership.", "relevant_documents": ["03_escalation_matrix"], "topic": "03_escalation_matrix"}

Actual validated answer:
```json
{
  "answer": "Retrieved policy excerpts:\n[03_escalation_matrix] Route billing and refund disputes to the billing specialist, technical issues and product defects to the technical specialist, and account-access failures to the account-security specialist. Escalate a P1 safety report immediately to the duty incident lead, who coordinates the responsible specialist\n[03_escalation_matrix] ty incident lead, who coordinates the responsible specialist and emergency guidance when appropriate. Escalate a P2 ticket to the support supervisor if its acknowledgement deadline is missed, and escalate any unresolved ticket before its resolution target expires. The receiving owner must accept the\n[03_escalation_matrix] solution target expires. The receiving owner must accept the handoff, and the original owner remains responsible for customer updates until acceptance is recorded.",
  "citations": [
    "03_escalation_matrix"
  ],
  "guardrails": [],
  "outcome": "answered",
  "ticket": null
}
```

Actual retrieved/lookup evidence:
- `03_escalation_matrix:fixed:000:16e3b8257f0eff0c` parent `03_escalation_matrix` cosine 0.62214082.
- `03_escalation_matrix:fixed:001:27645d729395448a` parent `03_escalation_matrix` cosine 0.60671538.
- `03_escalation_matrix:fixed:002:16a193f597c602d8` parent `03_escalation_matrix` cosine 0.56354785.

Judge result and reproducible calculations:
```json
{
  "Accuracy": 1.0,
  "Completeness": 1.0,
  "Grounding": 1.0,
  "Safety": 1.0,
  "calculations": {
    "Accuracy": "4/(4+0)",
    "Completeness": "4/4",
    "Grounding": "3/3",
    "Safety": "0 if unsafe pattern/unmasked phone, otherwise 1"
  },
  "claim_checks": [
    {
      "cited_parent": "03_escalation_matrix",
      "supported": true,
      "supporting_chunks": [
        "03_escalation_matrix:fixed:000:16e3b8257f0eff0c"
      ],
      "text": "Route billing and refund disputes to the billing specialist, technical issues and product defects to the technical specialist, and account-access failures to the account-security specialist. Escalate a P1 safety report immediately to the duty incident lead, who coordinates the responsible specialist"
    },
    {
      "cited_parent": "03_escalation_matrix",
      "supported": true,
      "supporting_chunks": [
        "03_escalation_matrix:fixed:001:27645d729395448a"
      ],
      "text": "ty incident lead, who coordinates the responsible specialist and emergency guidance when appropriate. Escalate a P2 ticket to the support supervisor if its acknowledgement deadline is missed, and escalate any unresolved ticket before its resolution target expires. The receiving owner must accept the"
    },
    {
      "cited_parent": "03_escalation_matrix",
      "supported": true,
      "supporting_chunks": [
        "03_escalation_matrix:fixed:002:16a193f597c602d8"
      ],
      "text": "solution target expires. The receiving owner must accept the handoff, and the original owner remains responsible for customer updates until acceptance is recorded."
    }
  ],
  "covered_facts": [
    "F1",
    "F2",
    "F3",
    "F4"
  ],
  "reasons": [
    "Declared evidence/rubric checks satisfied; bounded deterministic assessment"
  ]
}
```

## E04: Explain refund eligibility, processing time, compensation limits and approval restrictions.

Expected evidence: {"expected_facts": [{"anchors": ["duplicate charge", "confirmed overcharge"], "id": "F1"}, {"anchors": ["5 to 7 business days", "after approval"], "id": "F2"}, {"anchors": ["inr 200", "operations manager"], "id": "F3"}, {"anchors": ["do not promise a refund", "before approval"], "id": "F4"}], "id": "E04", "kind": "policy", "query": "Explain refund eligibility, processing time, compensation limits and approval restrictions.", "relevant_documents": ["04_refund_compensation"], "topic": "04_refund_compensation"}

Actual validated answer:
```json
{
  "answer": "Retrieved policy excerpts:\n[04_refund_compensation] ise a refund or compensation before approval, and record whether a service credit already covers the same loss to prevent duplicate reimbursement.\n[04_refund_compensation] A billing specialist may approve a refund after verifying a duplicate charge, a confirmed overcharge, or a charge for a service that was not delivered. Refund only the verified incorrect amount to the original payment method, with a target processing time of 5 to 7 business days after approval. A su\n[04_refund_compensation] processing time of 5 to 7 business days after approval. A support supervisor may approve goodwill compensation up to INR 200 for a documented service failure, while larger compensation requires the operations manager's approval. Do not promise a refund or compensation before approval, and record whe",
  "citations": [
    "04_refund_compensation"
  ],
  "guardrails": [],
  "outcome": "answered",
  "ticket": null
}
```

Actual retrieved/lookup evidence:
- `04_refund_compensation:fixed:002:01126a7ab8ef2101` parent `04_refund_compensation` cosine 0.53231353.
- `04_refund_compensation:fixed:000:f80d07bc14d4f8cb` parent `04_refund_compensation` cosine 0.52197504.
- `04_refund_compensation:fixed:001:92e90cec52f577db` parent `04_refund_compensation` cosine 0.50466639.

Judge result and reproducible calculations:
```json
{
  "Accuracy": 1.0,
  "Completeness": 1.0,
  "Grounding": 1.0,
  "Safety": 1.0,
  "calculations": {
    "Accuracy": "4/(4+0)",
    "Completeness": "4/4",
    "Grounding": "3/3",
    "Safety": "0 if unsafe pattern/unmasked phone, otherwise 1"
  },
  "claim_checks": [
    {
      "cited_parent": "04_refund_compensation",
      "supported": true,
      "supporting_chunks": [
        "04_refund_compensation:fixed:002:01126a7ab8ef2101"
      ],
      "text": "ise a refund or compensation before approval, and record whether a service credit already covers the same loss to prevent duplicate reimbursement."
    },
    {
      "cited_parent": "04_refund_compensation",
      "supported": true,
      "supporting_chunks": [
        "04_refund_compensation:fixed:000:f80d07bc14d4f8cb"
      ],
      "text": "A billing specialist may approve a refund after verifying a duplicate charge, a confirmed overcharge, or a charge for a service that was not delivered. Refund only the verified incorrect amount to the original payment method, with a target processing time of 5 to 7 business days after approval. A su"
    },
    {
      "cited_parent": "04_refund_compensation",
      "supported": true,
      "supporting_chunks": [
        "04_refund_compensation:fixed:001:92e90cec52f577db"
      ],
      "text": "processing time of 5 to 7 business days after approval. A support supervisor may approve goodwill compensation up to INR 200 for a documented service failure, while larger compensation requires the operations manager's approval. Do not promise a refund or compensation before approval, and record whe"
    }
  ],
  "covered_facts": [
    "F1",
    "F2",
    "F3",
    "F4"
  ],
  "reasons": [
    "Declared evidence/rubric checks satisfied; bounded deterministic assessment"
  ]
}
```

## E05: Explain customer communication channels, callback consent, verification and prohibited credential requests.

Expected evidence: {"expected_facts": [{"anchors": ["in-app support", "email"], "id": "F1"}, {"anchors": ["callback", "consents"], "id": "F2"}, {"anchors": ["account-verification process"], "id": "F3"}, {"anchors": ["never request an otp", "account password"], "id": "F4"}], "id": "E05", "kind": "policy", "query": "Explain customer communication channels, callback consent, verification and prohibited credential requests.", "relevant_documents": ["05_communication_channels"], "topic": "05_communication_channels"}

Actual validated answer:
```json
{
  "answer": "Retrieved policy excerpts:\n[05_communication_channels] requests or consents to the call. Before sharing ticket details on an alternative channel, complete the approved account-verification process and avoid exposing another customer's information. Never request an OTP, full payment-card details, or an account password, and keep every customer update att\n[05_communication_channels] , or an account password, and keep every customer update attached to the ticket record.\n[05_communication_channels] Use in-app support as the primary communication channel for rider and driver ticket updates, with email as the alternative when account access is unavailable. A support agent may offer a callback for an urgent issue only after the customer requests or consents to the call. Before sharing ticket deta",
  "citations": [
    "05_communication_channels"
  ],
  "guardrails": [],
  "outcome": "answered",
  "ticket": null
}
```

Actual retrieved/lookup evidence:
- `05_communication_channels:fixed:001:587121898580a804` parent `05_communication_channels` cosine 0.60068232.
- `05_communication_channels:fixed:002:24464a73f6de63f2` parent `05_communication_channels` cosine 0.48439616.
- `05_communication_channels:fixed:000:b16e1773936c4fbb` parent `05_communication_channels` cosine 0.47760856.

Judge result and reproducible calculations:
```json
{
  "Accuracy": 1.0,
  "Completeness": 1.0,
  "Grounding": 1.0,
  "Safety": 1.0,
  "calculations": {
    "Accuracy": "4/(4+0)",
    "Completeness": "4/4",
    "Grounding": "3/3",
    "Safety": "0 if unsafe pattern/unmasked phone, otherwise 1"
  },
  "claim_checks": [
    {
      "cited_parent": "05_communication_channels",
      "supported": true,
      "supporting_chunks": [
        "05_communication_channels:fixed:001:587121898580a804"
      ],
      "text": "requests or consents to the call. Before sharing ticket details on an alternative channel, complete the approved account-verification process and avoid exposing another customer's information. Never request an OTP, full payment-card details, or an account password, and keep every customer update att"
    },
    {
      "cited_parent": "05_communication_channels",
      "supported": true,
      "supporting_chunks": [
        "05_communication_channels:fixed:002:24464a73f6de63f2"
      ],
      "text": ", or an account password, and keep every customer update attached to the ticket record."
    },
    {
      "cited_parent": "05_communication_channels",
      "supported": true,
      "supporting_chunks": [
        "05_communication_channels:fixed:000:b16e1773936c4fbb"
      ],
      "text": "Use in-app support as the primary communication channel for rider and driver ticket updates, with email as the alternative when account access is unavailable. A support agent may offer a callback for an urgent issue only after the customer requests or consents to the call. Before sharing ticket deta"
    }
  ],
  "covered_facts": [
    "F1",
    "F2",
    "F3",
    "F4"
  ],
  "reasons": [
    "Declared evidence/rubric checks satisfied; bounded deterministic assessment"
  ]
}
```

## E06: Explain standard business hours, holiday support, SLA clock pauses and P1 on-call coverage.

Expected evidence: {"expected_facts": [{"anchors": ["09:00 to 18:00", "monday through saturday"], "id": "F1"}, {"anchors": ["clocks pause", "resume"], "id": "F2"}, {"anchors": ["p1 safety", "at all times", "sundays and holidays"], "id": "F3"}, {"anchors": ["outside standard hours", "without promising immediate resolution"], "id": "F4"}], "id": "E06", "kind": "policy", "query": "Explain standard business hours, holiday support, SLA clock pauses and P1 on-call coverage.", "relevant_documents": ["06_business_hours"], "topic": "06_business_hours"}

Actual validated answer:
```json
{
  "answer": "Retrieved policy excerpts:\n[06_business_hours]  business-day refund processing uses Monday through Friday excluding listed holidays. P1 safety and major-outage reports reach the on-call team at all times, including Sundays and holidays, and use elapsed-time SLA clocks. For other requests received outside standard hours, acknowledge receipt autom\n[06_business_hours] Standard support hours are 09:00 to 18:00 Asia/Kolkata from Monday through Saturday, excluding holidays listed in the team's published support calendar. Support-hour SLA clocks pause outside those hours and resume at the next opening, while business-day refund processing uses Monday through Friday e\n[06_business_hours] s received outside standard hours, acknowledge receipt automatically and state when staffed support resumes without promising immediate resolution.",
  "citations": [
    "06_business_hours"
  ],
  "guardrails": [],
  "outcome": "answered",
  "ticket": null
}
```

Actual retrieved/lookup evidence:
- `06_business_hours:fixed:001:efbb0d33b4eb8416` parent `06_business_hours` cosine 0.64130533.
- `06_business_hours:fixed:000:3a9ed78829619321` parent `06_business_hours` cosine 0.60583192.
- `06_business_hours:fixed:002:63203da5aeb66f2c` parent `06_business_hours` cosine 0.53779620.

Judge result and reproducible calculations:
```json
{
  "Accuracy": 1.0,
  "Completeness": 1.0,
  "Grounding": 1.0,
  "Safety": 1.0,
  "calculations": {
    "Accuracy": "4/(4+0)",
    "Completeness": "4/4",
    "Grounding": "3/3",
    "Safety": "0 if unsafe pattern/unmasked phone, otherwise 1"
  },
  "claim_checks": [
    {
      "cited_parent": "06_business_hours",
      "supported": true,
      "supporting_chunks": [
        "06_business_hours:fixed:001:efbb0d33b4eb8416"
      ],
      "text": "business-day refund processing uses Monday through Friday excluding listed holidays. P1 safety and major-outage reports reach the on-call team at all times, including Sundays and holidays, and use elapsed-time SLA clocks. For other requests received outside standard hours, acknowledge receipt autom"
    },
    {
      "cited_parent": "06_business_hours",
      "supported": true,
      "supporting_chunks": [
        "06_business_hours:fixed:000:3a9ed78829619321"
      ],
      "text": "Standard support hours are 09:00 to 18:00 Asia/Kolkata from Monday through Saturday, excluding holidays listed in the team's published support calendar. Support-hour SLA clocks pause outside those hours and resume at the next opening, while business-day refund processing uses Monday through Friday e"
    },
    {
      "cited_parent": "06_business_hours",
      "supported": true,
      "supporting_chunks": [
        "06_business_hours:fixed:002:63203da5aeb66f2c"
      ],
      "text": "s received outside standard hours, acknowledge receipt automatically and state when staffed support resumes without promising immediate resolution."
    }
  ],
  "covered_facts": [
    "F1",
    "F2",
    "F3",
    "F4"
  ],
  "reasons": [
    "Declared evidence/rubric checks satisfied; bounded deterministic assessment"
  ]
}
```

## E07: Explain repeat-complaint handling: time window, linked tickets, supervisor review and customer updates.

Expected evidence: {"expected_facts": [{"anchors": ["within 30 days"], "id": "F1"}, {"anchors": ["link the new report", "reopen"], "id": "F2"}, {"anchors": ["second repeat", "support supervisor"], "id": "F3"}, {"anchors": ["avoid asking for evidence already present"], "id": "F4"}], "id": "E07", "kind": "policy", "query": "Explain repeat-complaint handling: time window, linked tickets, supervisor review and customer updates.", "relevant_documents": ["07_repeat_complaints"], "topic": "07_repeat_complaints"}

Actual validated answer:
```json
{
  "answer": "Retrieved policy excerpts:\n[07_repeat_complaints] Treat a report as a repeat complaint when the same customer reports the same underlying issue within 30 days of the earlier ticket. Link the new report to the earlier ticket and reopen that ticket when the previous resolution has not held, preserving the original history. Assign a support supervisor\n[07_repeat_complaints] preserving the original history. Assign a support supervisor to review the root cause on the second repeat, and raise priority when the facts show greater impact rather than because of complaint count alone. Tell the customer which owner is investigating and avoid asking for evidence already present\n[07_repeat_complaints]  investigating and avoid asking for evidence already present in the linked history.",
  "citations": [
    "07_repeat_complaints"
  ],
  "guardrails": [],
  "outcome": "answered",
  "ticket": null
}
```

Actual retrieved/lookup evidence:
- `07_repeat_complaints:fixed:000:5de3ff2c88a5bdac` parent `07_repeat_complaints` cosine 0.75030285.
- `07_repeat_complaints:fixed:001:857bbf4d2651a994` parent `07_repeat_complaints` cosine 0.71435297.
- `07_repeat_complaints:fixed:002:80dff3857347202e` parent `07_repeat_complaints` cosine 0.64096487.

Judge result and reproducible calculations:
```json
{
  "Accuracy": 1.0,
  "Completeness": 1.0,
  "Grounding": 1.0,
  "Safety": 1.0,
  "calculations": {
    "Accuracy": "4/(4+0)",
    "Completeness": "4/4",
    "Grounding": "3/3",
    "Safety": "0 if unsafe pattern/unmasked phone, otherwise 1"
  },
  "claim_checks": [
    {
      "cited_parent": "07_repeat_complaints",
      "supported": true,
      "supporting_chunks": [
        "07_repeat_complaints:fixed:000:5de3ff2c88a5bdac"
      ],
      "text": "Treat a report as a repeat complaint when the same customer reports the same underlying issue within 30 days of the earlier ticket. Link the new report to the earlier ticket and reopen that ticket when the previous resolution has not held, preserving the original history. Assign a support supervisor"
    },
    {
      "cited_parent": "07_repeat_complaints",
      "supported": true,
      "supporting_chunks": [
        "07_repeat_complaints:fixed:001:857bbf4d2651a994"
      ],
      "text": "preserving the original history. Assign a support supervisor to review the root cause on the second repeat, and raise priority when the facts show greater impact rather than because of complaint count alone. Tell the customer which owner is investigating and avoid asking for evidence already present"
    },
    {
      "cited_parent": "07_repeat_complaints",
      "supported": true,
      "supporting_chunks": [
        "07_repeat_complaints:fixed:002:80dff3857347202e"
      ],
      "text": "investigating and avoid asking for evidence already present in the linked history."
    }
  ],
  "covered_facts": [
    "F1",
    "F2",
    "F3",
    "F4"
  ],
  "reasons": [
    "Declared evidence/rubric checks satisfied; bounded deterministic assessment"
  ]
}
```

## E08: Explain service-credit limits, validity, cash restrictions and approval records.

Expected evidence: {"expected_facts": [{"anchors": ["inr 150", "cash refund"], "id": "F1"}, {"anchors": ["validity of 30 days"], "id": "F2"}, {"anchors": ["cannot be transferred", "exchanged for cash"], "id": "F3"}, {"anchors": ["record the reason", "approval", "expiry"], "id": "F4"}], "id": "E08", "kind": "policy", "query": "Explain service-credit limits, validity, cash restrictions and approval records.", "relevant_documents": ["08_service_credit"], "topic": "08_service_credit"}

Actual validated answer:
```json
{
  "answer": "Retrieved policy excerpts:\n[08_service_credit]  account balance, with validity of 30 days from issuance. Service credits cannot be transferred or exchanged for cash, and a credit above INR 150 requires the operations manager's approval. Record the reason, approval, amount and expiry in the ticket and communicate those terms before issuing the cr\n[08_service_credit] the ticket and communicate those terms before issuing the credit.\n[08_service_credit] A support supervisor may approve a noncash service credit up to INR 150 for a verified service interruption when a cash refund does not already compensate the same loss. Apply an approved service credit to the customer's fabricated capstone account balance, with validity of 30 days from issuance. Se",
  "citations": [
    "08_service_credit"
  ],
  "guardrails": [],
  "outcome": "answered",
  "ticket": null
}
```

Actual retrieved/lookup evidence:
- `08_service_credit:fixed:001:e019600e4052eaa0` parent `08_service_credit` cosine 0.59970176.
- `08_service_credit:fixed:002:80846bbe499e9ad7` parent `08_service_credit` cosine 0.57532400.
- `08_service_credit:fixed:000:73e5b77be6988721` parent `08_service_credit` cosine 0.56571347.

Judge result and reproducible calculations:
```json
{
  "Accuracy": 1.0,
  "Completeness": 1.0,
  "Grounding": 1.0,
  "Safety": 1.0,
  "calculations": {
    "Accuracy": "4/(4+0)",
    "Completeness": "4/4",
    "Grounding": "3/3",
    "Safety": "0 if unsafe pattern/unmasked phone, otherwise 1"
  },
  "claim_checks": [
    {
      "cited_parent": "08_service_credit",
      "supported": true,
      "supporting_chunks": [
        "08_service_credit:fixed:001:e019600e4052eaa0"
      ],
      "text": "account balance, with validity of 30 days from issuance. Service credits cannot be transferred or exchanged for cash, and a credit above INR 150 requires the operations manager's approval. Record the reason, approval, amount and expiry in the ticket and communicate those terms before issuing the cr"
    },
    {
      "cited_parent": "08_service_credit",
      "supported": true,
      "supporting_chunks": [
        "08_service_credit:fixed:002:80846bbe499e9ad7"
      ],
      "text": "the ticket and communicate those terms before issuing the credit."
    },
    {
      "cited_parent": "08_service_credit",
      "supported": true,
      "supporting_chunks": [
        "08_service_credit:fixed:000:73e5b77be6988721"
      ],
      "text": "A support supervisor may approve a noncash service credit up to INR 150 for a verified service interruption when a cash refund does not already compensate the same loss. Apply an approved service credit to the customer's fabricated capstone account balance, with validity of 30 days from issuance. Se"
    }
  ],
  "covered_facts": [
    "F1",
    "F2",
    "F3",
    "F4"
  ],
  "reasons": [
    "Declared evidence/rubric checks satisfied; bounded deterministic assessment"
  ]
}
```

## E09: Explain feedback collection, survey scale, reminder limit and low-rating follow-up.

Expected evidence: {"expected_facts": [{"anchors": ["optional in-app feedback survey", "1 to 5"], "id": "F1"}, {"anchors": ["at most one reminder", "48 hours"], "id": "F2"}, {"anchors": ["rating of 1 or 2", "supervisor review"], "id": "F3"}, {"anchors": ["aggregated themes", "without identifying individual customers"], "id": "F4"}], "id": "E09", "kind": "policy", "query": "Explain feedback collection, survey scale, reminder limit and low-rating follow-up.", "relevant_documents": ["09_feedback"], "topic": "09_feedback"}

Actual validated answer:
```json
{
  "answer": "Retrieved policy excerpts:\n[09_feedback] After a ticket is resolved, offer one optional in-app feedback survey asking for a satisfaction rating from 1 to 5 and a short comment. If the customer does not respond, send at most one reminder after 48 hours and do not make feedback a condition of receiving support. A rating of 1 or 2 or a commen\n[09_feedback] ndition of receiving support. A rating of 1 or 2 or a comment indicating an unresolved issue triggers a supervisor review of the resolution. Store feedback against the ticket using the ticket-retention policy, and report aggregated themes without identifying individual customers.\n[07_repeat_complaints]  investigating and avoid asking for evidence already present in the linked history.",
  "citations": [
    "09_feedback",
    "07_repeat_complaints"
  ],
  "guardrails": [],
  "outcome": "answered",
  "ticket": null
}
```

Actual retrieved/lookup evidence:
- `09_feedback:fixed:000:a3d8734f888a96c1` parent `09_feedback` cosine 0.66462582.
- `09_feedback:fixed:001:396018a7a8a6b896` parent `09_feedback` cosine 0.58186120.
- `07_repeat_complaints:fixed:002:80dff3857347202e` parent `07_repeat_complaints` cosine 0.26213944.

Judge result and reproducible calculations:
```json
{
  "Accuracy": 1.0,
  "Completeness": 1.0,
  "Grounding": 1.0,
  "Safety": 1.0,
  "calculations": {
    "Accuracy": "4/(4+0)",
    "Completeness": "4/4",
    "Grounding": "3/3",
    "Safety": "0 if unsafe pattern/unmasked phone, otherwise 1"
  },
  "claim_checks": [
    {
      "cited_parent": "09_feedback",
      "supported": true,
      "supporting_chunks": [
        "09_feedback:fixed:000:a3d8734f888a96c1"
      ],
      "text": "After a ticket is resolved, offer one optional in-app feedback survey asking for a satisfaction rating from 1 to 5 and a short comment. If the customer does not respond, send at most one reminder after 48 hours and do not make feedback a condition of receiving support. A rating of 1 or 2 or a commen"
    },
    {
      "cited_parent": "09_feedback",
      "supported": true,
      "supporting_chunks": [
        "09_feedback:fixed:001:396018a7a8a6b896"
      ],
      "text": "ndition of receiving support. A rating of 1 or 2 or a comment indicating an unresolved issue triggers a supervisor review of the resolution. Store feedback against the ticket using the ticket-retention policy, and report aggregated themes without identifying individual customers."
    },
    {
      "cited_parent": "07_repeat_complaints",
      "supported": true,
      "supporting_chunks": [
        "07_repeat_complaints:fixed:002:80dff3857347202e"
      ],
      "text": "investigating and avoid asking for evidence already present in the linked history."
    }
  ],
  "covered_facts": [
    "F1",
    "F2",
    "F3",
    "F4"
  ],
  "reasons": [
    "Declared evidence/rubric checks satisfied; bounded deterministic assessment"
  ]
}
```

## E10: Explain VIP eligibility, owner updates, policy limits and missed-SLA handling.

Expected evidence: {"expected_facts": [{"anchors": ["verified account flag"], "id": "F1"}, {"anchors": ["named support owner", "every 4 support hours"], "id": "F2"}, {"anchors": ["does not change safety priority", "refund eligibility"], "id": "F3"}, {"anchors": ["normal sla deadline", "support supervisor"], "id": "F4"}], "id": "E10", "kind": "policy", "query": "Explain VIP eligibility, owner updates, policy limits and missed-SLA handling.", "relevant_documents": ["10_vip_handling"], "topic": "10_vip_handling"}

Actual validated answer:
```json
{
  "answer": "Retrieved policy excerpts:\n[10_vip_handling] IP handling does not change safety priority, refund eligibility, compensation limits, or the requirement to verify account access. When a VIP complaint remains unresolved at its normal SLA deadline, the named owner must involve the support supervisor and communicate the next review time.\n[10_vip_handling] Identify VIP eligibility only from a verified account flag rather than from a customer's claim in a message. Assign an eligible VIP ticket a named support owner and provide an update at least every 4 support hours while work remains open. VIP handling does not change safety priority, refund eligibil\n[02_severity_sla] port-hour calculations and require an update before a deadline is missed, while external dependencies must be documented rather than presented as guaranteed completion times.",
  "citations": [
    "10_vip_handling",
    "02_severity_sla"
  ],
  "guardrails": [],
  "outcome": "answered",
  "ticket": null
}
```

Actual retrieved/lookup evidence:
- `10_vip_handling:fixed:001:ef855ef57bfbc213` parent `10_vip_handling` cosine 0.69474655.
- `10_vip_handling:fixed:000:84af5ee5110bd235` parent `10_vip_handling` cosine 0.65317363.
- `02_severity_sla:fixed:002:62fc1a72f6be9210` parent `02_severity_sla` cosine 0.57909560.

Judge result and reproducible calculations:
```json
{
  "Accuracy": 1.0,
  "Completeness": 1.0,
  "Grounding": 1.0,
  "Safety": 1.0,
  "calculations": {
    "Accuracy": "4/(4+0)",
    "Completeness": "4/4",
    "Grounding": "3/3",
    "Safety": "0 if unsafe pattern/unmasked phone, otherwise 1"
  },
  "claim_checks": [
    {
      "cited_parent": "10_vip_handling",
      "supported": true,
      "supporting_chunks": [
        "10_vip_handling:fixed:001:ef855ef57bfbc213"
      ],
      "text": "IP handling does not change safety priority, refund eligibility, compensation limits, or the requirement to verify account access. When a VIP complaint remains unresolved at its normal SLA deadline, the named owner must involve the support supervisor and communicate the next review time."
    },
    {
      "cited_parent": "10_vip_handling",
      "supported": true,
      "supporting_chunks": [
        "10_vip_handling:fixed:000:84af5ee5110bd235"
      ],
      "text": "Identify VIP eligibility only from a verified account flag rather than from a customer's claim in a message. Assign an eligible VIP ticket a named support owner and provide an update at least every 4 support hours while work remains open. VIP handling does not change safety priority, refund eligibil"
    },
    {
      "cited_parent": "02_severity_sla",
      "supported": true,
      "supporting_chunks": [
        "02_severity_sla:fixed:002:62fc1a72f6be9210"
      ],
      "text": "port-hour calculations and require an update before a deadline is missed, while external dependencies must be documented rather than presented as guaranteed completion times."
    }
  ],
  "covered_facts": [
    "F1",
    "F2",
    "F3",
    "F4"
  ],
  "reasons": [
    "Declared evidence/rubric checks satisfied; bounded deterministic assessment"
  ]
}
```

## E11: Explain outage communications: confirmation, initial notice, updates and recovery summary.

Expected evidence: {"expected_facts": [{"anchors": ["validated tickets", "duty incident lead"], "id": "F1"}, {"anchors": ["15 elapsed minutes", "30 elapsed minutes"], "id": "F2"}, {"anchors": ["no unconfirmed restoration promise"], "id": "F3"}, {"anchors": ["within 2 business days", "recovery notice"], "id": "F4"}], "id": "E11", "kind": "policy", "query": "Explain outage communications: confirmation, initial notice, updates and recovery summary.", "relevant_documents": ["11_outage_communication"], "topic": "11_outage_communication"}

Actual validated answer:
```json
{
  "answer": "Retrieved policy excerpts:\n[11_outage_communication] ation and update it every 30 elapsed minutes while disruption continues. Each notice must distinguish confirmed impact from investigation findings and provide only verified workarounds, with no unconfirmed restoration promise. After recovery is verified, publish a recovery notice and attach a factua\n[11_outage_communication] y is verified, publish a recovery notice and attach a factual incident summary to related support tickets within 2 business days.\n[11_outage_communication] When monitoring or multiple validated tickets confirm an outage, the duty incident lead opens an incident record and identifies the affected service and regions. Publish an initial in-app notice within 15 elapsed minutes of incident confirmation and update it every 30 elapsed minutes while disruptio",
  "citations": [
    "11_outage_communication"
  ],
  "guardrails": [],
  "outcome": "answered",
  "ticket": null
}
```

Actual retrieved/lookup evidence:
- `11_outage_communication:fixed:001:2a50f755af392acd` parent `11_outage_communication` cosine 0.79320401.
- `11_outage_communication:fixed:002:2a8cb59e2a16f2bb` parent `11_outage_communication` cosine 0.69353813.
- `11_outage_communication:fixed:000:e594a15651293c24` parent `11_outage_communication` cosine 0.65371913.

Judge result and reproducible calculations:
```json
{
  "Accuracy": 1.0,
  "Completeness": 1.0,
  "Grounding": 1.0,
  "Safety": 1.0,
  "calculations": {
    "Accuracy": "4/(4+0)",
    "Completeness": "4/4",
    "Grounding": "3/3",
    "Safety": "0 if unsafe pattern/unmasked phone, otherwise 1"
  },
  "claim_checks": [
    {
      "cited_parent": "11_outage_communication",
      "supported": true,
      "supporting_chunks": [
        "11_outage_communication:fixed:001:2a50f755af392acd"
      ],
      "text": "ation and update it every 30 elapsed minutes while disruption continues. Each notice must distinguish confirmed impact from investigation findings and provide only verified workarounds, with no unconfirmed restoration promise. After recovery is verified, publish a recovery notice and attach a factua"
    },
    {
      "cited_parent": "11_outage_communication",
      "supported": true,
      "supporting_chunks": [
        "11_outage_communication:fixed:002:2a8cb59e2a16f2bb"
      ],
      "text": "y is verified, publish a recovery notice and attach a factual incident summary to related support tickets within 2 business days."
    },
    {
      "cited_parent": "11_outage_communication",
      "supported": true,
      "supporting_chunks": [
        "11_outage_communication:fixed:000:e594a15651293c24"
      ],
      "text": "When monitoring or multiple validated tickets confirm an outage, the duty incident lead opens an incident record and identifies the affected service and regions. Publish an initial in-app notice within 15 elapsed minutes of incident confirmation and update it every 30 elapsed minutes while disruptio"
    }
  ],
  "covered_facts": [
    "F1",
    "F2",
    "F3",
    "F4"
  ],
  "reasons": [
    "Declared evidence/rubric checks satisfied; bounded deterministic assessment"
  ]
}
```

## E12: Explain ticket retention, closure, restricted access and legal holds.

Expected evidence: {"expected_facts": [{"anchors": ["180 days", "after the ticket is closed"], "id": "F1"}, {"anchors": ["close it after confirming resolution"], "id": "F2"}, {"anchors": ["restrict ticket access", "masked phone numbers"], "id": "F3"}, {"anchors": ["legal hold", "every 30 days"], "id": "F4"}], "id": "E12", "kind": "policy", "query": "Explain ticket retention, closure, restricted access and legal holds.", "relevant_documents": ["12_ticket_retention"], "topic": "12_ticket_retention"}

Actual validated answer:
```json
{
  "answer": "Retrieved policy excerpts:\n[12_ticket_retention] close it after confirming resolution or document why further work is required rather than leave it indefinitely unresolved. Restrict ticket access to staff assigned to support duties, and use masked phone numbers in diagnostic logs. An authorized legal hold pauses deletion only for the affected reco\n[12_ticket_retention] Retain a support ticket and its attached communication for 180 days after the ticket is closed, then delete identifying details through the scheduled retention process. For a resolved ticket that remains open, the support owner must either close it after confirming resolution or document why further\n[12_ticket_retention] orized legal hold pauses deletion only for the affected records, must be documented and reviewed every 30 days, and allows deletion to resume after the hold is released.",
  "citations": [
    "12_ticket_retention"
  ],
  "guardrails": [],
  "outcome": "answered",
  "ticket": null
}
```

Actual retrieved/lookup evidence:
- `12_ticket_retention:fixed:001:1382f4294a33c865` parent `12_ticket_retention` cosine 0.66686237.
- `12_ticket_retention:fixed:000:3abdf5185121cb8d` parent `12_ticket_retention` cosine 0.63033026.
- `12_ticket_retention:fixed:002:8dd6ff87848d42ae` parent `12_ticket_retention` cosine 0.57525712.

Judge result and reproducible calculations:
```json
{
  "Accuracy": 1.0,
  "Completeness": 1.0,
  "Grounding": 1.0,
  "Safety": 1.0,
  "calculations": {
    "Accuracy": "4/(4+0)",
    "Completeness": "4/4",
    "Grounding": "3/3",
    "Safety": "0 if unsafe pattern/unmasked phone, otherwise 1"
  },
  "claim_checks": [
    {
      "cited_parent": "12_ticket_retention",
      "supported": true,
      "supporting_chunks": [
        "12_ticket_retention:fixed:001:1382f4294a33c865"
      ],
      "text": "close it after confirming resolution or document why further work is required rather than leave it indefinitely unresolved. Restrict ticket access to staff assigned to support duties, and use masked phone numbers in diagnostic logs. An authorized legal hold pauses deletion only for the affected reco"
    },
    {
      "cited_parent": "12_ticket_retention",
      "supported": true,
      "supporting_chunks": [
        "12_ticket_retention:fixed:000:3abdf5185121cb8d"
      ],
      "text": "Retain a support ticket and its attached communication for 180 days after the ticket is closed, then delete identifying details through the scheduled retention process. For a resolved ticket that remains open, the support owner must either close it after confirming resolution or document why further"
    },
    {
      "cited_parent": "12_ticket_retention",
      "supported": true,
      "supporting_chunks": [
        "12_ticket_retention:fixed:002:8dd6ff87848d42ae"
      ],
      "text": "orized legal hold pauses deletion only for the affected records, must be documented and reviewed every 30 days, and allows deletion to resume after the hold is released."
    }
  ],
  "covered_facts": [
    "F1",
    "F2",
    "F3",
    "F4"
  ],
  "reasons": [
    "Declared evidence/rubric checks satisfied; bounded deterministic assessment"
  ]
}
```

## E13: How can I calculate the orbital period of a planet?

Expected evidence: {"expected_facts": [], "id": "E13", "kind": "out_of_scope", "query": "How can I calculate the orbital period of a planet?", "relevant_documents": [], "topic": null}

Actual validated answer:
```json
{
  "answer": "I don't know based on the available policy documents.",
  "citations": [],
  "guardrails": [
    "groundedness_refusal"
  ],
  "outcome": "refused",
  "ticket": null
}
```

Actual retrieved/lookup evidence:
- `06_business_hours:fixed:000:3a9ed78829619321` parent `06_business_hours` cosine 0.12251306.
- `08_service_credit:fixed:001:e019600e4052eaa0` parent `08_service_credit` cosine 0.11971521.
- `02_severity_sla:fixed:002:62fc1a72f6be9210` parent `02_severity_sla` cosine 0.08837545.

Judge result and reproducible calculations:
```json
{
  "Accuracy": 1.0,
  "Completeness": 1.0,
  "Grounding": 1.0,
  "Safety": 1.0,
  "calculations": {
    "Accuracy": "1 iff exact evidence-free refusal, else 0",
    "Completeness": "1 iff correct refusal, else 0",
    "Grounding": "1 iff refusal plus measured retrieval fallback, else 0",
    "Safety": "independent unsafe-content check"
  },
  "claim_checks": [],
  "covered_facts": [],
  "reasons": [
    "Declared evidence/rubric checks satisfied; bounded deterministic assessment"
  ]
}
```

## E14: Explain photosynthesis in plants.

Expected evidence: {"expected_facts": [], "id": "E14", "kind": "out_of_scope", "query": "Explain photosynthesis in plants.", "relevant_documents": [], "topic": null}

Actual validated answer:
```json
{
  "answer": "I don't know based on the available policy documents.",
  "citations": [],
  "guardrails": [
    "groundedness_refusal"
  ],
  "outcome": "refused",
  "ticket": null
}
```

Actual retrieved/lookup evidence:
- `04_refund_compensation:fixed:002:01126a7ab8ef2101` parent `04_refund_compensation` cosine 0.09160292.
- `09_feedback:fixed:001:396018a7a8a6b896` parent `09_feedback` cosine 0.06361765.
- `04_refund_compensation:fixed:000:f80d07bc14d4f8cb` parent `04_refund_compensation` cosine 0.04418039.

Judge result and reproducible calculations:
```json
{
  "Accuracy": 1.0,
  "Completeness": 1.0,
  "Grounding": 1.0,
  "Safety": 1.0,
  "calculations": {
    "Accuracy": "1 iff exact evidence-free refusal, else 0",
    "Completeness": "1 iff correct refusal, else 0",
    "Grounding": "1 iff refusal plus measured retrieval fallback, else 0",
    "Safety": "independent unsafe-content check"
  },
  "claim_checks": [],
  "covered_facts": [],
  "reasons": [
    "Declared evidence/rubric checks satisfied; bounded deterministic assessment"
  ]
}
```

## E15: Check OLA-9999 status.

Expected evidence: {"expected_facts": [], "id": "E15", "kind": "unknown_ticket", "query": "Check OLA-9999 status.", "relevant_documents": [], "topic": null}

Actual validated answer:
```json
{
  "answer": "Ticket OLA-9999 was not found (unknown_record_id).",
  "citations": [],
  "guardrails": [],
  "outcome": "not_found",
  "ticket": {
    "days_since_created": null,
    "error": "unknown_record_id",
    "escalated": null,
    "escalation_score": null,
    "escalation_threshold": null,
    "found": false,
    "recommend_escalation": false,
    "record_id": "OLA-9999",
    "reopen_count": null,
    "resolution_time_hours": null,
    "status": null
  }
}
```

Actual retrieved/lookup evidence:
- {"days_since_created": null, "error": "unknown_record_id", "escalated": null, "escalation_score": null, "escalation_threshold": null, "found": false, "recommend_escalation": false, "record_id": "OLA-9999", "reopen_count": null, "resolution_time_hours": null, "status": null}

Judge result and reproducible calculations:
```json
{
  "Accuracy": 1.0,
  "Completeness": 1.0,
  "Grounding": 1.0,
  "Safety": 1.0,
  "calculations": {
    "Accuracy": "1 iff exact not-found answer and actual null-fact lookup match, else 0",
    "Completeness": "1 iff exact not-found answer and actual null-fact lookup match, else 0",
    "Grounding": "1 iff exact not-found answer and actual null-fact lookup match, else 0",
    "Safety": "independent unsafe-content check"
  },
  "claim_checks": [],
  "covered_facts": [],
  "reasons": [
    "Declared evidence/rubric checks satisfied; bounded deterministic assessment"
  ]
}
```

## Observed weaknesses

The unchanged fixed-chunk crew quotes partial/overlapping excerpts. Missing fact groups reduce completeness; lack of expected evidence reduces accuracy. Similarity gating and pattern-based safety do not prove robustness on near-domain or adversarial language. All low scores remain in the 15-case average; no labels, prompts, thresholds or crew behavior were tuned after observing evaluation.
