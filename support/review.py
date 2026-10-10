"""Real two-agent AutoGen evidence-only review after the CrewAI Composer."""
import json
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import StructuredMessage
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core.models import CreateResult, RequestUsage
from smoke_tests.review_smoke import VerdictModel, DeterministicReviewClient
from support.models import StageResult, SupportResponse
from support.guardrails import compose_evidence, guard_output
from support.governance import token_units

class ReviewClient(DeterministicReviewClient):
    def __init__(self,role,budget):
        super().__init__(role)
        self.budget=budget

    async def create(self,messages,*,tools=(),tool_choice='auto',json_output=None,
                     extra_create_args=None,cancellation_token=None):
        if tools:raise ValueError('Review agents cannot use tools')
        payloads=[]
        for m in messages:
            c=getattr(m,'content',None)
            if isinstance(c,str):
                try:v=json.loads(c)
                except ValueError:continue
                if isinstance(v,dict) and set(v)=={'draft','stages','original_context'}:payloads.append(v)
        if len(payloads)!=1:raise ValueError('Missing original review evidence')
        p=payloads[0]
        stages=[StageResult.model_validate(s) for s in p['stages']]
        expected=guard_output(compose_evidence(stages),stages,p['original_context'])
        draft=SupportResponse.model_validate(p['draft'])
        approved=draft.model_dump()==expected.model_dump()
        reason='Draft matches original tool evidence.' if approved else 'Replaced unsupported draft content with original evidence-only rendering.'
        if self.role=='reviewer':
            content=json.dumps({'supported':approved,'reason':reason,'evidence_kinds':sorted(p['original_context'])},sort_keys=True)
        else:
            if not any(getattr(m,'source',None)=='Policy_Compliance_Reviewer' for m in messages):
                raise ValueError('Editor requires actual preceding reviewer message')
            if json_output is not VerdictModel:raise ValueError('Missing structured verdict configuration')
            self.structured_requested=True
            content=VerdictModel(approved=approved,final_answer=expected.answer,reason=reason).model_dump_json()
        inputs=[{'role':type(m).__name__,'source':getattr(m,'source',None),'content':str(getattr(m,'content',''))} for m in messages]
        inputs={'messages':inputs,'structured_output_schema':VerdictModel.model_json_schema() if json_output is VerdictModel else None}
        self.budget.charge('AutoGen/'+self.role,inputs,content)
        prompt,completion=token_units(inputs),token_units(content)
        self.calls+=1;self.usage.prompt_tokens+=prompt;self.usage.completion_tokens+=completion
        return CreateResult(finish_reason='stop',content=content,usage=RequestUsage(prompt,completion),cached=False)

async def review_draft(draft,stages,original_context,budget):
    clients=[ReviewClient('reviewer',budget),ReviewClient('editor',budget)]
    agents=[AssistantAgent('Policy_Compliance_Reviewer',model_client=clients[0],
                system_message='Compare the structured draft with the original evidence. Identify unsupported claims; use no outside knowledge.'),
            AssistantAgent('Final_Editor',model_client=clients[1],output_content_type=VerdictModel,
                system_message='Consider the reviewer and original evidence; return approved, evidence-only final_answer and reason.')]
    team=RoundRobinGroupChat(agents,max_turns=2,custom_message_types=[StructuredMessage[VerdictModel]])
    payload={'draft':draft.model_dump(),'stages':[s.model_dump() for s in stages],'original_context':original_context}
    try:
        result=await team.run(task=json.dumps(payload,sort_keys=True))
        speakers=[m.source for m in result.messages if m.source!='user']
        if speakers!=['Policy_Compliance_Reviewer','Final_Editor']:raise ValueError('Review turn bound/order violated')
        if not isinstance(result.messages[-1],StructuredMessage):raise ValueError('Unstructured review verdict')
        verdict=VerdictModel.model_validate(result.messages[-1].content.model_dump())
        return {'verdict':verdict.model_dump(),'speakers':speakers,'max_turns':2,
                'custom_message_type':'StructuredMessage[VerdictModel]','structured_requested':clients[1].structured_requested,
                'model_calls':[c.calls for c in clients],
                'transcript':[{'source':m.source,'content':m.content.model_dump() if isinstance(m,StructuredMessage) else str(m.content)} for m in result.messages]}
    finally:
        for c in clients:await c.close()
