# Version 2 changes

## Layout
Exact moves and path-only config-manifest changes: [layout record](../evidence/v2_layout_changes.json). Archived v1 records describe v1 code only.

## Intended escalation behavior
New independent reopen_count stream seed+1; original fields/draw order unchanged. Formula changed from0.6flag+0.4age to0.4flag+0.3age+0.3reopen. Round scores to6 decimals, nearest-rankp80, strictgreater-than excludes ties. Old/new dataset hashes, thresholds and all selected examples: [single change record](../evidence/v2_escalation_change.json). Test formula/threshold expectations explicitly updated, range/type negative cases strengthened, original-record invariance asserted against preserved v1 evidence. Active protected dataset.py digest updated; archived digests preserved. Dataset8/8, CrewAI12/12 and all60 independently calculated actual lookups verified. Errors016/017 fixed and verified; original failure evidence retained.
