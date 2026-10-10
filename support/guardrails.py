"""Deterministic fixed-format input masking and evidence-only output boundary."""
import re
from support.models import StageResult, SupportResponse, TicketResult

# Fabricated examples only. Indian 10-digit mobile numbers, optional +91/91,
# optional spaces/hyphens; digit boundaries avoid masking ticket IDs.
PHONE = re.compile(r'(?<!\d)(?:(?:\+91|91)[ -]?)?[6-9](?:[ -]?\d){9}(?!\d)')
INJECTION = re.compile(
    r'ignore\s+(?:(?:all|the)\s+)?(?:previous|prior|above|system)\s+(?:instructions?|rules?|prompts?)'
    r'|(?:reveal|print|show)\s+(?:the\s+)?(?:system\s+prompt|api\s*keys?|secrets?)'
    r'|(?:bypass|disable)\s+(?:the\s+)?(?:guardrails?|safety|filters?)'
    r'|(?:system|developer)\s*:\s*(?:override|ignore)', re.IGNORECASE)


def guard_input(query: str) -> tuple[str, list[str], bool]:
    if not isinstance(query, str) or not query.strip():
        raise ValueError('A nonempty text query is required')
    masked, count = PHONE.subn('[PHONE_MASKED]', query.strip())
    flags = ['phone_masked'] if count else []
    blocked = bool(INJECTION.search(masked))
    if blocked:
        flags.append('injection_detected')
    return masked, flags, blocked


def compose_evidence(stages: list[StageResult]) -> SupportResponse:
    """Verbatim RAG excerpts + literal ticket facts; no unsupported new claims."""
    rag = next(s.data for s in stages if s.kind == 'rag')
    lookup = next(s.data for s in stages if s.kind == 'ticket')
    ticket = TicketResult.model_validate(lookup) if lookup is not None else None
    parts, citations = [], []
    unsupported = rag is not None and rag['fallback']
    if ticket is not None:
        if ticket.found:
            parts.append(f"Ticket {ticket.record_id}: status {ticket.status}; resolution_time_hours "
                         f"{ticket.resolution_time_hours}; escalation_score {ticket.escalation_score:.6f}; "
                         f"recommend_escalation {str(ticket.recommend_escalation).lower()} "
                         f"(score > {ticket.escalation_threshold:.6f}).")
        else:
            parts.append(f'Ticket {ticket.record_id} was not found ({ticket.error}).')
    if rag is not None:
        parts.append(rag['answer'])
        citations = list(rag['citations'])
    if not parts:
        return SupportResponse(answer='Please provide a ticket ID such as OLA-0001; this conversation has no ticket reference.',
                               outcome='clarification')
    if unsupported:
        outcome = 'partial' if ticket is not None and ticket.found else 'refused'
    elif ticket is not None and not ticket.found:
        outcome = 'partial' if rag is not None else 'not_found'
    else:
        outcome = 'answered'
    return SupportResponse(answer='\n\n'.join(parts), outcome=outcome, citations=citations, ticket=ticket,
                           guardrails=['groundedness_refusal'] if unsupported else [])


def guard_output(draft: SupportResponse, stages: list[StageResult], actual_results: dict) -> SupportResponse:
    """Accept only exact evidence rendering and actual executed tool results.

    A citation alone is insufficient. Check the complete answer and structured
    facts against trusted tool results captured at execution, not against claims
    produced by the model. Unsupported retrieval yields the measured fallback.
    """
    for stage in stages:
        if stage.data != actual_results.get(stage.kind):
            return SupportResponse(answer='I cannot answer because the draft evidence is unsupported.',
                                   outcome='refused', guardrails=['groundedness_refusal'])
    expected = compose_evidence(stages)
    if draft.model_dump() != expected.model_dump():
        return SupportResponse(answer='I cannot answer because the draft contains unsupported claims.',
                               outcome='refused', guardrails=['groundedness_refusal'])
    return SupportResponse.model_validate(expected.model_dump())
