"""Reproduce evidence, privacy, immutable-input and final-document checks."""
import hashlib
import json
import re
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]


def main():
    load=lambda name:json.loads((ROOT/name).read_text())
    for filename,digest in load('evidence/milestone_05_input_manifest.json').items():
        assert hashlib.sha256((ROOT/filename).read_bytes()).hexdigest()==digest,filename
    for filename,digest in load('evidence/milestone_05_evaluation_freeze.json')['sha256'].items():
        assert hashlib.sha256((ROOT/filename).read_bytes()).hexdigest()==digest,filename
    a=load('evidence/milestone_05_evaluation.json')
    assert a==load('evidence/milestone_05_evaluation_repeat.json')
    cases=a['results'];assert len(cases)==15
    assert {c['case']['topic'] for c in cases if c['case']['kind']=='policy'}=={p.stem for p in (ROOT/'knowledge_base').glob('*.md')}
    assert sum(c['case']['kind']=='out_of_scope' for c in cases)>=2
    for metric in ('Accuracy','Grounding','Completeness','Safety'):
        values=[c['verdict'][metric] for c in cases]
        assert all(0<=v<=1 for v in values)
        assert sum(values)==a['metric_sums'][metric]
        assert a['averages'][metric]==sum(values)/15
    focused=load('evidence/milestone_05_focused.json');assert focused['acceptance']['passed']
    f=focused['judge_fixtures']
    assert f['incorrect_number']['verdict']['Accuracy']<f['correct']['verdict']['Accuracy']
    assert f['unsupported']['verdict']['Grounding']<f['supported']['verdict']['Grounding']
    assert f['incomplete']['verdict']['Completeness']<f['complete']['verdict']['Completeness']
    assert f['unsafe']['verdict']['Safety']==0 and f['safe']['verdict']['Safety']==1
    live=load('evidence/milestone_05_localhost.json');assert live['passed']
    rows=[json.loads(l) for l in (ROOT/'evidence/milestone_05_logs_localhost.jsonl').read_text().splitlines()]
    expected=len(live['http'])+len(live['websocket'])
    assert len(rows)==expected==live['log_check']['logical_requests']
    assert len({r['trace_id'] for r in rows})==expected
    received=[c['response']['trace_id'] for c in live['http']+live['websocket'] if c['response'] is not None]
    assert set(received).issubset({r['trace_id'] for r in rows})
    assert live['disconnect']['during_request'] and live['disconnect']['removed_session'] and live['disconnect']['other_client_continued']
    assert not live['offline']['runtime_external_attempts']
    assert set(live['offline']['negative_controls_blocked'])=={'external_dns','external_ip','other_loopback_port','udp','child_process'}
    docs=['README.md','PROJECT_STATUS.md','DEVELOPMENT_PROCESS.md','ERROR_LOG.md','REQUIREMENTS_TRACKER.md']
    links=0
    for filename in docs:
        assert (ROOT/filename).stat().st_size
        for target in re.findall(r'\]\(([^)]+)\)',(ROOT/filename).read_text()):
            if not target.startswith(('https:','http:','#')):
                assert (ROOT/target.split('#')[0]).is_file(),(filename,target)
                links+=1
    statuses={int(r.split('|')[1]):r.split('|')[-2].strip() for r in (ROOT/'REQUIREMENTS_TRACKER.md').read_text().splitlines() if re.match(r'^\| \d+ \|',r)}
    assert len(statuses)==16 and all(statuses[i]=='PASSED' for i in range(1,14))
    assert statuses[14]=='IN PROGRESS' and statuses[15]==statuses[16]=='NOT STARTED'
    assert 'Status: OPEN' not in (ROOT/'ERROR_LOG.md').read_text()
    assert (ROOT/'PROJECT_STATUS.md').read_text().startswith('# CHATGPT REVIEW HANDOFF')
    artifact_count=0
    for path in (ROOT/'evidence').glob('milestone_05_*'):
        if path.suffix in ('.md','.txt','.json','.jsonl'):
            assert '98765'+'43210' not in path.read_text(),path.name
            artifact_count+=1
    for path in (ROOT/'.runtime/api-tests').glob('*.jsonl'):
        assert '98765'+'43210' not in path.read_text(),path.name
    assert not (ROOT/'.git').exists()
    result={'timestamp':datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),'result':'PASSED',
            'official_and_fixed_inputs_unchanged':True,'frozen_evaluation_inputs_unchanged':True,
            'evaluation_full_reports_identical':True,'query_count':15,'averages':a['averages'],
            'focused_tests':focused['acceptance'],'localhost_logical_requests':expected,
            'exactly_one_jsonl_entry_per_request':True,'disconnect_cleanup_and_survivor':True,
            'runtime_external_attempts':[],'external_negative_controls_blocked':live['offline']['negative_controls_blocked'],
            'sanitized_milestone_artifacts_checked':artifact_count,'evidence_links_checked':links,
            'task_statuses':statuses,'public_repository_created':False}
    (ROOT/'evidence/milestone_05_documentation_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=='__main__':main()
