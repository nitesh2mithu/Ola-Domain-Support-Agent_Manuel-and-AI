"""Real CrewAI native function calling; no remote LLM/provider selection."""
import asyncio
from contextvars import ContextVar
import json
import os
from typing import Any
from smoke_tests.runtime import prepare_runtime, configure_project_credential_storage
from rag.config import offline_settings

# Required even when imported outside the acceptance runner.
prepare_runtime()
offline_settings()
os.environ.update({'LANGCHAIN_TRACING_V2': 'false', 'LANGSMITH_TRACING': 'false',
                   'LANGSMITH_OTEL_ENABLED': 'false'})
configure_project_credential_storage()

from crewai import Agent, Crew, Process, Task
from crewai.llms.base_llm import BaseLLM
from crewai.tools import BaseTool
from crewai.hooks import register_before_tool_call_hook, register_after_tool_call_hook
from pydantic import BaseModel, PrivateAttr
from rag.core import grounded_answer
from support.models import StageResult, SupportResponse
from support.guardrails import compose_evidence, guard_output
from support.tickets import check_support_ticket_status
from support.governance import RequestBudget
from support.review import review_draft

_TICKET_PERMIT = ContextVar("ticket_permit", default=None)

def authorize_ticket_call(context):
    owner=getattr(getattr(context.tool,"func",None),"__self__",None)
    if isinstance(owner,TicketTool):
        _TICKET_PERMIT.set(None)
        if context.agent is not owner._authorized_agent or context.agent is None:
            owner._events.append({"event":"ticket_access_rejected","role":getattr(context.agent,"role",None)})
            return False
        _TICKET_PERMIT.set(owner)
    return None

def clear_ticket_call(context):
    _TICKET_PERMIT.set(None)
    return None

register_before_tool_call_hook(authorize_ticket_call)
register_after_tool_call_hook(clear_ticket_call)


class PolicyArguments(BaseModel):
    query: str


class TicketArguments(BaseModel):
    record_id: str


class PolicyTool(BaseTool):
    # 'lookup' is deliberately ambiguous: argument dispatch MUST use schema.
    name: str = 'rag_lookup'
    description: str = 'Retrieve policy excerpts from the evaluated local fixed-chunk Chroma collection.'
    args_schema: type[BaseModel] = PolicyArguments
    _rag: Any = PrivateAttr()
    _calibration: dict = PrivateAttr()
    _events: list = PrivateAttr()

    def __init__(self, rag, calibration, events):
        super().__init__()
        self._rag, self._calibration, self._events = rag, calibration, events

    def _run(self, query: str) -> str:
        strategy = self._calibration['recommended_strategy']
        threshold = self._calibration['thresholds'][strategy]
        hits = self._rag.retrieve(query, strategy, self._calibration['top_k_chunks'])
        result = grounded_answer(hits, threshold)
        result.update({'hits': hits, 'threshold': threshold, 'strategy': strategy,
                       'collection': self._rag.collections[strategy].name})
        self._events.append({'event': 'tool_executed', 'kind': 'rag', 'tool': self.name,
                             'arguments': {'query': query}, 'result': result})
        return json.dumps(result, sort_keys=True)


class TicketTool(BaseTool):
    name: str = 'check_support_ticket_status'
    description: str = 'Read a generated ticket by record_id, including deterministic escalation triage.'
    args_schema: type[BaseModel] = TicketArguments
    _events: list = PrivateAttr()
    _authorized_agent: Any = PrivateAttr(default=None)

    def __init__(self, events):
        super().__init__()
        self._events = events

    def _run(self, record_id: str) -> str:
        if _TICKET_PERMIT.get() is not self or self._authorized_agent is None:
            self._events.append({"event":"ticket_boundary_rejected"})
            raise PermissionError("Only the designated Lookup agent may execute the ticket tool")
        _TICKET_PERMIT.set(None)  # One-use capability, also cleared after framework execution.
        result = check_support_ticket_status(record_id)
        self._events.append({'event': 'tool_executed', 'kind': 'ticket', 'tool': self.name,
                             'arguments': {'record_id': record_id}, 'result': result})
        return json.dumps(result, sort_keys=True)


def schema_arguments(function: dict, plan: dict) -> dict:
    """Dispatch from declared parameter schema, never tool-name substrings."""
    schema = function['parameters']
    required = schema.get('required', [])
    properties = schema.get('properties', {})
    if required == ['query'] and properties.get('query', {}).get('type') == 'string':
        return PolicyArguments(query=plan['policy_query']).model_dump()
    if required == ['record_id'] and properties.get('record_id', {}).get('type') == 'string':
        return TicketArguments(record_id=plan['record_id']).model_dump()
    raise ValueError('Unsupported declared tool argument schema')


class MOCK_LLM(BaseLLM):
    """Input-responsive deterministic adapter using CrewAI's BaseLLM extension.

    The framework invokes tools. Only role=tool messages supply tool evidence;
    system/ReAct Observation placeholders are never parsed. Composer consumes
    actual preceding Task.output values supplied through CrewAI task context.
    """
    _kind: str = PrivateAttr()
    _plan: dict = PrivateAttr()
    _events: list = PrivateAttr()
    _calls: int = PrivateAttr(default=0)
    _budget: Any = PrivateAttr()
    _cached_policy: Any = PrivateAttr(default=None)

    def __init__(self, kind: str, plan: dict, events: list, budget=None, cached_policy=None):
        super().__init__(model='mock/local-support', temperature=0)
        self._kind, self._plan, self._events = kind, plan, events
        self._budget=budget or RequestBudget()
        self._cached_policy=cached_policy

    def supports_function_calling(self) -> bool:
        return True

    def get_context_window_size(self) -> int:
        return 32768

    def call(self, messages, **kwargs):
        output=self._answer(messages, **kwargs)
        self._budget.charge("CrewAI/"+self._kind,{"messages":messages,"tools":kwargs.get("tools")},output)
        self._events.append({"event":"model_call","kind":self._kind})
        return output

    def _answer(self, messages, tools=None, callbacks=None, available_functions=None,
             from_task=None, from_agent=None, response_model=None, **kwargs):
        self._calls += 1
        if not isinstance(messages, list) or from_task is None:
            raise ValueError('Requires actual CrewAI messages and task')
        if self._kind == 'composer':
            stages = [StageResult.model_validate_json(t.output.raw) for t in from_task.context]
            response = compose_evidence(stages)
            self._events.append({'event': 'composer_consumed_context',
                                 'task_outputs': [s.model_dump() for s in stages]})
            return response.model_dump_json()
        requested = bool(self._plan['policy_query']) if self._kind == 'rag' else bool(self._plan['record_id'])
        if not requested:
            self._events.append({'event': 'stage_not_requested', 'kind': self._kind})
            return StageResult(kind=self._kind, requested=False).model_dump_json()
        if self._kind=='rag' and self._cached_policy is not None:
            self._events.append({'event':'policy_cache_hit','kind':'rag','result':self._cached_policy})
            return StageResult(kind='rag',requested=True,data=self._cached_policy).model_dump_json()
        tool_messages = [m for m in messages if m.get('role') == 'tool']
        if tool_messages:
            actual = json.loads(tool_messages[-1]['content'])
            self._events.append({'event': 'model_consumed_tool_result', 'kind': self._kind,
                                 'result': actual})
            return StageResult(kind=self._kind, requested=True, data=actual).model_dump_json()
        if not tools or len(tools) != 1:
            raise ValueError('Expected exactly one tool declared by this agent')
        function = tools[0]['function']
        args = schema_arguments(function, self._plan)
        self._events.append({'event': 'model_requested_tool', 'kind': self._kind,
                             'declared_schema': function['parameters'],
                             'tool': function['name'], 'arguments': args})
        return [{'id': f'{self._kind}_call_{self._calls}', 'type': 'function',
                 'function': {'name': function['name'], 'arguments': json.dumps(args)}}]


def kickoff_support(plan: dict, rag, calibration: dict, *, budget=None, cache=None, draft_transform=None) -> dict:
    budget=budget or RequestBudget()
    events = []
    key=cache.key(plan["policy_query"],rag,calibration) if cache and plan["policy_query"] else None
    cached=cache.get(key) if key else None
    retrieval_tool = PolicyTool(rag, calibration, events)
    lookup_tool = TicketTool(events)
    agents = []
    for kind, role, tools in [('rag', 'Retrieval Agent', [retrieval_tool]),
                              ('ticket', 'Lookup Agent', [lookup_tool]),
                              ('composer', 'Response Composer', [])]:
        agents.append(Agent(role=role, goal='Use actual declared evidence and return strict JSON.',
            backstory='A deterministic offline support specialist; make no unsupported claims.',
            llm=MOCK_LLM(kind, plan, events, budget, cached), tools=tools, allow_delegation=False,
            verbose=False, max_iter=3))
    lookup_tool._authorized_agent=agents[1]
    tasks = [Task(description='Retrieve policies if the masked request has a policy question: '+json.dumps(plan),
                  expected_output='StageResult JSON with actual tool evidence or requested=false.',
                  agent=agents[0], output_pydantic=StageResult),
             Task(description='Look up a ticket when a specific reference is available: '+json.dumps(plan),
                  expected_output='StageResult JSON with actual tool evidence or requested=false.',
                  agent=agents[1], output_pydantic=StageResult)]
    tasks.append(Task(description='Combine the preceding actual task outputs into a grounded response_format.',
                      expected_output='SupportResponse JSON, supported facts or explicit refusal.',
                      agent=agents[2], context=tasks[:], output_pydantic=SupportResponse))
    crew = Crew(agents=agents, tasks=tasks, process=Process.sequential, verbose=False,
                memory=False, cache=False, tracing=False)
    budget.crew_started=True
    result = crew.kickoff()
    draft = SupportResponse.model_validate_json(result.raw)
    if not isinstance(result.pydantic, SupportResponse):
        raise ValueError('CrewAI did not produce the declared Pydantic response_format')
    stages = [StageResult.model_validate_json(t.output.raw) for t in tasks[:2]]
    actual_results = {e['kind']: e['result'] for e in events if e['event'] in ('tool_executed','policy_cache_hit')}
    review_input=SupportResponse.model_validate(draft_transform(draft.model_copy(deep=True)).model_dump()) if draft_transform else draft
    review=asyncio.run(review_draft(review_input,stages,actual_results,budget))
    candidate=compose_evidence(stages)
    candidate.answer=review['verdict']['final_answer']
    safe = guard_output(candidate, stages, actual_results)
    safe = SupportResponse.model_validate_json(safe.model_dump_json())
    if key and cached is None and "rag" in actual_results:
        cache.put(key,actual_results["rag"])
    return {'response': safe.model_dump(), 'draft': draft.model_dump(),
            'review_draft':review_input.model_dump(),'review':review,'budget':budget.report(),
            'cache':cache.counters() if cache else {'enabled':False},
            'stages': [s.model_dump() for s in stages], 'events': events,
            'agents': [{'role': a.role, 'tools': [t.name for t in a.tools]} for a in agents],
            'kickoff_executed': True, 'framework_pydantic_validated': True}
