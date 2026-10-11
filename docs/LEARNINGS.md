# Findings from the project record

Fixed chunking worked better for this small policy corpus, despite cutting some sentences. On the six common labelled queries, its parent-document precision and recall were 1.0 and 1.0; sentence chunking achieved 0.555556 and 1.0. The longer overlapping fragments retained useful neighbouring clauses and introduced fewer irrelevant parents. This result supports the chosen configuration here, not a general claim that fixed chunks are superior. [Retrieval calculations](../evidence/final_rag.md) show the individual fractions.

The measured cosine threshold separated three in-scope queries from two unrelated negatives. That experiment establishes a gap for those examples only. The additional cancellation query returned grounded refund excerpts without answering the requested entitlement, showing why similarity cannot establish scope or completeness. [Additional results](../evidence/v2_extra_evaluation.md) preserve that weakness.

A documented lookup bug accessed reopening data through an undefined variable after an automated edit. Dataset checks passed, but the real crew failed before its tests could run. Correcting the record reference and rerunning the complete crew suite verified the fix; [the error history](ERROR_LOG.md) retains both failed attempts. Separate schema-dispatch and ReAct-template regression checks protect tool integration.

A real LLM would require independently labelled semantic evaluations, stronger evidence-entailment review, provider-specific token accounting, latency and retry testing, and broader safety cases. Deterministic MOCK results would remain regression controls rather than proof of real-model performance.
