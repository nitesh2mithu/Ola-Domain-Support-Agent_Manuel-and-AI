"""Strict HTTP/WebSocket contracts; no raw validation inputs in errors."""
from typing import Literal
from pydantic import Field, field_validator
from support.models import StrictModel, SupportResponse


class SessionRequest(StrictModel):
    session_id: str = Field(min_length=1,max_length=64,pattern=r'^[A-Za-z0-9_-]+$')


class AskRequest(SessionRequest):
    query: str = Field(min_length=1)

    @field_validator('query')
    @classmethod
    def nonblank(cls,value):
        if not value.strip(): raise ValueError('Query must not be blank')
        return value


class ChatRequest(StrictModel):
    query: str = Field(min_length=1)

    @field_validator('query')
    @classmethod
    def nonblank(cls,value):
        if not value.strip(): raise ValueError('Query must not be blank')
        return value


class AskResponse(StrictModel):
    trace_id: str
    session_id: str
    response: SupportResponse
    crew_executed: bool
    history_messages_before: int = Field(ge=0)


class ResetResponse(StrictModel):
    trace_id: str
    session_id: str
    reset: bool


class APIError(StrictModel):
    trace_id: str
    error: Literal['validation_error','internal_error']
