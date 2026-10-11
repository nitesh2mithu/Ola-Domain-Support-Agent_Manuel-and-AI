# Version 2 Acceptance Report

**Verdict: all 16 official requirements verified on current v2 code; local review only.** The five additional evaluation cases expose known scope/coverage weaknesses. Documentation/content closing checks passed and are recorded below; no improvement push, merge, publication, deployment or submission.

Source: unchanged `Problem_Statement.md`. All original policies, calibrated RAG configuration and original 15 evaluation labels/prompt/rubric remain unchanged. Original requirements allocate Parts1–4:30/30/20/20, with no individual task marks.

## Executed current verification

-56 distinct automated checks,76 executions including fresh dataset/crew repeats; all passed. Dataset8twice, RAG8, crew12twice, focused11, integrated review/governance/cache6, framework6 and additional judge/average fixtures5.
-Actual localhost Uvicorn HTTP/WebSocket:18HTTP+11messages,29exact correlated masked log entries; malformed requests, session isolation, concurrent clients and mid-request disconnect/survivor passed.
-Required15queries executed twice with unchanged labels/rules, each Accuracy/Grounding/Completeness/Safety average1.0; allscore sums/averages independently recomputed.
-Additional5queries executed twice, reports exactly match. Accuracy0.8,Grounding1.0,Completeness0.7,Safety1.0; independent sums4.0/5,5.0/5,3.5/5,5.0/5. X01relatedrefundexcerpts failed expected undocumented-entitlement refusal; X04missing2of4facts. No post-result tuning or dropping cases.
-Datasetandfulluncachedcrewreports identical across processes; alloriginal7fields remain equal to v1. Separate seed43 reopening stream independently reproduced. All60lookup/schema/scores checked; threshold0.55,rank48,tiecount1 excluded,12recommendations including2non-escalated vs v1zero at0.613333.
-Both RAG strategies use actual local embeddings/upserts/stableparents; measured threshold midpoints/parent-deduplicated fractions independently checked. FixedP/R1.0/1.0; sentence0.5555555556/1.0.
-Real three-agent CrewAI/tool calls, memory/schema/guards, two-agent AutoGen structured approval/revision, identity-bound permission rejection, combined simulated budget caps and cache counters verified. Policy hit4→3crewmodelcalls,1→0RAGtoolcalls; review2 retained.
-Offline runtime:zeroexternal attempts; keys absent and telemetry disabled before imports. API permits only declaredlocalhost traffic; externalDNS/IP/otherport/UDP/process controls reject. Initiallyemptyindexes rebuiltoffline33fixed/24sentence preservingcalibration. Model files/pins unchanged.

## Reproduction commands

```sh
.venv311/bin/python -m scripts.run_final_verification
.venv311/bin/python -m scripts.run_final_verification --phase localhost
.venv311/bin/python -m scripts.verify_final_acceptance
.venv311/bin/python -m scripts.rebuild_indexes --db-dir .runtime/v2-clean-check --report evidence/final_clean_index.json
.venv311/bin/python -m scripts.inspect_submission
.venv311/bin/python -m scripts.verify_final_documents
```

Runner records exact commands, exit codes and full sanitized output in [offline ledger](../evidence/final_offline_execution.json) and [localhost ledger](../evidence/final_localhost_execution.json). Commands A–H below map to existing test modules: A=tests.milestone_02_acceptance;B=tests.milestone_03_acceptance;C=tests.milestone_04_acceptance;D=tests.milestone_05_focused;E=tests.milestone_05_localhost;F=scripts.evaluate_support;G=tests.milestone_06_acceptance;H=smoke_tests.run_offline. Run via `.venv311/bin/python -m`; the ledger includes arguments and current-evidence environment prefix.

## Task-by-task current evidence

| Task / Part | Implementation | Executed checks / command | Current evidence | Result |
|---|---|---|---|---|
|1 /1|`dataset.py`:generate_tickets/validate_tickets/SUPPORT_TICKETS; README design|A01–05/07/08: 60 records, required types/IDs/ranges, all category/status thresholds, 23.33% escalation; documented seed/weights/rationale; full seeded reproduction and invalid fixtures.|[records/counts/types](../evidence/final_dataset.json), [output](../evidence/final_dataset.txt), [repeat](../evidence/final_dataset_repeat.json)|PASSED|
|2 /1|`knowledge_base/*.md`, README topic mapping|A06/07: all 12 original required topics, four body sentences per document, content anchors and unchanged hashes.|[topic/sentence coverage](../evidence/final_dataset.json)|PASSED|
|3 /1|`rag/chunking.py`, `rag/core.py`:LocalRAG.upsert_indexes|B01/02/03/05/07/08: overlapping fixed and sentence chunks, stable parents/IDs, real 384D local embeddings, separate 33/24 cosine collections, upserts and sensible retrieval; empty-index rebuild.|[chunk/index/hits](../evidence/final_rag.json), [output](../evidence/final_rag.txt), [empty-index rebuild](../evidence/final_clean_index.json)|PASSED|
|4 /1|`rag/core.py`:retrieve/grounded_answer;calibration.json|B04/05: three in-scope/two out-of-scope measured cosines per strategy, empirical midpoint thresholds; six supported answers and held-out fallback using actual retrieved context.|[calibration/answers](../evidence/final_rag.md), [independent threshold checks](../evidence/final_acceptance_audit.json)|PASSED|
|5 /1|`evaluation/rag_queries.json`, `rag/evaluation.py`:document_metrics/experiment;README|B06 plus independent audit: same six frozen labelled queries, deduplicated parent sets, visible precision/recall fractions and macro means; three-sentence measured recommendation.|[per-query fractions](../evidence/final_rag.md), [independent arithmetic](../evidence/final_acceptance_audit.json)|PASSED|
|6 /2|`support/tickets.py`:check_support_ticket_status/escalation_score|C01/06/10 (updated score/reopen assertions): all 60 status/hours/score results; weighted flag/normalized-age formula, score bounds, dataset p80 threshold and unknown/malformed cases.|[all scores/distribution](../evidence/final_crew.json), [output](../evidence/final_crew.txt)|PASSED|
|7 /2|`support/crew.py`:MOCK_LLM(BaseLLM),PolicyTool/TicketTool/kickoff_support|C02/03/04/06/11: actual three-agent kickoff and both native tools on distinct/mixed queries; Composer consumes real task outputs; schema dispatch and Observation regressions.|[native call events/results](../evidence/final_crew.json)|PASSED|
|8 /2|`support/session.py`:LangChain RunnableWithMessageHistory/InMemoryChatMessageHistory|C05/07: three-turn carried ticket state, fresh-session absence/reset, sanitized history. D/E verify concurrent-client isolation.|[multi-turn/fresh/reset](../evidence/final_crew.json), [live transcripts](../evidence/final_localhost.json)|PASSED|
|9 /2|`support/models.py`:response_format=SupportResponse,StageResult,TicketResult|C02/10 and all actual outputs: framework Pydantic plus explicit draft/final/API validation; invalid schema/types/fact bounds rejected.|[validated outputs/negatives](../evidence/final_crew.json), [API](../evidence/final_focused.json)|PASSED|
|10 /2|`support/guardrails.py`:guard_input/guard_output;session/API boundaries|C07/08/09/10/12: phone masking before model/history, injection rejection without calls, unsupported-query fallback and injected-draft/fact refusal. D/E verify error-path privacy.|[guardrail examples](../evidence/final_crew.json), [masked live logs](../evidence/final_logs_localhost.jsonl)|PASSED|
|11 /3|`api/app.py`,`api/models.py`,`scripts/serve_api.py`|D/E: real typed ask/reset HTTP endpoints and multi-turn WebSocket; malformed/concurrent/isolated clients; disconnect during crew work, cleanup and surviving second client.|[HTTP/WS transcripts](../evidence/final_localhost.json), [output](../evidence/final_localhost.txt)|PASSED|
|12 /3|`api/logging.py`,WebSocket handler|D/E and independent audit: exactly one timed JSONL row per logical request, 29 correlated unique traces; masking on valid/validation/error/cache-hit paths.|[actual JSONL](../evidence/final_logs_localhost.jsonl), [fixtures](../evidence/final_focused.json), [cache-hit logs](../evidence/final_cache_api.jsonl)|PASSED|
|13 /3|`evaluation/support_queries.json`,judge_prompt/rubric,`evaluation/judge.py`,`scripts/evaluate_support.py`|F twice: exactly 15 cases, all 12 topics and at least two edge cases; explicit MOCK judge scores actual answers/evidence. D verifies negative fixtures; independent Decimal averages.|[all15/arithmetic](../evidence/final_evaluation.md), [full prompts/results](../evidence/final_evaluation.json), [independent averages](../evidence/final_acceptance_audit.json)|PASSED|
|14 /4|`support/review.py`,`support/crew.py`|G01/05: real two-agent RoundRobin, max_turns=2, original context, typed registered verdict; unchanged approval and actual injected-claim revision, including HTTP; final guard retained.|[approval/revision/original context](../evidence/final_acceptance.json), [output](../evidence/final_acceptance.txt)|PASSED|
|15 /4|`support/crew.py`:native permissionhook/TicketTool;`support/governance.py`:RequestBudget;READMEfourlayers/risk|G02/03/05: actual Lookup identity and one-use tool boundary; wrong-role/missing/impostor rejection; combined token/cost caps through crew/review; documented layers and Medium risk.|[permissions/receipts/rejections](../evidence/final_acceptance.json), READMEgovernance|PASSED|
|16 /4|`support/cache.py`:PolicyCache;crew/session|G04/05: normalized policy-only cache; miss four model/one RAG call to hit three/zero; review retained; misses/invalidation/config/stale evidence/session/guard/budget/logging checks.|[counters/isolation](../evidence/final_acceptance.json), [independent counters](../evidence/final_acceptance_audit.json)|PASSED|

## Changes and evaluation interpretation

[Single escalation change record](../evidence/v2_escalation_change.json) gives old/new dataset digests, formulas, score expectations, examples and independent lookup receipts. [Change log](CHANGELOG_V2.md) explains intentional schema/score changes. Existing originalfields/seed42/distribution preserved; no records hand-edited.

[Extra query freeze](../evidence/v2_extra_freeze.json) predates execution. Originaljudge arithmetic is unchanged; [extension](../evaluation/extra_rubric.md) adds generic unsupported-policy/injection expectation types without altering originalpolicy scoring. [Original15results](../evidence/final_evaluation.md), [extra5results](../evidence/v2_extra_evaluation.md), [negative fixtures](../evidence/v2_judge_fixtures.json) include actual evidence, prompts and every score. Supported partial coverage may retain precision-like Accuracy1 while Completeness falls. Grounding1 on irrelevant excerpts does not imply answer relevance.

## Preservation and review boundaries

Version1 repository: https://github.com/nitesh2mithu/Ola-Domain-Support-Agent_all-ai_v.1
New baseline repository: https://github.com/nitesh2mithu/Ola-Domain-Support-Agent_Manuel-and-AI
V1 implementation:`66251f65dc703b38d67f6f0cc1e6006b50ca7845`; preservedhead/annotatedtagv1.0.0:`64e19e9036e160bc93109fb2766d7e15c9d0a448`. Newcheckout:`../Ola-Domain-Support-Agent_Manuel-and-AI`, branchlocal`polish-v2`only. Baselinepublicmain/tag unchanged; improvements are unpushed.

Fullbundle:`../ola-v1-backup.bundle`outside repositories. Complete reviewdiff:`../polish-v2-vs-v1.diff`outside repository; regenerate after final local commit. [Exact187moves/preservation/baselineverification](../evidence/v2_layout_changes.json) and [historicalv1report](archive/v1_FINAL_ACCEPTANCE_REPORT.md) distinguish v1 from currentv2 evidence. Freshnewenv/model/indexsetup completed without copying oldenv/weights/runtime/keys.

## Limits and closing checks

MOCK scores are deterministic lexical/extractive proxies on a smallknowncorpus, not semantic quality or safety certification. Near-domain scope and multi-topic coverage remain measured weaknesses; code is not tuned to hide them. Chunks mayrepeat/cut sentences; exact-evidence review rejects somevalidparaphrases. Python audit hooks cover exercisedPython paths,not arbitrarynativecalls/OSfirewall. Budgets simulatedceil(chars/4)atUSD0.002/1000,actualspend0. In-processsessions/cache, no productionauth, noautomaticfinancial/recordmutation. PinnedLangChaindeprecations and narrowCrewcredential-storage shim documented.

ERROR-016lookup and017archive reader were recorded before fixes and resolved after dataset8/8/crew12/12; unsuccessful attempts retained. No current errors/blockers. README177lines/13sections; LEARNINGS215words; AI note honestlydeclares assistantwork and contributionconfirmation placeholder. Normal current documentation/public-content gates PASSED: all sources and ignore rules, README177lines/13sections, LEARNINGS215words, all16currenttaskrows, noopenerrors, validfile/directorylinks. Independent broad linkcheck262targets passed; complete artifactscan findings empty. [Document audit](../evidence/final_documentation_audit.json), [content scan](../evidence/final_submission_inspection.json), [link check](../evidence/v2_final_link_check.json). FinalGitcleanstate/diff reviewed after localcommit.
