"""Strict public response_format and framework intermediate results."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)


class TicketResult(StrictModel):
    record_id: str
    found: bool
    status: str | None = None
    resolution_time_hours: int | None = Field(default=None, ge=1, le=168)
    days_since_created: int | None = Field(default=None, ge=0, le=30)
    escalated: bool | None = None
    escalation_score: float | None = Field(default=None, ge=0, le=1)
    escalation_threshold: float | None = Field(default=None, ge=0, le=1)
    recommend_escalation: bool = False
    error: str | None = None

    @model_validator(mode='after')
    def consistent_lookup(self):
        values = (self.status, self.resolution_time_hours, self.days_since_created,
                  self.escalated, self.escalation_score, self.escalation_threshold)
        if self.found and (any(v is None for v in values) or self.error is not None):
            raise ValueError('Found ticket requires all evidence fields and no error')
        if not self.found and (any(v is not None for v in values) or self.recommend_escalation or not self.error):
            raise ValueError('Unknown ticket must not fabricate ticket facts')
        return self


class SupportResponse(StrictModel):
    """Declared response_format; every kickoff and returned response is validated."""
    answer: str = Field(min_length=1)
    outcome: Literal['answered', 'partial', 'not_found', 'clarification', 'refused']
    citations: list[str] = Field(default_factory=list)
    ticket: TicketResult | None = None
    guardrails: list[str] = Field(default_factory=list)


response_format = SupportResponse


class StageResult(StrictModel):
    kind: Literal['rag', 'ticket']
    requested: bool
    data: dict | None = None

    @model_validator(mode='after')
    def evidence_required(self):
        if self.requested != (self.data is not None):
            raise ValueError('Requested stage requires actual tool evidence')
        return self
