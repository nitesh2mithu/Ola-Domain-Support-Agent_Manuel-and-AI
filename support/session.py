"""LangChain owns per-session history; sanitized queries enter history/crew."""
import json
import os
import re
from smoke_tests.runtime import prepare_runtime
from rag.config import ROOT, offline_settings
prepare_runtime()
offline_settings()
os.environ.update({'LANGCHAIN_TRACING_V2':'false', 'LANGSMITH_TRACING':'false',
                   'LANGSMITH_OTEL_ENABLED':'false'})
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from rag.chunking import load_documents
from rag.core import LocalRAG
from support.models import SupportResponse
from support.guardrails import guard_input
from support.crew import kickoff_support
from support.cache import PolicyCache, StaleEvidence
from support.governance import RequestBudget, BudgetExceeded

TICKET_ID = re.compile(r'\bOLA-\d{4}\b', re.IGNORECASE)
POLICY_INTENT = re.compile(r'\b(policy|policies|refund|compensation|credit|SLA|priority|priorities|severity|holiday|hours|channels?|complaints?|VIP|outage|retention|feedback)\b', re.IGNORECASE)
TICKET_INTENT = re.compile(r'\b(ticket|status|escalat\w*|resolution|its|it|that)\b', re.IGNORECASE)
FOLLOWUP = re.compile(r'\b(its|it|that ticket|this ticket|same ticket)\b', re.IGNORECASE)


def make_plan(query: str, history: list) -> dict:
    ids = list(dict.fromkeys(x.upper() for x in TICKET_ID.findall(query)))
    if len(ids) > 1:
        # One ticket tool per request; ask explicitly rather than silently pick one.
        return {'record_id': None, 'policy_query': None, 'ticket_from_memory': False}
    record_id = ids[0] if ids else None
    from_memory = False
    if record_id is None and FOLLOWUP.search(query) and TICKET_INTENT.search(query):
        for message in reversed(history):
            if isinstance(message, AIMessage):
                previous = SupportResponse.model_validate_json(message.content)
                if previous.ticket is not None:
                    record_id = previous.ticket.record_id
                    from_memory = True
                    break
    ticket_query = bool(ids) or bool(TICKET_INTENT.search(query) and FOLLOWUP.search(query))
    needs_policy = not ticket_query or bool(POLICY_INTENT.search(query))
    # Explicit mixed requests remove record IDs and status clauses before retrieval.
    policy_query = query if needs_policy else None
    if ids and needs_policy:
        policy_query = TICKET_ID.sub('', query).strip()
    return {'record_id': record_id, 'policy_query': policy_query, 'ticket_from_memory': from_memory}


class SupportSession:
    def __init__(self, *, cache_enabled=True, token_cap=50000, cost_cap="0.10", draft_transform=None):
        self.cache=PolicyCache(cache_enabled)
        self.token_cap,self.cost_cap=token_cap,cost_cap
        self.draft_transform=draft_transform
        self.histories: dict[str, InMemoryChatMessageHistory] = {}
        self.rag = LocalRAG(load_documents())
        self.calibration = json.loads((ROOT / 'rag/calibration.json').read_text())
        if self.rag.index_fingerprint != self.calibration['index_fingerprint']:
            raise ValueError('Index identity differs from evaluated calibration')
        strategy = self.calibration['recommended_strategy']
        if self.rag.collections[strategy].count() != len(self.rag.chunks[strategy]):
            raise ValueError('Selected index not populated; run Part 1 acceptance during setup')
        self.with_history = RunnableWithMessageHistory(
            RunnableLambda(self._turn), self.get_history,
            input_messages_key='query', history_messages_key='history',
            output_messages_key='history_message')

    def get_history(self, session_id: str) -> InMemoryChatMessageHistory:
        return self.histories.setdefault(session_id, InMemoryChatMessageHistory())

    def reset(self, session_id: str) -> None:
        self.get_history(session_id).clear()

    def _turn(self, inputs: dict) -> dict:
        plan = make_plan(inputs['query'], inputs['history'])
        result = kickoff_support(plan, self.rag, self.calibration,budget=inputs["budget"],cache=self.cache,draft_transform=self.draft_transform)
        response = SupportResponse.model_validate(result['response'])
        response.guardrails = list(dict.fromkeys(inputs['input_flags'] + response.guardrails))
        response = SupportResponse.model_validate(response.model_dump())
        result.update({'response': response.model_dump(), 'plan': plan,
                       'masked_query': inputs['query'], 'history_messages_before': len(inputs['history']),
                       'history_message': AIMessage(content=response.model_dump_json())})
        return result

    def ask(self, query: str, session_id: str) -> dict:
        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError('A nonempty session_id is required')
        masked, flags, blocked = guard_input(query)
        if blocked:
            response = SupportResponse(answer='I cannot follow instructions that bypass support safeguards.',
                                       outcome='refused', guardrails=flags)
            return {'response': SupportResponse.model_validate(response.model_dump()).model_dump(),
                    'masked_query': masked, 'events': [], 'kickoff_executed': False,
                    'history_messages_before': len(self.get_history(session_id).messages)}
        budget=RequestBudget(token_cap=self.token_cap,cost_cap=self.cost_cap)
        try:
            budget.preflight(masked)
            result = self.with_history.invoke({'query': masked, 'input_flags': flags,'budget':budget},
                                             config={'configurable': {'session_id': session_id}})
        except StaleEvidence:
            response=SupportResponse(answer="Policy evidence changed; rebuild and verify the index before answering.",outcome="refused",guardrails=flags+["stale_evidence"])
            return {"response":response.model_dump(),"masked_query":masked,"events":[],"kickoff_executed":False,
                    "history_messages_before":len(self.get_history(session_id).messages)}
        except (BudgetExceeded, RuntimeError):
            if not budget.exceeded:
                raise
            response=SupportResponse(answer='Request refused because its simulated token or cost budget is insufficient.',
                                     outcome='refused',guardrails=flags+['budget_exceeded'])
            return {'response':response.model_dump(),'masked_query':masked,'events':[],
                    'kickoff_executed':budget.crew_started,'budget':budget.report(),
                    'history_messages_before':len(self.get_history(session_id).messages)}
        result.pop('history_message')
        SupportResponse.model_validate(result['response'])
        return result

    def transcript(self, session_id: str) -> list[dict]:
        return [{'role': m.type, 'content': m.content} for m in self.get_history(session_id).messages]
