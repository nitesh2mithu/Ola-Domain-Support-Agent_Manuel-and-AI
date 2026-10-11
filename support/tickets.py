"""Read-only deterministic triage; formula/percentile computed from generated data."""
import math
import re
from dataset import SUPPORT_TICKETS
from support.models import TicketResult


def escalation_score(escalated: bool, days_since_created: int, reopen_count: int = 0) -> float:
    if type(escalated) is not bool or type(days_since_created) is not int or not 0 <= days_since_created <= 30 or type(reopen_count) is not int or not 0 <= reopen_count <= 3:
        raise ValueError('Expected boolean flag, integer age in [0,30], integer reopen_count in [0,3]')
    # Age = 1 - recency; older tickets have more triage urgency.
    return round(0.4 * int(escalated) + 0.3 * days_since_created / 30 + 0.3 * reopen_count / 3, 6)


def distribution_report() -> dict:
    scores = sorted(escalation_score(t['escalated'], t['days_since_created'], t['reopen_count']) for t in SUPPORT_TICKETS)
    rank = math.ceil(0.8 * len(scores))
    threshold = scores[rank - 1]
    return {'formula': 'round(0.4*int(escalated) + 0.3*(days_since_created/30) + 0.3*(reopen_count/3), 6)',
            'normalized_recency': '1 - days_since_created/30; age signal = 1 - normalized_recency',
            'percentile_method': 'nearest rank: ceil(0.8*N), strict score > threshold',
            'record_count': len(scores), 'rank': rank, 'threshold': threshold,
            'scores_sorted': scores, 'above_threshold': sum(s > threshold for s in scores),
            'at_threshold': scores.count(threshold), 'min': min(scores), 'max': max(scores)}


ESCALATION_THRESHOLD = distribution_report()['threshold']


def check_support_ticket_status(record_id: str) -> dict:
    if not isinstance(record_id, str):
        raise TypeError('record_id must be a string')
    record_id = record_id.strip().upper()
    if not re.fullmatch(r'OLA-\d{4}', record_id):
        return TicketResult(record_id=record_id, found=False, error='invalid_record_id').model_dump()
    ticket = next((t for t in SUPPORT_TICKETS if t['record_id'] == record_id), None)
    if ticket is None:
        return TicketResult(record_id=record_id, found=False, error='unknown_record_id').model_dump()
    score = escalation_score(ticket['escalated'], ticket['days_since_created'], ticket['reopen_count'])
    return TicketResult(record_id=record_id, found=True, status=ticket['status'],
        resolution_time_hours=ticket['resolution_time_hours'], days_since_created=ticket['days_since_created'],
        escalated=ticket['escalated'], reopen_count=ticket['reopen_count'], escalation_score=score, escalation_threshold=ESCALATION_THRESHOLD,
        recommend_escalation=score > ESCALATION_THRESHOLD).model_dump()
