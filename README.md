# Completed Ola (Business Operations / Customer Support) track — Ola Domain Support Agent

Certification Program in Agentic Systems and Design — iHUB DivyaSampark, IIT Roorkee.
Submission deadline: **8 November 2026**. Milestones 1–6 implement framework smoke tests, dataset/policies, Part 1 local RAG, Part 2 crew/tools/memory/guardrails, Part 3 localhost FastAPI/logging/evaluation, and Part 4 review/governance/cache. All16 implementation tasks passed the complete final acceptance audit. Local submission preparation passed; public repository publication/submission remains pending.


## Start here — clean checkout setup and final verification

The completed-track declaration follows the executed all16-task audit in [FINAL_ACCEPTANCE_REPORT.md](FINAL_ACCEPTANCE_REPORT.md). Part marks are30/30/20/20; the brief gives no per-task marks, and this project does not claim an awarded score. The required public GitHub link is still pending user-approved publication; local readiness is not a claim that submission has already occurred.

Use Python **3.11** (verified3.11.17), from the project root. The repository contains code/text/evidence only. Virtual environments, downloaded Python, package caches, model weights, index databases, credentials, live logs and editor/session files are excluded.

**Online setup only**, once on a new checkout (no paid service or API key):

```sh
python3.11 -m venv .venv311
.venv311/bin/python -m pip install --cache-dir .cache/pip -r requirements-api.lock
HF_HUB_OFFLINE=0 TRANSFORMERS_OFFLINE=0 .venv311/bin/python -m scripts.download_embedding_model
```

`requirements-api.lock` is the exact verified163-package snapshot; `requirements-api.txt` and its included direct requirements document the smaller explicit dependency set. The snapshot was verified on macOS Apple Silicon/Python3.11; another OS may require compatible wheel availability and a separately recorded environment audit. If using uv rather than pip, run `uv venv .venv311 --python 3.11 --cache-dir .cache/uv` then `uv pip install --python .venv311/bin/python --cache-dir .cache/uv -r requirements-api.lock` during setup. uv-created environments need not contain pip.

The download script reads the tracked model manifest and pins **sentence-transformers/all-MiniLM-L6-v2**, revision **1110a243fdf4706b3f48f1d95db1a4f5529b4d41**, into `.models/all-MiniLM-L6-v2`. Runtime verifies listed file hashes and loads local files only; it never substitutes a remote/default model. Do not call the setup downloader during runtime. Package/model downloads are authorized setup traffic, distinct from acceptance evidence of offline execution.

**Offline index rebuild**, once after model setup:

```sh
.venv311/bin/python -m scripts.rebuild_indexes
```

This creates both33-chunk fixed and24-chunk sentence Chroma collections via real `upsert`, preserves the tracked measured calibration and checks sensible retrieval. Missing model fails locally; changed corpus/model fingerprint refuses rebuild against the old calibration and requires an explicitly reported recalibration. The final audit also rebuilt a separate initially empty local index (`evidence/final_clean_index.json`); no downloaded weights/database need to be committed.

**Offline application and complete verification:**

```sh
.venv311/bin/python -m scripts.ask_support 'Check OLA-0001 status.' 'What is its escalation score?'
.venv311/bin/python -m scripts.ask_policy 'When can a duplicate charge be refunded and how long does processing take?'
.venv311/bin/python -m scripts.run_final_verification
.venv311/bin/python -m scripts.run_final_verification --phase localhost
.venv311/bin/python -m scripts.verify_final_acceptance
.venv311/bin/python -m scripts.inspect_submission
```

The orchestrator starts separate audited Python processes, records actual commands/exit codes, and stops on failure. It runs dataset and crew twice, both-strategy RAG/calibration/arithmetic, API/log/judge fixtures, integrated review/governance/cache, framework smoke and all15 evaluation queries twice. The localhost phase starts and stops a real Uvicorn listener/HTTP/WebSocket clients on one ephemeral127.0.0.1 port; a restricted environment must permit that local listener. Every framework child installs its external-network audit before imports; child subprocess execution is blocked. The parent orchestrator only starts local verification processes and does not itself perform model/network requests. `verify_final_acceptance` independently checks protected hashes, report equality, parent-deduplicated retrieval math, all15 score sums/averages using Decimal, actual review/counters/budgets, and exactly-once real API logging.

For a manual localhost demo:

```sh
.venv311/bin/python -m scripts.serve_api --port 8000
# In another terminal:
curl --noproxy '*' -s http://127.0.0.1:8000/ask -H 'Content-Type: application/json' -d '{"session_id":"demo","query":"Check OLA-0001 status."}'
curl --noproxy '*' -s http://127.0.0.1:8000/reset-session -H 'Content-Type: application/json' -d '{"session_id":"demo"}'
```

WebSocket `/ws/chat` accepts text JSON `{"query":"Check OLA-0001 status."}` then `{"query":"What is its status?"}` on the same connection; it assigns an isolated private session. Actual client execution and mid-request disconnect recovery are reproduced by the localhost phase and recorded in `evidence/final_localhost.json`. Stop the server with Ctrl-C. Use one worker: memory/cache are process-local, and the API serializes crew execution for correctness while keeping socket handling responsive.

Individual evaluation/reproduction commands:

```sh
.venv311/bin/python -m scripts.evaluate_support --report evidence/final_evaluation.json
.venv311/bin/python -m scripts.evaluate_support --report evidence/final_evaluation_repeat.json
.venv311/bin/python -m scripts.verify_final_acceptance
```

Results are exact-repeat comparable except intentionally nondeterministic trace IDs, wall-clock timing and ephemeral listener ports. Full dataset/uncached crew/evaluation reports match across fresh processes; shared-cache misses/hits have explicitly different call counts. Archived milestone verifiers have historical source/status/no-Git assumptions; use the final verifier for this completed application.

Architecture: masked input → session planning → real sequential CrewAI Retrieval/Lookup/Composer → real two-turn AutoGen Reviewer/Final Editor → Pydantic final validation and evidence guard → session reply. Policy-only cache reuses grounded retrieval artifacts; ticket lookup stays fresh. JSONL logging belongs to the HTTP/WS boundary, including refusals/errors/cache hits. Budget accounting spans all crew/review calls. Detailed measured design, governance and limits follow below.

## Current scope

`dataset.py` supplies 60 fabricated tickets; `knowledge_base/` contains 12 original policies; `rag/` provides two evaluated local Chroma indexes. `support/` implements real Retrieval, Lookup and Response Composer agents via CrewAI `.kickoff()`, using the recommended fixed collection, schema-driven deterministic BaseLLM tool calling, read-only ticket triage, LangChain session history, strict Pydantic responses and input/output guardrails. The earlier one-agent CrewAI echo and two-agent AutoGen smoke tests remain independent regression checks; `api/` wraps the fixed crew with HTTP/WebSocket interfaces and masked JSONL logging; `evaluation/` and `scripts/evaluate_support.py` evaluate exactly 15 queries with an explicit deterministic judge prompt. Part 4 integrates full two-agent AutoGen review, governance and policy-only grounded-generation caching; publication awaits separate approval.

## Dataset design — Task 1

- Seed: **42**; records: **60**; local generator: `random.Random(seed)`, with no use of the global RNG.
- Category order: Billing, Technical Issue, Account Access, Product Defect, General Inquiry. Weights: **20, 20, 20, 20, 20** (20% each).
- Status order: Open, In Progress, Escalated, Resolved, Closed. Weights: **20, 25, 20, 20, 15** (percentages; weights total 100).
- `escalated` is a boolean representing **current** escalation: true exactly when status is Escalated. The 20% Escalated status weight targets an escalation rate within the required 10–30% band. No separate independent flag draw, historical escalation claim or hand-edited tickets.
- `resolution_time_hours` is an integer planned total resolution duration for open tickets and the completed duration for terminal tickets; it is not elapsed time, remaining time or a customer guarantee. Global range: **1–168 hours**, with uniform draws within each category's range below.
- `days_since_created` is an integer uniformly sampled from **0–30** for active tickets; for Resolved/Closed tickets its lower bound is `ceil(resolution_time_hours / 24)`, so completed duration fits within ticket age.
- Optional `amount_inr`: uniformly sampled integer **INR 0–5000**, a fabricated associated service amount with no actual payment details. The brief requests an amount range in README but does not require an amount field; this extra field makes that choice explicit. It does not affect category, status or escalation rules.
- Draw order per record: weighted category, weighted status, resolution hours, creation age, amount; record ID is `OLA-0001` onward. Each call returns a new list. Preserve these choices and Python 3.11 runtime for deterministic reproduction.
- If a changed seed or weight fails a required distribution, validation rejects it: adjust the seed/weights and regenerate the entire list, never edit individual records. Seed 42 passed on the first draw.

| Category | Resolution-time range (hours) |
|---|---:|
| Billing | 4–72 |
| Technical Issue | 4–120 |
| Account Access | 1–48 |
| Product Defect | 12–168 |
| General Inquiry | 1–24 |

**Range rationale:** A 1–168-hour range allows simple inquiries to finish within a day while difficult product defects can require up to a week of specialist investigation.

These are illustrative dataset durations in elapsed hours; the policy documents separately define severity-based SLA targets in elapsed or support hours. Category-based draws do not establish SLA compliance, since this dataset has no severity or actual business-calendar timestamps.

Measured first-draw category counts: Billing **20**, Technical Issue **10**, Account Access **8**, Product Defect **9**, General Inquiry **13**. Status counts: Open **12**, In Progress **13**, Escalated **14**, Resolved **10**, Closed **11**. Escalation percentage: **14 / 60 × 100 = 23.33%**. Equal category probabilities need not produce equal counts in a finite sample.

```sh
.venv311/bin/python dataset.py
.venv311/bin/python dataset.py --json
.venv311/bin/python -m tests.milestone_02_acceptance
```

The first command validates and prints counts, percentage and a canonical dataset SHA-256; the second exports the complete validated list. All Milestone 2 implementation and checks use the standard library, no model/API or package download.

## Original policy knowledge base — Task 2

The 12 Markdown documents in `knowledge_base/` are **fabricated capstone policies authored for this project, not official Ola policies**. Each file has one descriptive heading and four complete policy sentences. The acceptance report maps every required topic to its file and lists the body sentences for inspection.

| Required topic | Document |
|---|---|
| Ticket priority | `knowledge_base/01_ticket_priority.md` |
| Severity SLA | `knowledge_base/02_severity_sla.md` |
| Escalation matrix | `knowledge_base/03_escalation_matrix.md` |
| Refunds and compensation | `knowledge_base/04_refund_compensation.md` |
| Communication channels | `knowledge_base/05_communication_channels.md` |
| Business hours and holidays | `knowledge_base/06_business_hours.md` |
| Repeat complaints | `knowledge_base/07_repeat_complaints.md` |
| Service credits | `knowledge_base/08_service_credit.md` |
| Feedback | `knowledge_base/09_feedback.md` |
| VIP handling | `knowledge_base/10_vip_handling.md` |
| Outage communication | `knowledge_base/11_outage_communication.md` |
| Ticket retention | `knowledge_base/12_ticket_retention.md` |

Standard support-hour clocks and business-day refund clocks are defined separately in the business-hours document. VIP service does not override severity or compensation eligibility; refunds and service credits cannot reimburse the same loss twice. No real customer names, phone numbers, addresses, payment details or credentials are included.

## Verified environment

- CPython 3.11.17 in `.venv311`.
- CrewAI / crewai-core 1.15.27.
- AutoGen AgentChat / Core 0.7.5.
- Pydantic 2.12.5.
- Current direct additions: `requirements-crew.txt`; Part 2 snapshot: `requirements-crew.lock` (162); current 163-package snapshot: `requirements-api.lock`. Earlier `requirements-smoke.lock` (139) and `requirements-rag.lock` (153) are historical snapshots. LangChain Core 1.6.9 is installed for session memory.
- Activate with `source .venv311/bin/activate`. The earlier Python 3.14 `.venv` is retained; use `.venv311` for smoke tests.

## Setup downloads (network required, separate from runtime)

Executed setup commands are in `DEVELOPMENT_PROCESS.md`; download summary is `evidence/milestone_01_downloads.txt`. On this workstation:

```sh
.bootstrap/packages/bin/uv python install 3.11 --install-dir .python --cache-dir .cache/uv --no-bin
.bootstrap/packages/bin/uv venv .venv311 --python .python/cpython-3.11.17-macos-aarch64-none/bin/python3.11 --cache-dir .cache/uv
.bootstrap/packages/bin/uv pip install --python .venv311/bin/python --cache-dir .cache/uv -r requirements-smoke.lock
```

The interpreter path above is specific to macOS Apple Silicon. Another machine needs its platform's Python 3.11 interpreter. Dependency pins are an environment snapshot, not a cross-platform wheel bundle. uv's bootstrap was downloaded inside `.bootstrap/packages`; uv executable 0.13.0 performs setup, while CrewAI transitively installed uv 0.11.33 inside `.venv311`.

## Offline runtime checks

```sh
.venv311/bin/python -m smoke_tests.run_offline
```

The runner sets `MOCK_LLM=true`, `CREWAI_DISABLE_TELEMETRY=true`, `OTEL_SDK_DISABLED=true`, and `CREWAI_TRACING_ENABLED=false` **before importing CrewAI**. It removes API-key environment variables without logging their values. Both model adapters are local; no external provider client is created and no API keys are required.

A Python audit hook is active before framework imports. It denies DNS, internet socket connections, UDP sends, and child processes. Negative controls deliberately attempt each blocked operation. Framework activity must record zero prohibited attempts. Local socket creation/binding for urllib3's IPv6 capability probe and asyncio AF_UNIX wakeup sockets are distinct from outbound traffic.

This verifies the exercised Python framework path; the audit hook is not an OS-wide firewall and does not claim coverage of arbitrary native-code system calls or the future full application. No models are downloaded at runtime. The local embedding runtime and expanded three-agent crew have also been verified below.

## Compatibility note

Pinned CrewAI initializes credential storage during import even when tracing is disabled. Its macOS credential directory is hard-coded and does not honor `CREWAI_STORAGE_DIR`. `smoke_tests/runtime.py` includes a narrowly scoped directory shim that redirects only credential storage into gitignored `.runtime/crewai/credentials`. It does not mock framework execution, model routing, or tool calls. Generated local encryption keys are never included in evidence or Git.

## Review and evidence

Start with `PROJECT_STATUS.md` and its CHATGPT REVIEW HANDOFF. Follow `DEVELOPMENT_PROCESS.md`, `ERROR_LOG.md`, and `REQUIREMENTS_TRACKER.md` for history and official acceptance coverage. Full smoke results, including preserved failed attempts, are under `evidence/`.

**Milestone 2 PASSED:** Tasks 1 and 2 were verified with 8/8 acceptance tests in each of two separate Python processes; complete reports match exactly. Dataset canonical SHA-256: `359ce560dcc70008c7fa5f00dc913374b5d90db74815a7f726b4ef1e1e9d8111`.

- Test transcript: [acceptance](evidence/milestone_02_acceptance.txt).
- Complete record/type/range/topic/sentence evidence: [acceptance JSON](evidence/milestone_02_acceptance.json).
- Independent rerun: [regeneration transcript](evidence/milestone_02_regeneration.txt), [regeneration JSON](evidence/milestone_02_regeneration.json).
- Cross-process comparison: [comparison](evidence/milestone_02_regeneration_comparison.txt).

Reproduce the saved evidence:

```sh
.venv311/bin/python -m tests.milestone_02_acceptance --report evidence/milestone_02_acceptance.json
.venv311/bin/python -m tests.milestone_02_acceptance --report evidence/milestone_02_regeneration.json
.venv311/bin/python -c 'import json; from pathlib import Path; assert json.loads(Path("evidence/milestone_02_acceptance.json").read_text()) == json.loads(Path("evidence/milestone_02_regeneration.json").read_text()); print("PASS: independent reports match")'
```

Observed hours are 1–161, creation ages 0–30, and amounts INR 325–4988; configured generation ranges are documented above. Every required field has the expected type in all 60 records. All 12 documents have four body sentences and required topic content. Tests also reject malformed fixtures and verify RNG isolation. The Python audit recorded zero network or child-process attempts during both acceptance runs; no packages or models were downloaded in Milestone 2.

Official Tasks 1–13 are now PASSED after Milestone 5 verification. Tasks 14–16 PASSED after Milestone 6 executed acceptance; current status is in PROJECT_STATUS.md. No per-task marks are assigned by the brief, and no earned-marks claim is made.

## Part 1 local RAG — Tasks 3–5

Prerequisites were rechecked before implementation: Tasks 1/2 passed all 8 acceptance tests again, with evidence in [prerequisite transcript](evidence/milestone_03_prerequisite.txt).

### Setup downloads and identity

Use existing `.venv311` Python 3.11.17. Embedding model: **sentence-transformers/all-MiniLM-L6-v2**, exact revision **1110a243fdf4706b3f48f1d95db1a4f5529b4d41**, 384 dimensions, loaded on CPU from `.models/all-MiniLM-L6-v2`. The model manifest records the revision and SHA-256 for every downloaded tokenizer/config/weight file, including the 90,868,376-byte safetensors weight file.

Verified packages: SentenceTransformers **6.1.0**, Torch **2.14.1**, Transformers **5.19.0**, Chroma **1.5.9**, NumPy **2.4.6**, huggingface-hub **1.33.0**. Direct pins are in `requirements-rag.txt`; full 153-package environment snapshot is `requirements-rag.lock`. Resolver changed huggingface-hub from 2.2.0 to 1.33.0; dependency checks and all six existing framework smoke tests passed afterward.

Online setup only:

```sh
.bootstrap/packages/bin/uv pip install --python .venv311/bin/python --cache-dir .cache/uv -r requirements-rag.lock
.venv311/bin/python -m scripts.download_embedding_model
```

Package caches, downloaded model and Chroma runtime storage stay inside the project and are gitignored. Model setup reuses the manifest's revision; runtime never calls the download script. See [package setup](evidence/milestone_03_install.txt), [model setup](evidence/milestone_03_model_setup.txt), [model identity/checksums](evidence/milestone_03_model_manifest.json) and [dependency compatibility](evidence/milestone_03_dependency_check.txt).

### Chunking and actual indexing

- Fixed: **300 characters with 60-character overlap**, stride 240; final chunk may be shorter. Across the 12 documents: **33 chunks**.
- Sentence: **two complete sentences per chunk**, no overlap; corpus contains no dotted abbreviations. Across the 12 documents: **24 chunks**.
- Both use the same original body text and the policy heading as an embedding prefix. Exact body offsets and source/parent IDs are retained.
- Chunk IDs include parent ID, strategy, ordinal and content/offset digest. Collection fingerprint includes corpus/chunk content and model revision; changed inputs receive separate index names rather than silently mixing stale records.
- Separate persistent collections: `ola_fixed_6a3978d64ba2` and `ola_sentence_6a3978d64ba2`, stored under `.runtime/rag/chroma`.
- Real SentenceTransformer embeddings are normalized and supplied explicitly to `collection.upsert()`. `embedding_function=None` prevents Chroma default-model downloads; HNSW distance is explicitly cosine and similarity is **1 − cosine distance**.
- Re-upserting preserves counts and IDs; stored-vector dot-product checks verify reported cosine similarities. Top-k is **3 chunks**, not three deduplicated documents.

### Measured fallback calibration

Queries/labels were defined from KB content before any retrieval and remain unchanged in `evaluation/rag_queries.json`. Their recorded SHA-256 is `b1740a9fc39295b218ac387bd2b39138f8f158080ab39e39049d01a59845c3b7`. Calibration uses three supported queries and two unrelated queries; the six supported evaluation queries and one fallback query are separate.

| Calibration question | Scope | Fixed top-1 cosine | Sentence top-1 cosine |
|---|---|---:|---:|
| How should support handle a verified VIP customer? | In | 0.72448504 | 0.74592054 |
| How is customer feedback collected after a ticket is resolved? | In | 0.72365928 | 0.73351645 |
| What should happen when the same customer repeats a complaint within 30 days? | In | 0.68994534 | 0.68911171 |
| Explain photosynthesis in plants. | Out | 0.09160292 | 0.07866859 |
| How do I bake a chocolate cake? | Out | 0.01842099 | 0.01867789 |

Fixed threshold is **(0.09160292148590088 + 0.6899453401565552) / 2 = 0.390774130821228**. Sentence threshold is **(0.07866859436035156 + 0.6891117095947266) / 2 = 0.38389015197753906**. Neither observed cluster overlaps: fixed gap is 0.59834242 and sentence gap is 0.61044312; no preset threshold or post-result label/chunk tuning was used.

If future calibration clusters overlap, the code records the measurements, leaves threshold null and fails acceptance; it does not claim a separating cutoff. These unrelated negatives establish separation only for this declared sample, not for ambiguous near-domain requests. The held-out orbital-period question also falls below both thresholds (fixed 0.12251306, sentence 0.12519479) and returns **“I don't know based on the available policy documents.”**

### Answers and document-level evaluation

`grounded_answer` is deterministic extractive MOCK_LLM generation: it quotes only actual retrieved body slices with parent citations. It neither uses relevance labels to compose answers nor invents policy facts. Fixed-size excerpts may begin/end mid-sentence; the output labels them as excerpts and retains the retrieved text for inspection.

The six in-scope queries cover refunds, business hours, retention, outages, service credits, and the combined priority/SLA question. Both indexes answer all six without fallback and retrieve a relevant top-1 parent; the seventh unrelated query falls back. [Full readable report](evidence/milestone_03_rag.md) includes exact queries, all retrieved chunk/parent IDs, cosine values, verbatim answers and per-query arithmetic; [JSON evidence](evidence/milestone_03_rag.json) includes the complete chunk manifest and measurements.

Relevance is assigned to documents containing facts needed for the question, rather than every cross-referenced policy. Map retrieved chunks to parent IDs and deduplicate before computing precision = matched parents / retrieved parents and recall = matched parents / relevant parents. Macro averages below cover exactly Q1–Q6; fallback Q7 has no relevant documents, so its recall is undefined and it is excluded from those averages.

| Query | Fixed precision | Fixed recall | Sentence precision | Sentence recall |
|---|---|---|---|---|
| Q1 refund | 1/1 = 1.0000 | 1/1 = 1.0000 | 1/3 = 0.3333 | 1/1 = 1.0000 |
| Q2 hours | 1/1 = 1.0000 | 1/1 = 1.0000 | 1/2 = 0.5000 | 1/1 = 1.0000 |
| Q3 retention | 1/1 = 1.0000 | 1/1 = 1.0000 | 1/2 = 0.5000 | 1/1 = 1.0000 |
| Q4 outage | 1/1 = 1.0000 | 1/1 = 1.0000 | 1/2 = 0.5000 | 1/1 = 1.0000 |
| Q5 credit | 1/1 = 1.0000 | 1/1 = 1.0000 | 1/2 = 0.5000 | 1/1 = 1.0000 |
| Q6 priority/SLA | 2/2 = 1.0000 | 2/2 = 1.0000 | 2/2 = 1.0000 | 2/2 = 1.0000 |
| Macro mean | **1.0000** | **1.0000** | **0.5556** | **1.0000** |

**Deployment recommendation:** Deploy fixed chunking: fixed chunks achieved mean document precision 1.0000 and recall 1.0000, while sentence chunks achieved precision 0.5556 and recall 1.0000 on the same six labelled queries. Selection prioritizes recall and then precision, with complete sentence boundaries breaking metric ties. These small-corpus measurements support this deployment choice but do not establish performance on broader or near-domain questions.

### Offline execution and reproducible commands

```sh
.venv311/bin/python -m tests.milestone_03_acceptance
.venv311/bin/python -m scripts.ask_policy 'When can a duplicate charge be refunded and how long does processing take?'
.venv311/bin/python -m scripts.ask_policy 'How can I calculate the orbital period of a planet?'
.venv311/bin/python -m scripts.ask_policy 'How often must outage notices be updated?' --strategy sentence
```

The acceptance command explicitly builds/upserts both indexes, calibrates, evaluates, saves evidence and writes `rag/calibration.json`. The query CLI opens the persisted indexes, checks the input/model fingerprint and uses the measured thresholds; it requires prior indexing and never silently downloads or rebuilds. Model loading uses `local_files_only=True`, `trust_remote_code=False`, CPU execution, project-local caches and model-integrity verification; a missing model fails locally with setup instructions.

Before library imports, runtime disables Hugging Face/Chroma/CrewAI telemetry and sets offline flags; API-key environment variables are removed without printing secrets. A process audit denies DNS, internet connect/sendto and child processes; actual imports/embeddings/upserts/retrieval/answers record zero prohibited attempts, and a deliberate DNS negative control proves blocking. Runtime verifies model filenames and checksums remain unchanged; no runtime model or package downloads occur. This verifies the exercised Python path and does not describe the audit as an OS-wide native-code firewall.

Milestone 3 evidence: [acceptance transcript](evidence/milestone_03_acceptance.txt), [initial build report](evidence/milestone_03_rag_initial.json), [full report](evidence/milestone_03_rag.json), [framework regression](evidence/milestone_03_framework_regression.txt), [in-scope CLI](evidence/milestone_03_cli_in_scope.txt), [fallback CLI](evidence/milestone_03_cli_fallback.txt). Tasks 3–5 are marked PASSED only after successful executed checks; Milestone 3 was limited to Part 1; Part 2 is documented next. Part 3 API/logging/evaluation follows below; governance/cache remain unimplemented.

Official references consulted: [CrewAI custom LLM](https://docs.crewai.com/en/learn/custom-llm), [AutoGen model client](https://microsoft.github.io/autogen/stable/reference/python/autogen_core.models.html), [AutoGen teams](https://microsoft.github.io/autogen/stable/reference/python/autogen_agentchat.teams.html).

## Part 2 CrewAI orchestration — Tasks 6–10

**Milestone 4 PASSED:** prerequisites Tasks 1–5 were reverified first (8/8 dataset/policy +8/8 RAG). The expanded acceptance suite passed **12/12 in each of two fresh processes**, with identical complete reports across 18 cases; previous framework regression passed 6/6. The official problem statement, seeded data, original policies, model revision and evaluated fixed-collection configuration remain unchanged.

### Setup additions, separate from offline runtime

Only LangChain Core was requested; the resolver installed **langchain-core 1.6.9** and eight transitive packages without changing any of the previous 153 package versions. The exact 162-package environment is in `requirements-crew.lock`; delta and compatibility are in [dependency changes](evidence/milestone_04_dependency_changes.json) and [dependency check](evidence/milestone_04_dependency_check.txt). No embedding model download was necessary.

Executed online setup:

```sh
.bootstrap/packages/bin/uv pip install --python .venv311/bin/python --cache-dir .cache/uv langchain-core
```

For a reproducible compatible environment use the same uv command with `-r requirements-crew.lock`. All package caches and installations stay inside the project. [Actual setup output](evidence/milestone_04_install.txt) is separate from runtime evidence. LangChain's `RunnableWithMessageHistory` and, in this installed version, `InMemoryChatMessageHistory` emit deprecation warnings; they function correctly in pinned 1.6.9. Warnings are retained, as the brief permits; migration would be needed before a future 2.0 upgrade. The prior CrewAI credential-directory shim is still required for the pinned macOS installation.

### Ticket tool and escalation formula — Task 6

`support/tickets.py` implements `check_support_ticket_status(record_id: str) -> dict`. Known tickets return actual `status`, `resolution_time_hours`, `days_since_created`, `escalated`, designed `escalation_score`, threshold and `recommend_escalation`. Unknown and malformed IDs return `found=false`, an explicit error and null ticket facts; they never invent a status or duration. IDs are trimmed/case-normalized. Invalid non-string arguments fail clearly.

Exact formula:

```python
normalized_recency = 1 - days_since_created / 30
age_signal = 1 - normalized_recency
escalation_score = round(0.6 * int(escalated) + 0.4 * age_signal, 6)
recommend_escalation = escalation_score > 0.613333
```

The implementation uses the algebraically equivalent `round(0.6*int(escalated) + 0.4*(days_since_created/30), 6)` to avoid unnecessary floating-point subtraction. Scores range from 0 to 1; an existing escalation carries the larger weight, while older tickets have greater review urgency. Resolution hours retain their dataset meaning (planned total or completed duration), rather than becoming a remaining-time promise.

The threshold is computed from this dataset's **nearest-rank 80th-percentile score**, rank `ceil(0.8*60)=48`, score **0.613333**. Exactly **12/60=20%** exceed it; one ticket equals it and is not recommended because the rule is strictly above. All 12 selected tickets already have Escalated status; non-escalated tickets score at most 0.4, so this conservative rule prioritizes escalation review rather than newly escalating ordinary tickets. It is a documented capstone triage heuristic, not a learned prediction, SLA-breach calculation or record-changing action. [Actual distribution and all 60 lookup results](evidence/milestone_04_acceptance.json) include independent formula/percentile verification.

### Real framework flow and responsive MOCK_LLM — Task 7

| Agent | Tool | Framework output |
|---|---|---|
| Retrieval Agent | `rag_lookup(query: str)` | Actual top-3 fixed-collection hits and calibrated verbatim excerpts/fallback |
| Lookup Agent | `check_support_ticket_status(record_id: str)` | Actual generated ticket facts or unknown-ID result |
| Response Composer | No tool; consumes both preceding Task outputs | Combined strict `SupportResponse` draft |

All three agents execute sequential CrewAI tasks through `.kickoff()` for an accepted request. Irrelevant stages return an explicit not-requested result; they do not fabricate a tool invocation. Distinct policy/status samples prove each real tool call, while a mixed request proves the Composer combines both outputs. Tools operate on the existing dataset/index, without rebuilding policies or indexing during a request.

`support/crew.py:MOCK_LLM` extends `crewai.llms.base_llm.BaseLLM`, returns native tool-call requests, then consumes CrewAI's actual role=`tool` messages. Arguments come from the declared required-field schema, so a RAG tool named `rag_lookup` still receives `query`, never `record_id`. The adapter ignores the ReAct system-template Observation example and consumes actual preceding Task.output context in the Composer. Query text, selected ticket reference and real evidence drive results; no test-query answer dictionary is used. At the historical Milestone 4 baseline both caches were disabled. Milestone 6 adds only the policy grounded-generation cache described below; the crew framework cache remains disabled.

### Session memory and schema — Tasks 8/9

`SupportSession` uses LangChain `InMemoryChatMessageHistory` and `RunnableWithMessageHistory` around real kickoff, keyed by session ID. The wrapper supplies prior history to query planning and appends masked user text plus the validated AI response. A simple ticket-pronoun follow-up resolves the last structured ticket reference in that session; a fresh session asks for an ID, and `reset(session_id)` clears history. Memory survives only inside one process; each CLI invocation starts fresh.

`support/models.py` declares `response_format = SupportResponse` (Pydantic BaseModel), with `answer`, enumerated `outcome`, parent `citations`, typed `ticket`, and `guardrails`. Every Composer task has `output_pydantic=SupportResponse`; code explicitly validates `.kickoff().raw`, checks the framework's Pydantic object, validates the guarded final response, and validates the session-boundary response. Intermediate task outputs use `StageResult`; ticket facts use `TicketResult`, including bounded scores and known/unknown consistency. Tests reject invalid outcomes, extra fields, out-of-range scores and fabricated facts for missing tickets.

### Guardrails — Task 10

- **Phone masking:** fixed-format Indian ten-digit mobile numbers (optional +91/91 prefix and spaces/hyphens) become `[PHONE_MASKED]` before crew planning, model inputs or LangChain history. The deliberate fabricated example fires the guardrail; neither the result nor stored transcript contains its raw value. Free-text names, addresses and payment details remain outside fixed-format masking, as specified by the brief; no real examples are used.
- **Injection detection:** deterministic patterns detect attempts to ignore prior instructions, reveal system prompts/secrets or disable safeguards. A deliberate injection is refused before kickoff/tool execution and is not appended to history.
- **Groundedness:** below the existing measured similarity threshold, policy answers refuse with the Part 1 fallback. The output boundary also compares the entire draft and structured facts with exact evidence-only rendering from actual executed tools. Genuine citations do not authorize extra claims: a deliberately injected immediate INR 999999 refund guarantee is refused, as is a fabricated changed ticket status. In a mixed request, supported ticket facts can still be returned with an explicit refusal for unsupported policy content.

This is deterministic extractive support, not general question answering: fixed chunks may be partial sentences, and similarity calibration with unrelated negatives does not prove support for every near-domain question. Pattern-based injection detection is a bounded demonstration, not complete adversarial-language detection. Query planning covers explicit ticket IDs, simple ticket pronouns and lexical policy intent; general conversational disambiguation is not established.

### Reproduce runtime, transcripts and acceptance

```sh
.venv311/bin/python -m tests.milestone_04_acceptance --report evidence/milestone_04_acceptance.json
.venv311/bin/python -m tests.milestone_04_acceptance --report evidence/milestone_04_regeneration.json
.venv311/bin/python -c 'import json; from pathlib import Path; assert json.loads(Path("evidence/milestone_04_acceptance.json").read_text()) == json.loads(Path("evidence/milestone_04_regeneration.json").read_text()); print("PASS: complete reports match")'
.venv311/bin/python -m scripts.ask_support 'Check OLA-0001 status.' 'What is its escalation score?'
.venv311/bin/python -m scripts.ask_support 'When can a duplicate charge be refunded and how long does processing take?'
.venv311/bin/python -m scripts.ask_support 'Check OLA-9999 status.'
.venv311/bin/python -m smoke_tests.run_offline
```

Use `.venv311`. Runtime sets CrewAI/OTEL/Chroma/Hugging Face telemetry/offline flags before imports and disables LangChain/LangSmith tracing before their imports. It removes API-key variables without revealing values; the MOCK_LLM makes no provider calls. Acceptance and CLI install the existing audit before framework imports/model loading: **zero DNS/connect/sendto/child-process attempts**, deliberate blocked DNS control, unchanged model file list/checksums. Prior framework tests retain DNS/numeric-IP/UDP/process negative controls. This is evidence for the exercised Python path, not an OS-wide native-code firewall; local socket construction is recorded separately.

Reviewer evidence:

- [Readable report: tools, retrieved IDs, validated answers, conversations and guardrails](evidence/milestone_04_report.md).
- [Complete actual JSON evidence](evidence/milestone_04_acceptance.json), [initial full report](evidence/milestone_04_initial.json), [fresh-process equality](evidence/milestone_04_reproduction.txt).
- [Initial 12-test transcript](evidence/milestone_04_attempt_01.txt), [fresh 12-test transcript](evidence/milestone_04_acceptance.txt), [prior 6-test regression](evidence/milestone_04_framework_regression.txt).
- [CLI multi-turn output](evidence/milestone_04_cli_memory.txt), [executed CLI verification](evidence/milestone_04_cli_verification.txt).
- [Dataset prerequisite](evidence/milestone_04_prerequisite_dataset.txt), [RAG prerequisite](evidence/milestone_04_prerequisite_rag.txt), [full preceding RAG recheck](evidence/milestone_04_prerequisite_rag.json).

No new unresolved errors. Missing LangChain dependency ERROR-004 was recorded before installation and resolved after actual imports and compatibility checks; expected deprecation warnings remain documented. Milestone 4 stopped at this scope; subsequently approved Part 3 follows below. The separately approved Milestone 6 integration is documented below.

Official references: [CrewAI BaseLLM extension](https://docs.crewai.com/en/learn/custom-llm), [LangChain RunnableWithMessageHistory](https://reference.langchain.com/python/langchain-core/runnables/history/RunnableWithMessageHistory), [LangChain in-process history](https://reference.langchain.com/python/langchain-core/chat_history/InMemoryChatMessageHistory).

## Part 3 localhost API, logging and judge evaluation — Tasks 11–13

**Milestone 5 PASSED:** the fixed Part 2 prerequisite suite passed 12/12 before implementation. Final focused API/privacy/concurrency/judge suite passed **11/11**; actual Uvicorn HTTP/WebSocket checks passed with **29 logical requests and exactly 29 unique JSONL entries**. Full 15-query evaluation matched across two processes; existing dataset/policy 8/8, RAG 8/8, crew 12/12 and prior framework 6/6 regressions all passed. Original statement, dataset, 12 policies, Part 2 source and calibrated RAG code/configuration are byte-identical to [captured input hashes](evidence/milestone_05_input_manifest.json).

### Free setup, exact versions and runtime boundary

Only **FastAPI 0.143.0** was downloaded; all previous 162 package versions remain unchanged. Existing **Starlette 1.7.0**, **Uvicorn 0.54.0**, **httpx 0.28.1**, **websockets 17.2** and Pydantic 2.12.5 are used. Current complete 163-package snapshot: `requirements-api.lock`; direct requirements: `requirements-api.txt`. No model downloads were necessary.

Executed setup (network required):

```sh
.bootstrap/packages/bin/uv pip install --python .venv311/bin/python --cache-dir .cache/uv fastapi
.bootstrap/packages/bin/uv pip check --python .venv311/bin/python --cache-dir .cache/uv
```

For reproducing setup use `-r requirements-api.lock` instead of `fastapi`. See [actual installation](evidence/milestone_05_install.txt), [compatibility](evidence/milestone_05_dependency_check.txt), [exact version/delta evidence](evidence/milestone_05_versions.json). All storage/cache is project-local; setup is separate from runtime.

Supported server command, one worker:

```sh
.venv311/bin/python -m scripts.serve_api --port 8000
```

This long-running command binds **127.0.0.1 only**; stop it with Ctrl-C. The runner installs a Python audit before framework/model imports, permitting IPv4 TCP connections and numeric-address resolution only at the configured loopback port. External DNS, external-IP connections, other loopback ports, UDP and child processes remain blocked; a local urllib3 IPv6 bind probe sends no traffic. Framework telemetry/offline flags and LangSmith tracing controls precede imports; no API keys or runtime package/model downloads. Direct offline crew/evaluation tests retain the original stricter audit with no TCP allowance. The audited entry point is `scripts.serve_api`; bypassing it with another server command would omit its network control.

Final real tests use the same default modern Uvicorn SansIO WebSocket implementation. LangChain memory deprecation warnings remain expected in pinned 1.6.9; early legacy-WebSocket test warnings are retained in historical transcripts. No current dependency conflicts or unresolved compatibility errors. Audit evidence covers exercised Python operations, not an OS-wide native-code firewall.

### HTTP and WebSocket contracts — Task 11

| Route | Request | Response/behavior |
|---|---|---|
| `POST /ask` | `AskRequest`: `session_id`, nonblank string `query` | `AskResponse`: generated `trace_id`, session ID, validated existing `SupportResponse`, actual completed `crew_executed`, prior history-message count |
| `POST /reset-session` | `SessionRequest`: `session_id` | `ResetResponse`: trace/session IDs and `reset=true`; clears only that named HTTP session |
| `WebSocket /ws/chat` | Each text frame is `ChatRequest` JSON: `{"query":"..."}` | One `AskResponse` per valid message; generic typed `APIError` for rejected/failed messages; private session for the connection |

Session IDs use 1–64 ASCII letters/digits/underscore/hyphen. Extra fields and invalid types are rejected. Successful domain refusals/unknown tickets remain HTTP 200 with explicit existing response outcomes; malformed requests return 422; unexpected backend errors return 500 with generic `APIError`. No raw validation inputs or exception text appear in errors. Every HTTP response has `X-Trace-ID`; successful/reset/error JSON includes the same identifier. OpenAPI JSON is available at `/openapi.json`; external-CDN interactive docs are disabled.

HTTP session IDs are explicitly caller-chosen: distinct IDs isolate conversations, and deliberately reusing the same ID shares that named history. HTTP sessions live until reset or process shutdown. Each WebSocket gets a private server-generated ID and separate namespace; clients cannot provide another connection's ID. `WebSocketDisconnect` is caught, connection tracking is removed, and its history is reset and deleted. Actual tests disconnect during a gated real crew request, verify cleanup, and show another connected client continues its own remembered ticket conversation.

One process hosts one shared local model and session manager. A global async lock serializes crew/reset/history operations, while `asyncio.to_thread` keeps synchronous CrewAI work off the socket event loop. Tests exercise three overlapping HTTP clients and two simultaneously connected WebSocket clients. This establishes concurrent-client correctness and session isolation; it does not claim parallel crew throughput or cross-process persistent memory. Keep one worker for this in-process memory design.

### Exactly one masked JSONL record — Task 12

Application records append to gitignored `.runtime/api/requests.jsonl`. Each entry contains a generated trace ID, UTC ISO timestamp, elapsed `duration_ms`, transport, masked route, masked request text, session, outcome/status, phone-mask flag and crew-completion indicator. Trace/private connection IDs use a letter-only UUID encoding, preserving UUID identity without phone-shaped digit runs that could be accidentally redacted.

HTTP pure-ASGI middleware is the only owner of HTTP records; the WebSocket message handler is the only owner of WebSocket records. There is **one entry per HTTP request and per received WebSocket user message**, including rejection, failure and disconnect during message processing. Handshakes, protocol pings and disconnect notifications are connection lifecycle events, not additional user requests. Direct internal crew/evaluation calls are not HTTP/WebSocket requests and do not add duplicate API logs. Uvicorn access logging is disabled.

The boundary parses JSON first, decoding Unicode escapes, then recursively applies the existing phone masker to strings and object keys before Pydantic validation, model dispatch or logging. A numeric phone in an invalid typed field is redacted as null so sanitization cannot turn an invalid integer query into a valid string. Invalid JSON/encoding retains no raw body and logs only `[INVALID_JSON_OR_ENCODING]`. Request headers/query strings and raw exception/validation bodies are not logged. Final persistence applies sanitization again. String phone masking is also demonstrated in stored conversation text; the API response retains `phone_masked` even though the crew receives already masked input.

Before-crew validation and injection rejection are logged once with `crew_executed=false`. Successful returns record the actual kickoff boolean. Internal failures use `crew_executed=null` when completion cannot be established; they never falsely assert that no crew ran. Backend RuntimeError/ValueError get generic internal errors; only request-schema/JSON errors count as validation failures. Unexpected exception text and traceback are never interpolated into logs or replies.

[Real JSONL examples](evidence/milestone_05_logs_localhost.jsonl), [focused validation/error JSONL](evidence/milestone_05_logs_focused.jsonl) and [real transcripts/count/privacy evidence](evidence/milestone_05_localhost.json) verify every received trace against exactly one log row. Fabricated raw phones are absent from all saved milestone evidence and application test logs, including initial failures; unsafe fixtures are constructed only in memory and sanitized before saving.

### Frozen 15-query judge evaluation — Task 13

Before any new evaluation retrieval, `evaluation/support_queries.json`, `evaluation/judge_prompt.txt` and `evaluation/judge_rubric.md` were frozen with [timestamped SHA-256 evidence](evidence/milestone_05_evaluation_freeze.json). Exactly 15 cases cover all 12 required KB topics, two unrelated questions and one unknown-ticket edge case. Expected parent-document labels and fact-anchor groups were authored from the original policy content before results; no post-result label, query, rubric, threshold or crew tuning occurred.

`DeterministicJudge.call()` implements MOCK_LLM judge behavior. Each explicit system message contains the actual judge prompt and rubric; the user packet contains the query, preregistered expected evidence, actual crew response and actual executed tool results. It returns validated `JudgeVerdict` JSON with four [0,1] scores, covered facts, per-claim support, reasons and arithmetic. It does not score from query IDs or return a canned score dictionary.

The rubric is deliberately transparent: Accuracy rewards covered expected facts and penalizes unsupported claim units, requiring a relevant citation; Grounding is the supported-claim fraction against actual retrieved text and parent IDs; Completeness is the fraction of expected anchor groups present; Safety independently checks unmasked fixed-format PII and declared unsafe patterns. Correct refusal and unknown-ticket cases have explicit evidence-consistency rules. These are deterministic lexical/extractive proxies, not general semantic model assessment.

| Case | Required topic/edge | Accuracy | Grounding | Completeness | Safety |
|---|---|---:|---:|---:|---:|
| E01 | Ticket priority | 1 | 1 | 1 | 1 |
| E02 | Severity SLA | 1 | 1 | 1 | 1 |
| E03 | Escalation matrix | 1 | 1 | 1 | 1 |
| E04 | Refund/compensation | 1 | 1 | 1 | 1 |
| E05 | Communication channels | 1 | 1 | 1 | 1 |
| E06 | Hours/holidays | 1 | 1 | 1 | 1 |
| E07 | Repeat complaints | 1 | 1 | 1 | 1 |
| E08 | Service credits | 1 | 1 | 1 | 1 |
| E09 | Feedback | 1 | 1 | 1 | 1 |
| E10 | VIP handling | 1 | 1 | 1 | 1 |
| E11 | Outage communications | 1 | 1 | 1 | 1 |
| E12 | Ticket retention | 1 | 1 | 1 | 1 |
| E13 | Orbital period, out of scope | 1 | 1 | 1 | 1 |
| E14 | Photosynthesis, out of scope | 1 | 1 | 1 | 1 |
| E15 | Unknown OLA ticket | 1 | 1 | 1 | 1 |
| Mean, all 15 included | Each metric: **15.0 /15 =1.0** | **1.0** | **1.0** | **1.0** |

The complete reports reproduce exactly across fresh processes: [actual evaluation JSON](evidence/milestone_05_evaluation.json), [per-query readable answers/evidence/arithmetic](evidence/milestone_05_evaluation.md), [independent repeat](evidence/milestone_05_evaluation_repeat.json), [full comparison](evidence/milestone_05_reproduction.txt). Every result includes its full judge messages, actual retrieved chunk/parent IDs and similarities, crew events, structured answer and score calculations.

Negative judge fixtures verify that changed numbers lower Accuracy/Grounding, unsupported additions lower Grounding/Accuracy, removed content lowers Completeness while remaining text stays grounded, and an unsafe credential request/raw temporary phone makes Safety=0. Wrong-parent citations are also penalized. [Focused fixture evidence](evidence/milestone_05_focused.json) and [API/fixture report](evidence/milestone_05_api_report.md) show actual scores.

**Observed limits:** perfect scores reflect this small known corpus, exact excerpts and the declared lexical checks. Fixed-size fragments and duplicated overlapping passages remain visible; the rubric does not measure fluency, general semantics, multilingual support or adversarial/near-domain robustness. No weak query was excluded or scoring rule changed after inspection. This paragraph describes historical Milestone5; full AutoGen review was integrated in Milestone6 and reverified in the final audit.

### Reproducible acceptance and review

```sh
.venv311/bin/python -m tests.milestone_05_focused
.venv311/bin/python -m tests.milestone_05_localhost
.venv311/bin/python -m scripts.evaluate_support
.venv311/bin/python -m scripts.evaluate_support --report evidence/milestone_05_evaluation_repeat.json
.venv311/bin/python -m scripts.verify_milestone_05
.venv311/bin/python -m tests.milestone_02_acceptance --report evidence/milestone_05_dataset_regression.json
.venv311/bin/python -m tests.milestone_03_acceptance
.venv311/bin/python -m tests.milestone_04_acceptance --report evidence/milestone_05_crew_regression.json
.venv311/bin/python -m smoke_tests.run_offline
```

The real localhost test creates an ephemeral 127.0.0.1 listener, exercises actual HTTP/WebSocket traffic and shuts it down; default sandbox listener binding was denied, so authorized execution permission was needed while its internal audit still denied external access. Focused tests use the stricter offline audit and ASGI TestClient. All package/model downloads are setup only.

Start review with [PROJECT_STATUS](PROJECT_STATUS.md), [API/transcripts/logging/fixtures report](evidence/milestone_05_api_report.md), [evaluation report](evidence/milestone_05_evaluation.md), [focused test output](evidence/milestone_05_focused_final.txt), [real localhost output](evidence/milestone_05_localhost_acceptance.txt) and raw JSON/JSONL evidence. Regression transcripts are `evidence/milestone_05_dataset_regression.txt`, `milestone_05_rag_regression.txt`, `milestone_05_crew_regression.txt`, `milestone_05_framework_regression.txt`.

Three initial failures are preserved: ERROR-005 numeric sanitization, ERROR-006 sandbox loopback binding, ERROR-007 trace redaction. Each was recorded before its fix and resolved only after verification. No unresolved errors/blockers. At the historical Milestone5 closure, review/governance/cache were pending. Milestone6 implemented them; the final audit reverified all16 tasks. Public hosting and repository publication remain pending.

Official implementation references: [FastAPI WebSockets and disconnect handling](https://fastapi.tiangolo.com/advanced/websockets/), [FastAPI safe error handlers](https://fastapi.tiangolo.com/tutorial/handling-errors/).

Final Milestone5 documentation/evidence audit: [executed audit](evidence/milestone_05_documentation_audit.json) PASSED; historical command `.venv311/bin/python -m scripts.verify_milestone_05` checks the old fixed-source snapshot and is not the current final verifier.

## Part 4 integrated review, governance and cache — Tasks 14–16

Milestone 6 uses the existing `.venv311` and all 163 pinned packages; **no dependency or model downloads** were needed. Setup remains separate from offline runtime. Tasks 14–16 run through `SupportSession.ask`, the CLI, and the same HTTP/WebSocket application; historical smoke review is not used as a substitute for application integration.

### Review after actual Composer

`support/review.py` constructs two real AutoGen `AssistantAgent`s and `RoundRobinGroupChat(max_turns=2, custom_message_types=[StructuredMessage[VerdictModel]])`. The Final Editor uses `output_content_type=VerdictModel`, with strict `approved: bool`, `final_answer: str`, and `reason: str`. The initiating task contains the validated actual CrewAI Composer draft, its actual stage outputs, and **original trusted tool context**, including complete retrieved chunks/parent IDs/cosines or literal ticket results. Distinct local model clients compare the draft with evidence-only rendering, rather than returning answers selected by query ID.

Both agents speak once. The final verdict validates, its answer is placed in an evidence-derived `SupportResponse`, and the existing complete-answer/structured-fact output guard validates it against trusted context. Unsupported review output is refused. Review remains active on cache hits. A test-only constructor `draft_transform` fault-injects an immediate INR 999999 guarantee after actual Composer execution; the two-agent team revises it to the original supported answer. This hook is not exposed in user HTTP/WebSocket schemas. Both direct application and HTTP revision executions are saved in [integrated acceptance](evidence/milestone_06_acceptance.json).

This deterministic MOCK review checks exact evidence rendering, not general paraphrase entailment. It can reject a valid paraphrase and cannot establish general semantic robustness. No external judge/model services or API keys are used.

### Four governance layers

The official Task 15 explicitly names **Application** and **Runtime**, without naming or specifying the other two layers. This project organizes its four-layer explanation as **Data, Model, Application, Runtime**; the first two names are an explicit project interpretation, not additional quoted course requirements.

| Layer | Implemented controls | Conceptual boundaries / remaining limitations |
|---|---|---|
| Data | Seeded fabricated data; original policy checksums and parent mappings; frozen evaluation labels; phone masking before models/history/logs; cache rejects changed live corpus until index rebuild/recalibration | Policies describe retention but no production deletion scheduler, consent management or access-controlled customer database is implemented. Free-text identity/address/payment masking remains outside this brief. |
| Model | Local pinned embedding model with verified manifest; deterministic CrewAI BaseLLM and distinct AutoGen clients; two-agent bounded review; strict Pydantic outputs and evidence-only final guard; measured similarity cutoff | No provider training-data audit, real-model semantic verifier or independent human adjudication. MOCK review is exact/extractive. |
| Application | Retrieval gets only RAG, Lookup gets only ticket tool, Composer/review have no tools; delegation disabled; native pre-tool hook checks actual agent identity and grants one-use ticket permission; ticket `_run` fails closed without that permission; input injection refusal and isolated memory | This governs application agent tool access, not arbitrary hostile Python code on the host. Caller-chosen HTTP session IDs are not authentication; no production RBAC/tenant identity is claimed. |
| Runtime | Request-local simulated token/cost caps shared by every crew and review model call; oversized request preflight; atomic per-call rejection; telemetry disabled before imports; external DNS/connect/UDP/process audit; per-request masked JSONL logs | Audit is a Python-path control, not an OS-wide firewall. Budgets are simulated MOCK units, not vendor billing tokens. No external hosting, production SLA or paid-provider cost enforcement is claimed. |

**Least autonomy:** Only the actual designated Lookup agent instance can obtain a one-use capability from CrewAI's native `before_tool_call` context. Matching its role string is insufficient: Retrieval, Composer, missing callers and an impostor named Lookup are rejected; the ticket tool checks and consumes that capability at its own execution boundary. The framework `after_tool_call` hook clears residual permission. Wiring only Lookup provides the first restriction; the identity/boundary check supplies a second restriction even if the tool is accidentally exposed elsewhere. Evidence includes rejected calls and a successful real `.kickoff()` lookup.

**Risk classification: Medium.** The course scheme explicitly puts customer-support tickets in Medium. This agent reads support records, summarizes fabricated compensation policies and recommends escalation review; wrong information can mislead a customer or staff member. It does not execute payments/refunds, change records, handle medical data, select hires or make financial decisions, so the implemented capabilities do not justify a High classification; customer-ticket use is more consequential than the Low summarization/transcription examples.

**Autonomy classification: Low.** The system can choose between two bounded read-only tools, resolve a ticket pronoun from its own session, and produce a reviewed answer. It cannot delegate, mutate tickets, grant refunds/credits, contact customers, execute arbitrary code, publish content or access external services. Medium domain risk therefore coexists with Low operational autonomy; those classifications describe different properties.

### Simulated budget arithmetic

`support/governance.py:RequestBudget` is created for each accepted request and shared across Retrieval, Lookup, Composer, Policy Compliance Reviewer and Final Editor. Defaults are **50,000 simulated tokens and USD 0.10 per request**. Tokens are `ceil(len(serialized input)/4) + ceil(len(serialized output)/4)` for each actual adapter call; crew input includes role messages/tool schemas, review input includes messages and the declared structured verdict JSON schema. Cached policy evidence still contributes tokens when consumed by the crew/review. No provider tokenizer is claimed.

The explicit simulated price is **USD 0.002 per 1,000 tokens**, uniformly for input/output: `simulated_cost = total_tokens × 0.002 / 1000`. This is a capstone assumption, not a current vendor price. **Actual monetary expenditure is USD 0.** Input-alone lower-bound preflight occurs before history/crew/cache. Before each model output is released, an atomic budget check rejects either cap violation without adding its tokens to accepted usage; a review-stage rejection returns a structured refusal and commits neither history nor a new cache result. AutoGen wraps model exceptions, so trusted `budget.exceeded` state identifies its rejection without parsing/logging raw exception text.

The representative policy baseline measured **12,828 simulated tokens**, **USD 0.025656**, across four CrewAI and two review calls. Receipt-level input/output counts and sums are saved in acceptance JSON. Tests reject oversized token and cost requests before any calls, a small cap at first crew call, and caps sufficient for the crew but insufficient for review. Usage never silently exceeds either cap; rejection also cannot bypass budgets through a warm cache.

### Grounded-generation cache scope

`support/cache.py:PolicyCache` is an in-process dictionary keyed by `query.casefold()` with collapsed whitespace, plus an evidence/configuration namespace. It stores **only the RAG tool's grounded policy result and original retrieved context**, not the Composer draft, reviewed response, ticket result, user history or session ID. The namespace includes live policy hashes, evaluated index fingerprint, model identity, complete runtime calibration configuration and renderer version. Changed configuration misses; changed policy corpus fails closed against the loaded index rather than serving stale indexed answers. Explicit `invalidate()` clears entries. No persistence, TTL or eviction policy is claimed.

Input masking/injection rejection and budget preflight run before cache access. On a hit, the real Retrieval task consumes cached policy evidence in one model call instead of requesting/executing the RAG tool and consuming its result in two calls. Lookup remains fresh for ticket/mixed queries; Composer, both review agents, final guard/schema validation, session memory and exactly-once API logging still execute. Equivalent policy portions can be shared across conversations without sharing ticket facts.

| Actual policy request | Crew model calls | RAG tool calls | AutoGen review calls |
|---|---:|---:|---:|
| Uncached baseline | 4 | 1 | 2 |
| First enabled-cache request (miss) | 4 | 1 | 2 |
| Identical repeated request (hit) | 3 | 0 | 2 |
| After invalidation / changed configuration | 4 | 1 | 2 |

There is no whole-response cache: ticket-only requests always execute the ticket tool; no full response shortcut bypasses review/logging. Cache entries are deep-copied and committed after successful review/validation. Acceptance covers normalized hits, unrelated-query misses, invalidation, configuration changes, synthetic live-corpus mismatch, cross-session mixed-ticket isolation, fresh conversation, injection refusal, budget rejection before warm-cache lookup, and one JSONL row per cache-hit HTTP request.

### Reproducible verification and limits

```sh
.venv311/bin/python -m tests.milestone_06_acceptance
.venv311/bin/python -m tests.milestone_04_acceptance --report evidence/milestone_06_crew.json
CAPSTONE_EVIDENCE_PREFIX=milestone_06 .venv311/bin/python -m tests.milestone_05_focused
CAPSTONE_EVIDENCE_PREFIX=milestone_06 .venv311/bin/python -m tests.milestone_05_localhost
.venv311/bin/python -m scripts.evaluate_support --report evidence/milestone_06_evaluation.json
.venv311/bin/python -m scripts.evaluate_support --report evidence/milestone_06_evaluation_repeat.json
.venv311/bin/python -m smoke_tests.run_offline
```

Localhost tests require a permitted local listener in this sandbox and keep the existing external-network-denial audit. Strict non-API acceptance blocks all external networking before framework/model imports. Model files and protected statement/data/policies/calibration/frozen labels remain unchanged; no runtime downloads. The historical `verify_milestone_05` audited its fixed Part 2 source snapshot before this authorized integration; its old byte-identity/status checks are not a current Milestone 6 audit.

The frozen 15-query evaluation still reports **Accuracy, Grounding, Completeness and Safety averages 1.0**; all 15 remain in each denominator and labels/prompt/rubric were not changed. These lexical/extractive metrics do not establish general answer quality. Final Milestone 6 audit and reviewer evidence are recorded in the tracking documents. The complete final acceptance audit is now authorized and passed; no public repository or external deployment has been created. Publication and submission require separate approval.

**Milestone6 PASSED and stopped:** [readable integrated evidence](evidence/milestone_06_report.md), [final evidence/document audit](evidence/milestone_06_documentation_audit.json). All16 implementation tasks have executed evidence; the complete final audit is recorded below, while repository publication remains separately authorized work.

## Final local readiness

[FINAL_ACCEPTANCE_REPORT.md](FINAL_ACCEPTANCE_REPORT.md) maps all16 tasks to actual commands/tests/evidence. [Final task audit](evidence/final_acceptance_audit.json), [submission inspection](evidence/final_submission_inspection.json), [documentation audit](evidence/final_documentation_audit.json) and [local Git preparation](evidence/final_git_preparation.json) record actual outcomes. One local initial commit on `main` contains the complete code/text/evidence allowlist; no remote or push. Required public repository/link remains pending separate approval.
