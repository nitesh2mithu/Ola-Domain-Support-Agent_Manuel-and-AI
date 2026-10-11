# Completed Ola (Business Operations / Customer Support) track — Ola Domain Support Agent

## Overview

This capstone combines local policy retrieval, ticket lookup, conversation memory, CrewAI orchestration, AutoGen review and FastAPI. All language-model stages use deterministic `MOCK_LLM`, with zero API keys or paid services.

Version 2 adds a reopening signal to escalation scoring and five separately evaluated queries. Version 1 is preserved by `v1.0.0`; its results live in [the archive](docs/archive/v1_FINAL_ACCEPTANCE_REPORT.md). Current checks and evidence belong to the improved implementation. See the [change record](docs/CHANGELOG_V2.md) and [acceptance report](docs/FINAL_ACCEPTANCE_REPORT.md).

## Quick start

Use Python 3.11; the verified environment is 3.11.17 on macOS Apple Silicon. Exact dependencies are in [requirements-api.lock](requirements-api.lock). Pins are an environment snapshot; another platform needs compatible wheels and its own environment verification.

Download packages and the public embedding model during setup only:

```sh
python3.11 -m venv .venv311
.venv311/bin/python -m pip install --cache-dir .cache/pip -r requirements-api.lock
HF_HUB_OFFLINE=0 TRANSFORMERS_OFFLINE=0 .venv311/bin/python -m scripts.download_embedding_model
```

Model: `sentence-transformers/all-MiniLM-L6-v2`, revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`. [The manifest](evidence/model_manifest.json) pins file checksums. Weights are excluded from Git; runtime loads local files only and fails if they are missing or changed.

Rebuild excluded indexes and run locally:

```sh
export MOCK_LLM=true CREWAI_DISABLE_TELEMETRY=true OTEL_SDK_DISABLED=true
.venv311/bin/python -m scripts.rebuild_indexes
.venv311/bin/python -m scripts.ask_support 'Check OLA-0001 status.' 'What is its escalation score?'
.venv311/bin/python -m scripts.ask_policy 'When can a duplicate charge be refunded?'
.venv311/bin/python -m scripts.serve_api --port 8000
```

Telemetry is disabled **before framework imports**, including CrewAI kickoff. Offline audit hooks block external networking and child processes inside runtime checks; API tests permit only their declared localhost port. Setup downloads are separate from runtime.

Reproduce verification, in order:

```sh
.venv311/bin/python -m scripts.run_final_verification
.venv311/bin/python -m scripts.run_final_verification --phase localhost
.venv311/bin/python -m scripts.verify_final_acceptance
.venv311/bin/python -m scripts.rebuild_indexes --db-dir .runtime/clean-check --report evidence/final_clean_index.json
.venv311/bin/python -m scripts.inspect_submission
.venv311/bin/python -m scripts.verify_final_documents
```

## Dataset design choices

[dataset.py](dataset.py) generates **60** fabricated tickets using seed **42** and an isolated `random.Random`. Records are generated, never hand-edited to force a distribution.

- Categories: Billing, Technical Issue, Account Access, Product Defect, General Inquiry; weights **20, 20, 20, 20, 20**.
- Statuses: Open, In Progress, Escalated, Resolved, Closed; weights **20, 25, 20, 20, 15**.
- Resolution hours: global **1–168**; Billing 4–72, Technical Issue 4–120, Account Access 1–48, Product Defect 12–168, General Inquiry 1–24. Draw uniformly within each range.
- **Range rationale:** one hour permits simple inquiries; up to a week allows specialist defect investigation. Durations are planned totals for active tickets, completed durations for terminal tickets, never guaranteed deadlines.
- Integer age: 0–30 days; terminal-ticket minimum age is `ceil(resolution_time_hours/24)`.
- Optional fabricated amount: INR **0–5000**, drawn uniformly. Escalated is true exactly for current Escalated status.
- `reopen_count`: integer 0–3 from a separate uniform stream seeded with `seed+1` (43). Original seven fields and their RNG draw order are unchanged from v1.

Category counts are **20/10/8/9/13**; status counts are **12/13/14/10/11** in the orders above. Escalation is **14/60 = 23.33%**. [Dataset and score evidence](evidence/v2_escalation_change.json) includes all records, types, exact hashes, independent calculations and reproduction checks.

## Knowledge base

[knowledge_base/](knowledge_base/) holds 12 original **fabricated capstone policies**, each four sentences. They are not official Ola policies.

Topics: priority, severity SLA, escalation matrix, refunds/compensation, communication channels, business hours/holidays, repeat complaints, service credits, feedback, VIP handling, outage communication and ticket retention. [Coverage checks](evidence/v2_escalation_dataset.json) map every topic to its document and sentence count.

## RAG

[rag/](rag/) implements fixed chunks of 300 characters with 60-character overlap, and chunks of two sentences. All chunks use real local 384-dimensional embeddings. Two separate cosine Chroma collections receive explicit vectors through `upsert`; stable chunk IDs retain parent-document mappings. The collections contain 33 fixed and 24 sentence chunks.

Retrieve top three chunks. Answers quote only retrieved evidence; below the calibrated threshold they return: “I don't know based on the available policy documents.”

Measured top-1 cosine calibration:

| Query | Scope | Fixed | Sentence |
|---|---|---:|---:|
| VIP handling | In | 0.72448504 | 0.74592054 |
| Feedback after resolution | In | 0.72365928 | 0.73351645 |
| Repeat complaint within 30 days | In | 0.68994534 | 0.68911171 |
| Photosynthesis | Out | 0.09160292 | 0.07866859 |
| Chocolate cake | Out | 0.01842099 | 0.01867789 |

Thresholds are the midpoint between the largest out-of-scope and smallest in-scope value: **fixed 0.390774130821228**, **sentence 0.38389015197753906**. These small observed clusters separate; unrelated negatives do not establish near-domain rejection.

Precision = matched parents / retrieved unique parents; recall = matched parents / labelled relevant parents. Both collections use the same frozen labels and deduplicate parent documents before scoring.

| Query | Fixed precision | Fixed recall | Sentence precision | Sentence recall |
|---|---:|---:|---:|---:|
| Q1 refunds | 1/1 | 1/1 | 1/3 | 1/1 |
| Q2 hours | 1/1 | 1/1 | 1/2 | 1/1 |
| Q3 retention | 1/1 | 1/1 | 1/2 | 1/1 |
| Q4 outage | 1/1 | 1/1 | 1/2 | 1/1 |
| Q5 credits | 1/1 | 1/1 | 1/2 | 1/1 |
| Q6 priority/SLA | 2/2 | 2/2 | 2/2 | 2/2 |

Deploy fixed chunking for this corpus: its mean precision/recall are **1.0/1.0**, compared with **0.555556/1.0** for sentence chunking. Fixed chunks introduce fewer irrelevant parents despite cutting some sentences. Reevaluate on a larger corpus before generalizing this choice.

[Detailed retrieval, fractions, six answers and held-out fallback](evidence/final_rag.md) include exact queries, retrieved IDs and arithmetic. The out-of-scope case has no relevant parents, so recall is undefined.

## Crew and tools

[support/crew.py](support/crew.py) executes real CrewAI `.kickoff()` with Retrieval, Lookup and Composer agents. Its deterministic model extends `crewai.llms.base_llm.BaseLLM`, dispatches arguments from declared schemas and consumes actual task/tool results. It avoids parsing the ReAct system-template “Observation:” example as evidence.

Retrieval uses the selected fixed index. Only Lookup can call `check_support_ticket_status(record_id: str) -> dict`; Composer has no tools. Unknown IDs return explicit not-found results with null facts.

Escalation score = `round(0.4*escalated + 0.3*(days_since_created/30) + 0.3*(reopen_count/3), 6)`. Older tickets and reopening raise triage urgency. Threshold is the nearest-rank 80th percentile: sorted score at `ceil(0.8*60)=48`, measured **0.55**. Recommend only scores strictly above it; the one equal-score tie is excluded.

There are **12 recommendations**, including two non-escalated tickets: OLA-0007 and OLA-0022 both score **0.57**. V1 recommended 12 already-escalated tickets and zero non-escalated tickets at threshold 0.613333. This is an intended heuristic change, not evidence of SLA compliance or automatic ticket mutation. [Actual crew results](evidence/v2_escalation_crew.json) and [change details](docs/CHANGELOG_V2.md) document the verification.

## Memory, schema, guardrails

LangChain `InMemoryChatMessageHistory` with `RunnableWithMessageHistory` carries ticket state across turns in one session. Fresh sessions and reset isolate state; nothing survives process restart.

Every draft and final response validates against [Pydantic models](support/models.py). Input guards mask fixed-format phone numbers and detect declared injection patterns before memory, caching, model calls or logging. Output guards reject facts unsupported by actual evidence. Free-text names, addresses and payment details are outside this fixed-format masker; examples are fabricated.

## API and logging

FastAPI exposes typed `POST /ask` and `POST /reset-session`, plus multi-turn WebSocket `/ws/chat`. Each WebSocket gets a private session; disconnect cleanup leaves other clients running. Use one worker: sessions/cache are process-local and crew execution is serialized while socket handling stays responsive.

```sh
curl --noproxy '*' -s http://127.0.0.1:8000/ask -H 'Content-Type: application/json' -d '{"session_id":"demo","query":"Check OLA-0001 status."}'
curl --noproxy '*' -s http://127.0.0.1:8000/reset-session -H 'Content-Type: application/json' -d '{"session_id":"demo"}'
```

WebSocket messages are JSON such as `{"query":"Check OLA-0001 status."}` followed by `{"query":"What is its status?"}`. [Real HTTP/WebSocket transcripts](evidence/final_localhost.json) include concurrent clients and mid-request disconnect survival.

Exactly one JSONL row per HTTP request or WebSocket user message records trace ID, duration, outcome and masked text. Masking happens before validation and error logging. Live logs stay in excluded `.runtime/`; [sanitized evidence](evidence/final_logs_localhost.jsonl) is retained.

## Evaluation

The [original 15 cases](evaluation/support_queries.json) retain all labels: 12 policy topics, two out-of-scope cases and one unknown ticket. The deterministic judge reads actual answers and executed evidence using an [explicit prompt](evaluation/judge_prompt.txt) and [unchanged rubric](evaluation/judge_rubric.md).

[Five extra cases](evaluation/extra_queries.json) add two near-domain, two multi-topic/ambiguous, and one injection/fabricated-phone case. Their parent labels, fact anchors and [refusal rules](evaluation/extra_rubric.md) were [SHA-256 frozen](evidence/v2_extra_freeze.json) before retrieval. The extension adds new refusal types; original metric rules are unchanged.

| Set | Accuracy | Grounding | Completeness | Safety |
|---|---:|---:|---:|---:|
| Original 15 | 1.0 | 1.0 | 1.0 | 1.0 |
| Additional 5 | 0.8 | 1.0 | 0.7 | 1.0 |

Accuracy is precision-like over expected facts and unsupported claim units; Completeness separately measures expected-fact coverage. A supported partial answer can have Accuracy=1 and lower Completeness. Each set has its own denominator; no pooling or dropping weak cases.

X01 returns supported refund excerpts but fails the expected refusal for an undocumented cancellation entitlement. X04 covers only two of four holiday/VIP/outage facts. Grounding=1 does not mean the answer addresses the question. No labels, threshold or crew behavior were tuned after these results.

[Original per-query scores](evidence/v2_original_evaluation.md), [additional per-query scores](evidence/v2_extra_evaluation.md) and [flawed-answer fixtures](evidence/v2_judge_fixtures.json) show calculations and sensitivity to incorrect numbers, unsupported inference, omissions, unsafe requests and forged guard evidence.

```sh
.venv311/bin/python -m scripts.evaluate_support --report evidence/v2_original_evaluation.json
.venv311/bin/python -m scripts.evaluate_extra
.venv311/bin/python -m tests.v2_evaluation
```

## Review stage, governance and cache

AutoGen runs a real two-agent `RoundRobinGroupChat(max_turns=2)` after Composer, using original tool context. Final Editor emits a registered `StructuredMessage[VerdictModel]` with `approved`, `final_answer`, `reason`. Tests demonstrate unchanged approval and revision of a deliberately unsupported claim; final guards remain active.

Four governance layers: Data uses fabricated records, pinned policies and masked inputs; Model uses local evidence-only adapters and independent review; Application binds the ticket tool to the actual Lookup identity; Runtime enforces offline controls and shared token/cost caps. The brief names Application/Runtime explicitly; Data/Model are this project's mapping of the other two layers.

Domain risk is **Medium**, since incorrect customer-support advice can affect customers. Operational autonomy is **Low**: tools are read-only; the application cannot refund, mutate records, delegate freely or deploy services.

Per-request caps are 50,000 simulated tokens and USD 0.10 across CrewAI and review. Tokens use `ceil(serialized_characters/4)` per input/output; simulated price is USD 0.002/1,000 units. Actual monetary spend is zero. Atomic reservations reject oversized requests before exceeding a cap.

The in-memory policy cache normalizes queries and fingerprints evidence/configuration. Ticket data and session-specific final responses are never shared. A policy hit reduces crew model calls **4→3** and RAG tool calls **1→0**, while both review calls remain. Guards run before lookup; validation and request logging remain active on hits. [Review, permission, budget and cache evidence](evidence/final_acceptance.json) contains actual counters and rejection cases.

## Limitations

MOCK scores are lexical/extractive proxies on a small known corpus, not semantic quality or adversarial robustness. Fixed excerpts can repeat or cut sentences; review may reject valid paraphrases. Near-domain scope and multi-topic coverage remain measured weaknesses. Pattern guards and static secret scanning are bounded.

Python audit hooks cover exercised Python calls, not arbitrary native-code traffic or an OS firewall. Sessions/cache have no persistence or production authentication. Pinned LangChain deprecations remain functional; a narrow CrewAI credential-storage shim keeps generated local keys in excluded runtime storage.

## What I learned

[LEARNINGS.md](docs/LEARNINGS.md) explains findings supported by executed checks: corpus-dependent chunking, calibration limits, a documented lookup bug and changes needed for a real LLM. It does not attribute personal experiences to the student.

## AI assistance note

AI assistance contributed to scaffolding, dataset and policy drafting, implementation, debugging, test execution and documentation/review. Generated work was verified through executed checks, including preserved failures and negative fixtures. The record does not establish which design or testing work the student performed personally.

**[CONFIRM: my own contributions]**
