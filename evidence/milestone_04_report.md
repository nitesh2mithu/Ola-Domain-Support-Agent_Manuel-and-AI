# Milestone 4 executed acceptance evidence

12/12 acceptance checks passed in each of two separate processes; complete JSON reports match exactly. Tasks 1–5 prerequisites: 8/8 dataset/policy +8/8 RAG; prior framework regression: 6/6.

Reproduce: `.venv311/bin/python -m tests.milestone_04_acceptance --report evidence/milestone_04_acceptance.json`. The JSON report retains all intermediate task outputs, declared schemas, actual tool results, consumed results and validated drafts/responses.

## Dataset-grounded escalation design

```json
{
  "above_threshold": 12,
  "at_threshold": 1,
  "formula": "round(0.6*int(escalated) + 0.4*(days_since_created/30), 6)",
  "max": 0.986667,
  "min": 0.0,
  "normalized_recency": "1 - days_since_created/30; age signal = 1 - normalized_recency",
  "percentile_method": "nearest rank: ceil(0.8*N), strict score > threshold",
  "rank": 48,
  "record_count": 60,
  "scores_sorted": [
    0.0,
    0.04,
    0.066667,
    0.066667,
    0.08,
    0.093333,
    0.093333,
    0.093333,
    0.106667,
    0.106667,
    0.106667,
    0.106667,
    0.12,
    0.146667,
    0.146667,
    0.16,
    0.16,
    0.16,
    0.186667,
    0.2,
    0.213333,
    0.213333,
    0.213333,
    0.226667,
    0.226667,
    0.24,
    0.24,
    0.24,
    0.253333,
    0.293333,
    0.293333,
    0.293333,
    0.293333,
    0.293333,
    0.306667,
    0.32,
    0.333333,
    0.333333,
    0.333333,
    0.346667,
    0.36,
    0.36,
    0.373333,
    0.386667,
    0.4,
    0.4,
    0.6,
    0.613333,
    0.626667,
    0.653333,
    0.693333,
    0.693333,
    0.706667,
    0.72,
    0.746667,
    0.813333,
    0.853333,
    0.92,
    0.96,
    0.986667
  ],
  "threshold": 0.613333
}
```

## Actual kickoff and tools per case

| Case | Crew kickoff | Actual tools | Outcome | Guardrails |
|---|---|---|---|---|
| different_ticket | True | check_support_ticket_status {"record_id": "OLA-0004"} | answered | none |
| escalated_ticket | True | check_support_ticket_status {"record_id": "OLA-0012"} | answered | none |
| fresh_conversation | True | none | clarification | none |
| injection | False | none | refused | injection_detected |
| memory_turn_1 | True | check_support_ticket_status {"record_id": "OLA-0003"} | answered | none |
| memory_turn_2 | True | check_support_ticket_status {"record_id": "OLA-0003"} | answered | none |
| memory_turn_3 | True | check_support_ticket_status {"record_id": "OLA-0003"} | answered | none |
| mixed | True | rag_lookup {"query": "Check  and explain the refund policy."}, check_support_ticket_status {"record_id": "OLA-0002"} | answered | none |
| phone_masking | True | check_support_ticket_status {"record_id": "OLA-0001"} | answered | phone_masked |
| policy | True | rag_lookup {"query": "When can a duplicate charge be refunded and how long does processing take?"} | answered | none |
| repeat_policy_1 | True | rag_lookup {"query": "When can a duplicate charge be refunded and how long does processing take?"} | answered | none |
| repeat_policy_2 | True | rag_lookup {"query": "When can a duplicate charge be refunded and how long does processing take?"} | answered | none |
| repeat_ticket_1 | True | check_support_ticket_status {"record_id": "OLA-0001"} | answered | none |
| repeat_ticket_2 | True | check_support_ticket_status {"record_id": "OLA-0001"} | answered | none |
| reset_conversation | True | none | clarification | none |
| ticket | True | check_support_ticket_status {"record_id": "OLA-0001"} | answered | none |
| unknown_ticket | True | check_support_ticket_status {"record_id": "OLA-9999"} | not_found | none |
| unsupported_question | True | rag_lookup {"query": "How can I calculate the orbital period of a planet?"} | refused | groundedness_refusal |

## Actual selected retrieval context

### policy

Masked query: When can a duplicate charge be refunded and how long does processing take?

Collection: `ola_fixed_6a3978d64ba2`; threshold 0.390774130821228; fallback False.

- Chunk `04_refund_compensation:fixed:000:f80d07bc14d4f8cb`, parent `04_refund_compensation`, cosine 0.78248781.
- Chunk `04_refund_compensation:fixed:002:01126a7ab8ef2101`, parent `04_refund_compensation`, cosine 0.49111795.
- Chunk `04_refund_compensation:fixed:001:92e90cec52f577db`, parent `04_refund_compensation`, cosine 0.48661697.

Validated response:
```json
{
  "answer": "Retrieved policy excerpts:\n[04_refund_compensation] A billing specialist may approve a refund after verifying a duplicate charge, a confirmed overcharge, or a charge for a service that was not delivered. Refund only the verified incorrect amount to the original payment method, with a target processing time of 5 to 7 business days after approval. A su\n[04_refund_compensation] ise a refund or compensation before approval, and record whether a service credit already covers the same loss to prevent duplicate reimbursement.\n[04_refund_compensation] processing time of 5 to 7 business days after approval. A support supervisor may approve goodwill compensation up to INR 200 for a documented service failure, while larger compensation requires the operations manager's approval. Do not promise a refund or compensation before approval, and record whe",
  "citations": [
    "04_refund_compensation"
  ],
  "guardrails": [],
  "outcome": "answered",
  "ticket": null
}
```

### mixed

Masked query: Check OLA-0002 and explain the refund policy.

Collection: `ola_fixed_6a3978d64ba2`; threshold 0.390774130821228; fallback False.

- Chunk `04_refund_compensation:fixed:000:f80d07bc14d4f8cb`, parent `04_refund_compensation`, cosine 0.62980485.
- Chunk `04_refund_compensation:fixed:002:01126a7ab8ef2101`, parent `04_refund_compensation`, cosine 0.58494443.
- Chunk `08_service_credit:fixed:000:73e5b77be6988721`, parent `08_service_credit`, cosine 0.48718405.

Validated response:
```json
{
  "answer": "Ticket OLA-0002: status Open; resolution_time_hours 15; escalation_score 0.240000; recommend_escalation false (score > 0.613333).\n\nRetrieved policy excerpts:\n[04_refund_compensation] A billing specialist may approve a refund after verifying a duplicate charge, a confirmed overcharge, or a charge for a service that was not delivered. Refund only the verified incorrect amount to the original payment method, with a target processing time of 5 to 7 business days after approval. A su\n[04_refund_compensation] ise a refund or compensation before approval, and record whether a service credit already covers the same loss to prevent duplicate reimbursement.\n[08_service_credit] A support supervisor may approve a noncash service credit up to INR 150 for a verified service interruption when a cash refund does not already compensate the same loss. Apply an approved service credit to the customer's fabricated capstone account balance, with validity of 30 days from issuance. Se",
  "citations": [
    "04_refund_compensation",
    "08_service_credit"
  ],
  "guardrails": [],
  "outcome": "answered",
  "ticket": {
    "days_since_created": 18,
    "error": null,
    "escalated": false,
    "escalation_score": 0.24,
    "escalation_threshold": 0.613333,
    "found": true,
    "recommend_escalation": false,
    "record_id": "OLA-0002",
    "resolution_time_hours": 15,
    "status": "Open"
  }
}
```

### unsupported_question

Masked query: How can I calculate the orbital period of a planet?

Collection: `ola_fixed_6a3978d64ba2`; threshold 0.390774130821228; fallback True.

- Chunk `06_business_hours:fixed:000:3a9ed78829619321`, parent `06_business_hours`, cosine 0.12251306.
- Chunk `08_service_credit:fixed:001:e019600e4052eaa0`, parent `08_service_credit`, cosine 0.11971521.
- Chunk `02_severity_sla:fixed:002:62fc1a72f6be9210`, parent `02_severity_sla`, cosine 0.08837545.

Validated response:
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

## Conversations — same process, independent sessions

### fresh

human: What is its status?

ai: {"answer":"Please provide a ticket ID such as OLA-0001; this conversation has no ticket reference.","outcome":"clarification","citations":[],"ticket":null,"guardrails":[]}

### multi_turn

human: Check the status of OLA-0003.

ai: {"answer":"Ticket OLA-0003: status Open; resolution_time_hours 33; escalation_score 0.213333; recommend_escalation false (score > 0.613333).","outcome":"answered","citations":[],"ticket":{"record_id":"OLA-0003","found":true,"status":"Open","resolution_time_hours":33,"days_since_created":16,"escalated":false,"escalation_score":0.213333,"escalation_threshold":0.613333,"recommend_escalation":false,"error":null},"guardrails":[]}

human: What is its escalation score?

ai: {"answer":"Ticket OLA-0003: status Open; resolution_time_hours 33; escalation_score 0.213333; recommend_escalation false (score > 0.613333).","outcome":"answered","citations":[],"ticket":{"record_id":"OLA-0003","found":true,"status":"Open","resolution_time_hours":33,"days_since_created":16,"escalated":false,"escalation_score":0.213333,"escalation_threshold":0.613333,"recommend_escalation":false,"error":null},"guardrails":[]}

human: And what is its status?

ai: {"answer":"Ticket OLA-0003: status Open; resolution_time_hours 33; escalation_score 0.213333; recommend_escalation false (score > 0.613333).","outcome":"answered","citations":[],"ticket":{"record_id":"OLA-0003","found":true,"status":"Open","resolution_time_hours":33,"days_since_created":16,"escalated":false,"escalation_score":0.213333,"escalation_threshold":0.613333,"recommend_escalation":false,"error":null},"guardrails":[]}

### reset

human: What is its status?

ai: {"answer":"Please provide a ticket ID such as OLA-0001; this conversation has no ticket reference.","outcome":"clarification","citations":[],"ticket":null,"guardrails":[]}

## Masked input and actual history

```json
[
  {
    "content": "My phone is [PHONE_MASKED]; check OLA-0001 status.",
    "role": "human"
  },
  {
    "content": "{\"answer\":\"Ticket OLA-0001: status Open; resolution_time_hours 82; escalation_score 0.093333; recommend_escalation false (score > 0.613333).\",\"outcome\":\"answered\",\"citations\":[],\"ticket\":{\"record_id\":\"OLA-0001\",\"found\":true,\"status\":\"Open\",\"resolution_time_hours\":82,\"days_since_created\":7,\"escalated\":false,\"escalation_score\":0.093333,\"escalation_threshold\":0.613333,\"recommend_escalation\":false,\"error\":null},\"guardrails\":[\"phone_masked\"]}",
    "role": "ai"
  }
]
```

The fabricated raw phone is constructed only in the test; it is absent from this report, crew inputs and history. Injection test skips kickoff/tools and does not enter history.

## Deliberate unsupported draft

```json
{
  "draft": {
    "answer": "Retrieved policy excerpts:\n[04_refund_compensation] A billing specialist may approve a refund after verifying a duplicate charge, a confirmed overcharge, or a charge for a service that was not delivered. Refund only the verified incorrect amount to the original payment method, with a target processing time of 5 to 7 business days after approval. A su\n[04_refund_compensation] ise a refund or compensation before approval, and record whether a service credit already covers the same loss to prevent duplicate reimbursement.\n[04_refund_compensation] processing time of 5 to 7 business days after approval. A support supervisor may approve goodwill compensation up to INR 200 for a documented service failure, while larger compensation requires the operations manager's approval. Do not promise a refund or compensation before approval, and record whe A refund of INR 999999 is guaranteed immediately.",
    "citations": [
      "04_refund_compensation"
    ],
    "guardrails": [],
    "outcome": "answered",
    "ticket": null
  },
  "guarded_response": {
    "answer": "I cannot answer because the draft contains unsupported claims.",
    "citations": [],
    "guardrails": [
      "groundedness_refusal"
    ],
    "outcome": "refused",
    "ticket": null
  }
}
```

Complete trusted retrieved context is in the JSON report; the injected guarantee is rejected even though the draft cites genuine policy documents. A changed ticket-status fact is separately rejected.

## Offline verification and versions

```json
{
  "acceptance": {
    "errors": 0,
    "failures": 0,
    "passed": true,
    "tests_run": 12
  },
  "offline": {
    "api_key_variables_absent": true,
    "child_process_attempts": [],
    "dns_negative_control": "blocked",
    "model_files_and_checksums_unchanged": true,
    "network_attempts": [],
    "socket_constructions": [
      "connection.py:_has_ipv6"
    ],
    "telemetry_flags_before_import": true
  },
  "python": "3.11.17",
  "versions": {
    "chromadb": "1.5.9",
    "crewai": "1.15.27",
    "crewai-core": "1.15.27",
    "langchain-core": "1.6.9",
    "langsmith": "0.14.7",
    "pydantic": "2.12.5",
    "sentence-transformers": "6.1.0"
  }
}
```

Audit begins before framework imports and model loading, denies Python DNS/internet connections/UDP sends and child processes. Recorded socket construction is a local urllib3 IPv6 probe, not traffic. Model file list and checksums are unchanged; setup downloads are separate. This is exercised-path evidence, not an OS-wide native-code firewall.

## Practical limits

MOCK_LLM provides exact retrieved excerpts and literal ticket facts; it does not synthesize claims or promise resolutions. Similarity gating was calibrated on unrelated negatives and cannot establish support for all near-domain questions. Injection patterns and fixed-format phone masking are deterministic demonstrations, not comprehensive detection of arbitrary adversarial language or free-text PII. Session routing handles explicit IDs, simple ticket pronouns and lexical policy intent; it does not attempt general language understanding. LangChain deprecation warnings are expected and retained; pinned 1.6.9 works.
