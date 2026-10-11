"""Five preregistered extra cases, actual application, zero-key offline execution."""
import argparse,hashlib,json
from pathlib import Path
from smoke_tests.runtime import prepare_runtime,install_offline_audit,NETWORK_ATTEMPTS,FORBIDDEN_PROCESS_ATTEMPTS
prepare_runtime();install_offline_audit()
from rag.config import ROOT
from support.session import SupportSession
from support.models import SupportResponse
from evaluation.extra_judge import ExtraJudge,extra_messages
from evaluation.judge import JudgeVerdict

def verify_freeze():
    frozen=json.loads((ROOT/'evidence/v2_extra_freeze.json').read_text())
    for file,digest in frozen['sha256'].items():assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==digest,file
    cases=json.loads((ROOT/'evaluation/extra_queries.json').read_text())
    assert len(cases)==5 and len({c['id'] for c in cases})==5
    assert [c['group'] for c in cases].count('near_domain')==2 and [c['group'] for c in cases].count('ambiguous_multi_topic')==2
    assert [c['group'] for c in cases].count('injection_fabricated_pii')==1
    return frozen,cases

def evaluate():
    frozen,cases=verify_freeze();app=SupportSession(cache_enabled=False);judge=ExtraJudge();results=[]
    for case in cases:
        query=case['query'].replace('[FABRICATED_PHONE]','98765'+'43210')
        execution=app.ask(query,'extra-'+case['id']);SupportResponse.model_validate(execution['response'])
        tools={e['kind']:e['result'] for e in execution['events'] if e['event']=='tool_executed'}
        tools['input_guard']={'masked_query':execution['masked_query'],'kickoff_executed':execution['kickoff_executed'],'event_count':len(execution['events'])}
        messages=extra_messages(case,execution['response'],tools);verdict=JudgeVerdict.model_validate_json(judge.call(messages))
        results.append({'case':case,'execution':execution,'judge_messages':messages,'verdict':verdict.model_dump()})
    metrics=('Accuracy','Grounding','Completeness','Safety');sums={m:sum(r['verdict'][m] for r in results) for m in metrics}
    report={'query_count':5,'frozen_input_hashes':frozen['sha256'],'model':judge.model,'results':results,'metric_sums':sums,'averages':{m:v/5 for m,v in sums.items()},'offline':{'network_attempts':list(NETWORK_ATTEMPTS),'child_process_attempts':list(FORBIDDEN_PROCESS_ATTEMPTS)}}
    assert not NETWORK_ATTEMPTS and not FORBIDDEN_PROCESS_ATTEMPTS
    assert '98765'+'43210' not in json.dumps(report)
    return report

def markdown(r):
    lines=['# Five additional queries — actual v2 results','','Original15 averages are reported separately. Frozen labels/rules are unchanged after execution.','','| ID | Group | Accuracy | Grounding | Completeness | Safety |','|---|---|---:|---:|---:|---:|']
    for item in r['results']:lines.append('| '+item['case']['id']+' | '+item['case']['group']+' | '+' | '.join(f"{item['verdict'][m]:.6f}" for m in r['averages'])+' |')
    for m in r['averages']:lines.append(f"\n{m}: {r['metric_sums'][m]}/5 = {r['averages'][m]:.12f}")
    for item in r['results']:lines+=['', '## '+item['case']['id'], '',item['case']['query'],'','```json',json.dumps({'response':item['execution']['response'],'verdict':item['verdict']},indent=2,sort_keys=True),'```']
    return '\n'.join(lines)+'\n'

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--report',type=Path,default=ROOT/'evidence/v2_extra_evaluation.json');args=p.parse_args();r=evaluate()
    args.report.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');args.report.with_suffix('.md').write_text(markdown(r))
    print(json.dumps({'query_count':5,'averages':r['averages'],'offline':r['offline']},indent=2))
