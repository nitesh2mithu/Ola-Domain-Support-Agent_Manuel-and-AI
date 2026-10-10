"""A real CrewAI kickoff, using native tool messages and a local BaseLLM."""

import json
from typing import Any

from crewai import Agent, Crew, Process, Task
from crewai.llms.base_llm import BaseLLM
from crewai.tools import BaseTool
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr


class EchoArguments(BaseModel):
    query: str


class EchoTool(BaseTool):
    # Intentional regression case: 'lookup' in the name does not imply record_id.
    name: str = "rag_lookup"
    description: str = "Echo fabricated smoke-test text; this is not a RAG implementation."
    args_schema: type[BaseModel] = EchoArguments
    invocations: list[str] = Field(default_factory=list)

    def _run(self, query: str) -> str:
        self.invocations.append(query)
        print(f"TOOL_INVOKED name={self.name} arguments={json.dumps({'query': query})}")
        return json.dumps({"answer": f"Tool confirmed: {query}", "tool_used": True})


class CrewSmokeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    answer: str
    tool_used: bool


class DeterministicCrewLLM(BaseLLM):
    """Return tool-call requests; CrewAI itself invokes the tool.

    Native role='tool' results avoid the system template's Observation placeholder.
    Argument dispatch is based on the declared JSON schema, never the tool name.
    """
    _calls: int = PrivateAttr(default=0)
    _seen_tool_messages: int = PrivateAttr(default=0)

    def __init__(self) -> None:
        super().__init__(model="mock/local-smoke", temperature=0)

    @property
    def call_count(self) -> int:
        return self._calls

    @property
    def seen_tool_messages(self) -> int:
        return self._seen_tool_messages

    def supports_function_calling(self) -> bool:
        return True

    def get_context_window_size(self) -> int:
        return 8192

    def call(self, messages, tools=None, callbacks=None, available_functions=None,
             from_task=None, from_agent=None, response_model=None, **kwargs) -> Any:
        self._calls += 1
        if not isinstance(messages, list):
            raise ValueError("Smoke adapter requires role-labelled framework messages")
        results = [m for m in messages if m.get("role") == "tool"]
        if results:
            self._seen_tool_messages += 1
            response = CrewSmokeResponse.model_validate_json(results[-1]["content"])
            return response.model_dump_json()
        if not tools or len(tools) != 1:
            raise ValueError("Expected one framework-provided tool schema")
        function = tools[0]["function"]
        schema = function["parameters"]
        if schema.get("required") != ["query"] or "query" not in schema["properties"]:
            raise ValueError("Unsupported declared argument schema")
        return [{
            "id": "smoke_call_1",
            "type": "function",
            "function": {"name": function["name"],
                         "arguments": json.dumps({"query": "milestone-one"})},
        }]


def run_crew_smoke() -> dict:
    tool = EchoTool()
    llm = DeterministicCrewLLM()
    agent = Agent(role="Smoke Tool Agent", goal="Call the provided echo tool once.",
                  backstory="A deterministic framework integration tester.",
                  tools=[tool], llm=llm, allow_delegation=False,
                  verbose=False, max_iter=3)
    task = Task(description="Use the tool for query milestone-one and return its JSON.",
                expected_output="JSON with answer and tool_used.", agent=agent,
                output_pydantic=CrewSmokeResponse)
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential,
                memory=False, cache=False, verbose=False, tracing=False)
    result = crew.kickoff()
    validated = CrewSmokeResponse.model_validate_json(result.raw)
    assert result.pydantic is not None, "CrewAI must produce its Pydantic task output"
    assert isinstance(result.pydantic, CrewSmokeResponse)
    assert tool.invocations == ["milestone-one"], tool.invocations
    assert validated.answer == "Tool confirmed: milestone-one"
    assert validated.tool_used is True
    assert llm.call_count == 2, llm.call_count
    assert llm.seen_tool_messages == 1
    summary = {"response": validated.model_dump(), "tool_invocations": tool.invocations,
               "model_calls": llm.call_count, "tool_messages_seen": llm.seen_tool_messages}
    print("CREW_SMOKE " + json.dumps(summary, sort_keys=True))
    return summary
