"""Execute exactly 15 frozen queries through the fixed crew and local judge."""
import argparse
import hashlib
import json
from pathlib import Path
from smoke_tests.runtime import prepare_runtime,install_offline_audit,NETWORK_ATTEMPTS,FORBIDDEN_PROCESS_ATTEMPTS
prepare_runtime();install_offline_audit()
from rag.config import ROOT
from support.session import SupportSession
from support.models import SupportResponse
from evaluation.judge import DeterministicJudge,JudgeVerdict,judge_messages


def verify_freeze():
    manifest=json.loads((ROOT/'evidence/archive/v1/milestone_05_evaluation_freeze.json').read_text())
    for file,digest in manifest['sha256'].items():
        if hashlib.sha256((ROOT/file).read_bytes()).hexdigest()!=digest:
            raise ValueError('Preregistered evaluation inputs changed: '+file)
    cases=json.loads((ROOT/'evaluation/support_queries.json').read_text())
    assert len(cases)==15 and len({c['id'] for c in cases})==15
    assert {c['topic'] for c in cases if c['kind']=='policy'}=={p.stem for p in (ROOT/'knowledge_base').glob('*.md')}
    assert sum(c['kind']=='out_of_scope' for c in cases)>=2
    return manifest,cases


def evaluate():
    manifest,cases=verify_freeze()
    app=SupportSession();judge=DeterministicJudge();results=[]
    for case in cases:
        execution=app.ask(case['query'],'eval-'+case['id'])
        SupportResponse.model_validate(execution['response'])
        tools={e['kind']:e['result'] for e in execution['events'] if e['event']=='tool_executed'}
        messages=judge_messages(case,execution['response'],tools)
        verdict=JudgeVerdict.model_validate_json(judge.call(messages))
        results.append({'case':case,'execution':execution,'judge_messages':messages,'verdict':verdict.model_dump()})
    sums={m:sum(r['verdict'][m] for r in results) for m in ('Accuracy','Grounding','Completeness','Safety')}
    return {'query_count':len(results),'frozen_input_hashes':manifest['sha256'],'model':judge.model,
            'results':results,'metric_sums':sums,'averages':{m:v/15 for m,v in sums.items()},
            'offline':{'network_attempts':list(NETWORK_ATTEMPTS),'child_process_attempts':list(FORBIDDEN_PROCESS_ATTEMPTS)}}


def markdown(report):
    lines=['# Part 3 — actual 15-query MOCK_LLM judge evaluation','',
           'Frozen original labels/fact groups/rubric, fixed existing crew and calibrated fixed index. All metrics on [0,1]. These are transparent lexical/extractive proxies, not a semantic model benchmark.','',
           '| ID | Topic/kind | Accuracy | Grounding | Completeness | Safety |','|---|---|---:|---:|---:|---:|']
    for r in report['results']:
        c,v=r['case'],r['verdict'];lines.append(f"| {c['id']} | {c['topic'] or c['kind']} | "+' | '.join(f'{v[m]:.6f}' for m in report['averages'])+' |')
    lines+=['','## Averages and arithmetic','']
    for m,average in report['averages'].items():lines.append(f"- {m}: {report['metric_sums'][m]} /15 = {average:.12f}.")
    for r in report['results']:
        lines += ['',f"## {r['case']['id']}: {r['case']['query']}",'',
                  'Expected evidence: '+json.dumps(r['case'],sort_keys=True),'',
                  'Actual validated answer:', '```json',json.dumps(r['execution']['response'],indent=2,sort_keys=True),'```','',
                  'Actual retrieved/lookup evidence:']
        for e in r['execution']['events']:
            if e['event']=='tool_executed':
                if e['kind']=='rag':
                    for h in e['result']['hits']:lines.append(f"- `{h['chunk_id']}` parent `{h['document_id']}` cosine {h['cosine_similarity']:.8f}.")
                else:lines.append('- '+json.dumps(e['result'],sort_keys=True))
        lines+=['','Judge result and reproducible calculations:','```json',json.dumps(r['verdict'],indent=2,sort_keys=True),'```']
    lines+=['','## Observed weaknesses','',
            'The unchanged fixed-chunk crew quotes partial/overlapping excerpts. Missing fact groups reduce completeness; lack of expected evidence reduces accuracy. Similarity gating and pattern-based safety do not prove robustness on near-domain or adversarial language. All low scores remain in the 15-case average; no labels, prompts, thresholds or crew behavior were tuned after observing evaluation.','']
    return '\n'.join(lines)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path,default=ROOT/'evidence/milestone_05_evaluation.json')
    args=parser.parse_args();report=evaluate()
    args.report.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    args.report.with_suffix('.md').write_text(markdown(report))
    if NETWORK_ATTEMPTS or FORBIDDEN_PROCESS_ATTEMPTS:raise RuntimeError('Offline evaluation attempted forbidden operation')
    print(json.dumps({'query_count':report['query_count'],'sums':report['metric_sums'],'averages':report['averages'],'offline':report['offline']},indent=2))
