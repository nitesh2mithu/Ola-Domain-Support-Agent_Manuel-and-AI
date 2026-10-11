# Version 2 changes

## Layout
Exact moves and path-only config-manifest changes: [layout record](../evidence/v2_layout_changes.json). Archived v1 records describe v1 code only.

## Intended escalation behavior
New independent reopen_count stream seed+1; original fields/draw order unchanged. Formula changed from0.6flag+0.4age to0.4flag+0.3age+0.3reopen. Round scores to6 decimals, nearest-rankp80, strictgreater-than excludes ties. Old/new dataset hashes, thresholds and all selected examples: [single change record](../evidence/v2_escalation_change.json). Test formula/threshold expectations explicitly updated, range/type negative cases strengthened, original-record invariance asserted against preserved v1 evidence. Active protected dataset.py digest updated; archived digests preserved. Dataset8/8, CrewAI12/12 and all60 independently calculated actual lookups verified. Errors016/017 fixed and verified; original failure evidence retained.

## Evaluation extension
Original15labels,judgeprompt/rubric unchanged. Five additionalcases frozenbeforeexecution with new generic refusal/injection expectation types, not modified originalmetrics. Results: original15 means1.0 allfour; additional5 Accuracy0.8/Grounding1.0/Completeness0.7/Safety1.0. X01relatedrefundquotes failed requiredrefusal; X04missing2of4facts. Five meaningful fixture/arithmetic checks passed, including unsupported inference/partial/unsafe/forgedguard evidence. No crew/query/calibration tuning. See [freeze](../evidence/v2_extra_freeze.json), [extra results](../evidence/v2_extra_evaluation.md), [fixtures](../evidence/v2_judge_fixtures.json).

## Readability and current verification
README177lines in requestedsectionorder; learnings215words; AI assistance explicit, personalcontributionsconfirmation pending. Fullcurrentv2suite56distinct/76executions plus29realrequests/logs andindependentall16audit executed successfully. Original15andextra5reportsrepeatidentically; source/labels/calibration unchanged exceptdeclared score/reopen/path/evaluation-extension work. Documentation/content gates passed previously and are being freshly repeated in the final local review.

## Final review corrections

Fresh runtime verification passed all56 distinct checks /76 executions,29 real HTTP/WebSocket requests, repeated15+5 evaluations and the independent all16 audit. No application or scoring changes during review. The additional2 documentation behavior checks pass.

ERROR-019 corrected macOS temporary-path canonicalization in the new reproducible history review helper. ERROR-020 corrected a historical audit link-base variable, supported contained directory links and redirected audit output to excluded runtime storage, protecting archived reports. Existing stage assertions remain intact. Failed attempts were retained before fixes; both errors were resolved only after actual verification.

[Review evidence](../evidence/v2_final_review.json) includes reachable-history hygiene, archive preservation, exact dependency pins and independent old/new score arithmetic. Local commits9711d22 and a4b3427 separate these corrections. The final evidence/documentation refresh is a separate local commit; no improvement push or merge.
