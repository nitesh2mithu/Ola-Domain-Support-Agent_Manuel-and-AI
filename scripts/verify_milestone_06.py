"""Historical v1 stage audit; stage-specific assertions remain unchanged.

This cannot certify current v2 inputs. Use scripts.run_final_verification and
scripts.verify_final_acceptance for v2. Rerun output never overwrites the archive.
"""
import hashlib
import json
import re
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from importlib import metadata
ROOT=Path(__file__).resolve().parents[1]

def main():
    load=lambda p:json.loads((ROOT/p).read_text())
    for file,digest in load('evidence/archive/v1/milestone_06_input_manifest.json').items():
        assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==digest,file
    for file,digest in load('evidence/archive/v1/milestone_05_evaluation_freeze.json')['sha256'].items():
        assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==digest,file
    a=load('evidence/archive/v1/milestone_06_acceptance.json');assert a['acceptance']['passed']
    assert a['cases']['approval']['review']['verdict']['approved']
    revision=a['cases']['revision'];assert not revision['review']['verdict']['approved']
    assert revision['review_draft']['answer']!=revision['response']['answer']==revision['draft']['answer']
    assert not a['cases']['http_revision_execution']['review']['verdict']['approved']
    assert a['checks']['permission']['identity_bound'] and a['checks']['permission']['one_use']
    for name in ('oversized','cost_oversized','review_budget_refusal','review_cost_refusal','crew_budget_refusal','cache_budget_preflight'):
        r=a['cases'][name];assert 'budget_exceeded' in r['response']['guardrails']
        assert r['budget']['simulated_tokens']<=r['budget']['token_cap']
        from decimal import Decimal
        assert Decimal(r['budget']['simulated_cost_usd'])<=Decimal(r['budget']['cost_cap_usd'])
    c=a['checks']['cache'];assert c['hit']['rag_tools']==0 and c['miss']['rag_tools']==1
    assert c['hit']['crew_model_calls']<c['miss']['crew_model_calls'] and c['hit']['review_calls']==2
    assert a['cases']['session_b']['response']['ticket']['record_id']=='OLA-0004'
    assert a['cases']['fresh_isolation']['response']['ticket'] is None
    assert 'stale_evidence' in a['cases']['stale_evidence']['response']['guardrails']
    e=load('evidence/archive/v1/milestone_06_evaluation.json');assert e==load('evidence/archive/v1/milestone_06_evaluation_repeat.json')
    assert e['query_count']==15 and len(e['results'])==15
    for r in e['results']:assert r['execution']['review']['model_calls']==[1,1]
    for m in e['averages']:
        assert e['metric_sums'][m]==sum(r['verdict'][m] for r in e['results'])
        assert e['averages'][m]==e['metric_sums'][m]/15
    assert e['averages']==load('evidence/archive/v1/milestone_05_evaluation.json')['averages']
    f=load('evidence/archive/v1/milestone_06_focused.json');assert f['acceptance']['passed']
    fixtures=f['judge_fixtures']
    for bad,good,metric in [('incorrect_number','correct','Accuracy'),('unsupported','supported','Grounding'),('incomplete','complete','Completeness'),('unsafe','safe','Safety')]:
        assert fixtures[bad]['verdict'][metric]<fixtures[good]['verdict'][metric]
    live=load('evidence/archive/v1/milestone_06_localhost.json');assert live['passed']
    rows=[json.loads(l) for l in (ROOT/'evidence/archive/v1/milestone_06_logs_localhost.jsonl').read_text().splitlines()]
    assert len(rows)==len(live['http'])+len(live['websocket'])==29
    assert len({r['trace_id'] for r in rows})==29
    assert live['disconnect']['during_request'] and live['disconnect']['removed_session'] and live['disconnect']['other_client_continued']
    assert not live['offline']['runtime_external_attempts']
    assert set(live['offline']['negative_controls_blocked'])=={'external_dns','external_ip','other_loopback_port','child_process','udp'}
    assert not a['checks']['offline']['network_attempts'] and not e['offline']['network_attempts']
    for name in ['crew','focused']:
        assert load('evidence/archive/v1/milestone_06_'+name+'.json')['acceptance']['passed']
    # Confirm all final executed suites, rather than inferring a pass from code.
    for name,count in [('dataset',8),('prerequisite_rag',8),('crew',12),('focused',11),('framework',6),('acceptance',6)]:
        text=(ROOT/f'evidence/archive/v1/milestone_06_{name}.txt').read_text()
        assert f'Ran {count} tests' in text and '\nOK\n' in text,(name,count)
    links=0
    docs=['README.md','docs/PROJECT_STATUS.md','docs/DEVELOPMENT_PROCESS.md','docs/ERROR_LOG.md','docs/REQUIREMENTS_TRACKER.md']
    for file in docs:
        text=(ROOT/file).read_text();assert text.strip()
        for target in re.findall(r'\]\(([^)]+)\)',text):
            if not target.startswith(('http:','https:','#')):
                resolved = ((ROOT/file).parent/target.split('#')[0]).resolve()
                assert resolved.is_relative_to(ROOT) and (resolved.is_file() or resolved.is_dir()),(file,target)
                links+=1
    statuses={int(r.split('|')[1]):r.split('|')[-2].strip() for r in (ROOT/'docs/REQUIREMENTS_TRACKER.md').read_text().splitlines() if re.match(r'^\| \d+ \|',r)}
    assert len(statuses)==16 and all(s=='PASSED' for s in statuses.values())
    assert 'Status: OPEN' not in (ROOT/'docs/ERROR_LOG.md').read_text()
    assert (ROOT/'docs/PROJECT_STATUS.md').read_text().startswith('# REVIEW NOTES')
    for path in list((ROOT/'evidence').glob('milestone_06_*'))+list((ROOT/'.runtime/api-tests').glob('*.jsonl')):
        if path.suffix in {'.json','.jsonl','.md','.txt'}:assert '98765'+'43210' not in path.read_text(),path.name
    assert not (ROOT/'.git').exists()
    pins={line.split('==')[0]:line.split('==')[1] for line in (ROOT/'requirements-api.lock').read_text().splitlines() if '==' in line}
    for name,version in pins.items():assert metadata.version(name)==version,(name,version)
    result={'timestamp':datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),'result':'PASSED',
        'scope':'Milestone6 Tasks14–16 and relevant regression; not a complete final submission audit',
        'protected_inputs_unchanged':True,'frozen_evaluation_inputs_unchanged':True,
        'acceptance':a['acceptance'],'framework_regression':6,'dataset_policy_regression':8,'rag_regression':8,
        'crew_regression':12,'focused_api_judge_regression':11,'real_localhost_requests_and_logs':29,
        'approval_and_revision_through_application_and_http':True,'boundary_rejections':True,
        'combined_token_cost_caps_verified':True,'cache':c,'all_task_statuses':statuses,
        'evaluation_reports_identical':True,'averages':e['averages'],'averages_changed':False,
        'evidence_links_checked':links,'dependency_pins_unchanged':len(pins),'external_runtime_attempts':[],
        'public_repository_created':False,'final_submission_readiness_claimed':False}
    destination = ROOT/'.runtime/historical-audits/milestone_06_documentation_audit.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True,indent=2))

if __name__=='__main__':main()
