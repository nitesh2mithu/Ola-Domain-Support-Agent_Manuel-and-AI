# Final Acceptance Report — Ola Domain Support Agent

**Verdict: all 16 official implementation tasks verified; local submission preparation passed; ready for user-approved publication.** Public repository creation and push are complete and verified. Portal submission remains pending user action; no deployment performed. This report does not claim a grade or production readiness.

Source: unchanged `Problem_Statement.md`. Deadline: **8 November 2026**. Part allocations:30/30/20/20 marks (100 total); no individual task marks are specified. Final execution:11 October2026, IST (Asia/Calcutta, UTC+05:30). Use the exact timestamped commands/results in [execution ledger](evidence/final_offline_execution.json) and [localhost ledger](evidence/final_localhost_execution.json).

## Executed verification

- **51 distinct automated checks passed;71 executions** including dataset and crew fresh-process repeats. Dataset/policies8 twice; RAG8; crew12 twice; API/log/judge11; integrated review/governance/cache6; framework6. Focused11 additionally rerun after equivalent UUID-source cleanup.
- Real Uvicorn: **18 HTTP requests +11 WebSocket messages =29 logical requests/29 unique correlated JSONL entries**. Multi-turn state, fresh/reset isolation, concurrent clients, malformed input, masked errors, mid-request disconnect cleanup and survivor all verified.
- Exactly15 frozen evaluation queries cover all12 topics plus2 out-of-scope questions and1 unknown ticket. All four scores reported per query; independent Decimal arithmetic gives each sum15.0/15, **Accuracy1.0, Grounding1.0, Completeness1.0, Safety1.0**. Full evaluation reports match across fresh processes; averages unchanged from Milestone6.
- Full dataset and uncached crew reports match across fresh processes. Both RAG strategies/calibration/parent-deduplicated fractions independently recomputed. Fixed precision/recall1.0/1.0; sentence0.5555555556/1.0; fixed remains selected.
- Local model checksums/pins and official statement/dataset/policies/calibration/frozen labels unchanged. External runtime attempts0; strict children deny networking/process spawning, API test allows only its declared loopback port. External DNS/IP/other port/UDP/process controls rejected.
- Both initially empty collections rebuilt offline:33 fixed/24 sentence chunks, sensible refund retrieval, calibration preserved ([clean rebuild](evidence/final_clean_index.json)). No setup downloads during final audit.

## Reproducible command key

Run from the project root with the existing Python3.11 `.venv311`:

| Key | Command |
|---|---|
| A | `.venv311/bin/python -m tests.milestone_02_acceptance --report evidence/final_dataset.json` |
| B | `CAPSTONE_EVIDENCE_PREFIX=final .venv311/bin/python -m tests.milestone_03_acceptance` |
| C | `.venv311/bin/python -m tests.milestone_04_acceptance --report evidence/final_crew.json` |
| D | `CAPSTONE_EVIDENCE_PREFIX=final .venv311/bin/python -m tests.milestone_05_focused` |
| E | `CAPSTONE_EVIDENCE_PREFIX=final .venv311/bin/python -m tests.milestone_05_localhost` |
| F | `.venv311/bin/python -m scripts.evaluate_support --report evidence/final_evaluation.json` |
| G | `CAPSTONE_EVIDENCE_PREFIX=final .venv311/bin/python -m tests.milestone_06_acceptance` |
| H | `.venv311/bin/python -m smoke_tests.run_offline` |

Preferred complete execution: `.venv311/bin/python -m scripts.run_final_verification`, then `--phase localhost`, then `.venv311/bin/python -m scripts.verify_final_acceptance`. The runner records all commands/exit codes and stops on failure;localhost binding requires local permission. It runs A/C/F again in fresh processes with `_repeat` report names.

## Task-by-task acceptance evidence

PASSED below reflects executed assertions and independent final inspection, not prior tracker labels. Test numbers refer to the corresponding module's tests.

| Task / Part | Implementation | Executed acceptance checks / command | Supporting final evidence | Result |
|---|---|---|---|---|
|1 /1|`dataset.py`:generate_tickets/validate_tickets/SUPPORT_TICKETS; README design|A01–05/07/08: 60 records, required types/IDs/ranges, all category/status thresholds, 23.33% escalation; documented seed/weights/rationale; full seeded reproduction and invalid fixtures.|[records/counts/types](evidence/final_dataset.json), [output](evidence/final_dataset.txt), [repeat](evidence/final_dataset_repeat.json)|PASSED|
|2 /1|`knowledge_base/*.md`, README topic mapping|A06/07: all 12 original required topics, four body sentences per document, content anchors and unchanged hashes.|[topic/sentence coverage](evidence/final_dataset.json)|PASSED|
|3 /1|`rag/chunking.py`, `rag/core.py`:LocalRAG.upsert_indexes|B01/02/03/05/07/08: overlapping fixed and sentence chunks, stable parents/IDs, real 384D local embeddings, separate 33/24 cosine collections, upserts and sensible retrieval; empty-index rebuild.|[chunk/index/hits](evidence/final_rag.json), [output](evidence/final_rag.txt), [empty-index rebuild](evidence/final_clean_index.json)|PASSED|
|4 /1|`rag/core.py`:retrieve/grounded_answer;calibration.json|B04/05: three in-scope/two out-of-scope measured cosines per strategy, empirical midpoint thresholds; six supported answers and held-out fallback using actual retrieved context.|[calibration/answers](evidence/final_rag.md), [independent threshold checks](evidence/final_acceptance_audit.json)|PASSED|
|5 /1|`evaluation/rag_queries.json`, `rag/evaluation.py`:document_metrics/experiment;README|B06 plus independent audit: same six frozen labelled queries, deduplicated parent sets, visible precision/recall fractions and macro means; three-sentence measured recommendation.|[per-query fractions](evidence/final_rag.md), [independent arithmetic](evidence/final_acceptance_audit.json)|PASSED|
|6 /2|`support/tickets.py`:check_support_ticket_status/escalation_score|C01/06/10: all 60 status/hours/score results; weighted flag/normalized-age formula, score bounds, dataset p80 threshold and unknown/malformed cases.|[all scores/distribution](evidence/final_crew.json), [output](evidence/final_crew.txt)|PASSED|
|7 /2|`support/crew.py`:MOCK_LLM(BaseLLM),PolicyTool/TicketTool/kickoff_support|C02/03/04/06/11: actual three-agent kickoff and both native tools on distinct/mixed queries; Composer consumes real task outputs; schema dispatch and Observation regressions.|[native call events/results](evidence/final_crew.json)|PASSED|
|8 /2|`support/session.py`:LangChain RunnableWithMessageHistory/InMemoryChatMessageHistory|C05/07: three-turn carried ticket state, fresh-session absence/reset, sanitized history. D/E verify concurrent-client isolation.|[multi-turn/fresh/reset](evidence/final_crew.json), [live transcripts](evidence/final_localhost.json)|PASSED|
|9 /2|`support/models.py`:response_format=SupportResponse,StageResult,TicketResult|C02/10 and all actual outputs: framework Pydantic plus explicit draft/final/API validation; invalid schema/types/fact bounds rejected.|[validated outputs/negatives](evidence/final_crew.json), [API](evidence/final_focused.json)|PASSED|
|10 /2|`support/guardrails.py`:guard_input/guard_output;session/API boundaries|C07/08/09/10/12: phone masking before model/history, injection rejection without calls, unsupported-query fallback and injected-draft/fact refusal. D/E verify error-path privacy.|[guardrail examples](evidence/final_crew.json), [masked live logs](evidence/final_logs_localhost.jsonl)|PASSED|
|11 /3|`api/app.py`,`api/models.py`,`scripts/serve_api.py`|D/E: real typed ask/reset HTTP endpoints and multi-turn WebSocket; malformed/concurrent/isolated clients; disconnect during crew work, cleanup and surviving second client.|[HTTP/WS transcripts](evidence/final_localhost.json), [output](evidence/final_localhost.txt)|PASSED|
|12 /3|`api/logging.py`,WebSocket handler|D/E and independent audit: exactly one timed JSONL row per logical request, 29 correlated unique traces; masking on valid/validation/error/cache-hit paths.|[actual JSONL](evidence/final_logs_localhost.jsonl), [fixtures](evidence/final_focused.json), [cache-hit logs](evidence/final_cache_api.jsonl)|PASSED|
|13 /3|`evaluation/support_queries.json`,judge_prompt/rubric,`evaluation/judge.py`,`scripts/evaluate_support.py`|F twice: exactly 15 cases, all 12 topics and at least two edge cases; explicit MOCK judge scores actual answers/evidence. D verifies negative fixtures; independent Decimal averages.|[all15/arithmetic](evidence/final_evaluation.md), [full prompts/results](evidence/final_evaluation.json), [independent averages](evidence/final_acceptance_audit.json)|PASSED|
|14 /4|`support/review.py`,`support/crew.py`|G01/05: real two-agent RoundRobin, max_turns=2, original context, typed registered verdict; unchanged approval and actual injected-claim revision, including HTTP; final guard retained.|[approval/revision/original context](evidence/final_acceptance.json), [output](evidence/final_acceptance.txt)|PASSED|
|15 /4|`support/crew.py`:native permissionhook/TicketTool;`support/governance.py`:RequestBudget;READMEfourlayers/risk|G02/03/05: actual Lookup identity and one-use tool boundary; wrong-role/missing/impostor rejection; combined token/cost caps through crew/review; documented layers and Medium risk.|[permissions/receipts/rejections](evidence/final_acceptance.json), READMEgovernance|PASSED|
|16 /4|`support/cache.py`:PolicyCache;crew/session|G04/05: normalized policy-only cache; miss four model/one RAG call to hit three/zero; review retained; misses/invalidation/config/stale evidence/session/guard/budget/logging checks.|[counters/isolation](evidence/final_acceptance.json), [independent counters](evidence/final_acceptance_audit.json)|PASSED|

## Submission inspection and remaining boundaries

Intended files are code, original policies, pinned dependencies, original statement, tracking/report Markdown and curated sanitized text/JSON/JSONL evidence. `.gitignore` excludes virtual environments, interpreter/bootstrap, model weights/cache/index databases, live runtime credentials/logs, private configuration/editor state, keys/env files and build binaries. The explicit allowlist and static scan are reproducible via `scripts.inspect_submission`; staged-byte inspection must pass before commit. Required evidence stays under `evidence/`; live logs remain excluded under `.runtime/`.

Final hygiene findings were recorded before fixes:ERROR-011 fabricated UUID-source literal construction;ERROR-012 local paths in warning transcript. Focused rerun passed, source meaning unchanged, intended scan subsequently clean;original failed inspection retained and unsanitized successful output kept only in excluded runtime. No genuine credentials or real customer data discovered. Static secret patterns are not exhaustive; raw fabricated-phone absence plus runtime masking tests give specific inspectable evidence.

Known limitations:MOCK scores are deterministic lexical/extractive proxies on a small known corpus, not semantic quality, fluency or adversarial robustness. Fixed fragments can repeat/cut sentences; calibration negatives are unrelated, not comprehensive near-domain tests. Exact evidence review can reject valid paraphrases. Budgets use simulatedceil(chars/4) units/USD0.002per1000, actual spend0. Python audit hooks verify exercised Python calls, not arbitrary native-code traffic or an OS firewall. Session/cache are one-process/in-memory;HTTP session IDs are not authentication;no production tenant/RBAC/payment/record-mutation capabilities. Pinned LangChain deprecations and CrewAI credential-storage shim are documented. The brief explicitly names Application/Runtime governance layers;Data/Model are the declared project mapping of the remaining two, subject to any additional course material.

README contains completed-track declaration, exact setup/model identity, offline rebuild/runtime/API/evaluation/reproduction commands, architecture/governance/dependencies and limitations. Allfour tracking documents are updated with actual final outcomes. **Publication remains pending:**create one public GitHub repository, attach it as origin,push the inspected local commit,then submit that single repository link by8November2026—only after separate user approval. No remote has been created, no push/externaldeployment/submission performed.

## Local Git preparation

Local `main` initialized only after task/content/document audits passed. One unpublished initial commit uses generic project identity and includes all required source packages plus sanitized evidence; no global Git configuration changed and no remote exists. A postcommit check discovered omitted `support/` in the staging allowlist; ERROR-013 was recorded, source-completeness checks added, all intended files rescanned/tracked and the initial commit amended. Its failed intermediate knowledge-base gate was preserved. Final closure is included in that same initial commit; all265 intended files are tracked, committed bytes match inspected files, branch main has one commit, working tree is clean and there are no remotes. See [Git preparation evidence](evidence/final_git_preparation.json). All14 errors are resolved.

## Authorized publication preflight

2026-10-11T00:54:48.732158+05:30: independent all16-task and prepublication documentation gates freshly passed;265 intended committed files reviewed, one clean initial submission commit66251f65dc703b38d67f6f0cc1e6006b50ca7845, no remotes and no scan findings. CLI identity/auth status failed HTTP401/invalid keyring token; connector identity works but cannot create/push repositories. Publication remains blocked awaiting browser-based CLI login. No public repository/link or final remote commit is claimed. [Sanitized preflight evidence](evidence/publication_preflight.json). Historical pending-approval statements above describe the previous session.

## Final publication verdict — PASSED

Publication verified — 2026-10-11T01:00:13.850996+05:30: [public capstone repository](https://github.com/nitesh2mithu/ola-domain-support-agent), default branch main, published submission commit `66251f65dc703b38d67f6f0cc1e6006b50ca7845`. GitHub public visibility, exact265-file tree equality, rendered README heading/code blocks and all relative file links PASSED. ERROR-015 resolved by verified browser CLI login; no unresolved errors or blockers. Publication documentation update is committed separately after this submission commit; final remote head is verified after pushing that update. No course-portal submission or external deployment.

[GitHub verification evidence](evidence/publication_github_verification.json). Earlier local/preflight statements are historical. All16 implementation acceptance criteria and public repository packaging/visibility requirements are met; no awarded marks or production-readiness claim.
