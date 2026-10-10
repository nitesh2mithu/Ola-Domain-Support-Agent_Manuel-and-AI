"""Two real AutoGen turns, with deterministic evidence-sensitive review."""

import json
from typing import Any

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import StructuredMessage
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core.models import ChatCompletionClient, CreateResult, RequestUsage
from pydantic import BaseModel, ConfigDict


class VerdictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    approved: bool
    final_answer: str
    reason: str


class DeterministicReviewClient(ChatCompletionClient):
    """Smoke-only extractive reviewer; no remote provider or canned case lookup."""
    def __init__(self, role: str) -> None:
        self.role = role
        self.calls = 0
        self.usage = RequestUsage(prompt_tokens=0, completion_tokens=0)
        self.closed = False
        self.structured_requested = False

    async def create(self, messages, *, tools=(), tool_choice="auto", json_output=None,
                     extra_create_args=None, cancellation_token=None) -> CreateResult:
        if tools:
            raise ValueError("Review smoke agents must have no tools")
        payloads = []
        for message in messages:
            content = getattr(message, "content", None)
            if isinstance(content, str):
                try:
                    value = json.loads(content)
                except json.JSONDecodeError:
                    continue
                if isinstance(value, dict) and set(value) == {"draft", "context"}:
                    payloads.append(value)
        if len(payloads) != 1:
            raise ValueError("Expected one task message containing draft and context")
        payload = payloads[0]
        context = payload["context"]
        draft = payload["draft"]
        approved = draft == context
        if self.role == "reviewer":
            content = "Draft matches evidence." if approved else "Unsupported addition: use only the supplied context."
        else:
            # Require the real preceding agent's message; team order is verified.
            if not any(getattr(m, "source", None) == "Policy_Compliance_Reviewer" for m in messages):
                raise ValueError("Final Editor did not receive the reviewer message")
            if json_output is not VerdictModel:
                raise ValueError("Framework did not request the Pydantic verdict schema")
            self.structured_requested = True
            content = VerdictModel(
                approved=approved, final_answer=draft if approved else context,
                reason="Draft matches supplied evidence." if approved else "Removed claim absent from supplied evidence.",
            ).model_dump_json()
        self.calls += 1
        prompt_tokens = self.count_tokens(messages)
        completion_tokens = len(content.split())
        self.usage.prompt_tokens += prompt_tokens
        self.usage.completion_tokens += completion_tokens
        return CreateResult(finish_reason="stop", content=content,
                            usage=RequestUsage(prompt_tokens, completion_tokens), cached=False)

    async def create_stream(self, messages, **kwargs):
        yield await self.create(messages, **kwargs)

    async def close(self) -> None:
        self.closed = True

    def actual_usage(self) -> RequestUsage:
        return RequestUsage(self.usage.prompt_tokens, self.usage.completion_tokens)

    def total_usage(self) -> RequestUsage:
        return self.actual_usage()

    def count_tokens(self, messages, *, tools=()) -> int:
        # Deterministic simulated whitespace units, not a provider tokenizer.
        return sum(len(str(getattr(m, "content", "")).split()) for m in messages)

    def remaining_tokens(self, messages, *, tools=()) -> int:
        return 8192 - self.count_tokens(messages, tools=tools)

    @property
    def capabilities(self) -> dict[str, Any]:
        return {"vision": False, "function_calling": False, "json_output": True}

    @property
    def model_info(self) -> dict[str, Any]:
        return {**self.capabilities, "family": "unknown", "structured_output": True}


async def run_review_smoke(draft: str, context: str) -> dict:
    reviewer_client = DeterministicReviewClient("reviewer")
    editor_client = DeterministicReviewClient("editor")
    reviewer = AssistantAgent("Policy_Compliance_Reviewer", model_client=reviewer_client,
                              system_message="Compare draft with supplied evidence. Flag unsupported additions.")
    editor = AssistantAgent("Final_Editor", model_client=editor_client,
                            system_message="Return an approval or evidence-only revision with reason.",
                            output_content_type=VerdictModel)
    team = RoundRobinGroupChat([reviewer, editor], max_turns=2,
                              custom_message_types=[StructuredMessage[VerdictModel]])
    try:
        result = await team.run(task=json.dumps({"draft": draft, "context": context}))
        speakers = [m.source for m in result.messages if m.source != "user"]
        assert speakers == ["Policy_Compliance_Reviewer", "Final_Editor"], speakers
        final_message = result.messages[-1]
        assert isinstance(final_message, StructuredMessage)
        verdict = VerdictModel.model_validate(final_message.content.model_dump())
        assert reviewer_client.calls == editor_client.calls == 1
        assert editor_client.structured_requested
        summary = {"speakers": speakers, "verdict": verdict.model_dump(),
                   "model_calls": [reviewer_client.calls, editor_client.calls]}
        print("AUTOGEN_SMOKE " + json.dumps(summary, sort_keys=True))
        return summary
    finally:
        await reviewer_client.close()
        await editor_client.close()
