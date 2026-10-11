"""Run real audited child processes, fail fast, preserve sanitized transcripts.

This orchestration process creates test subprocesses. Inside each child, the
existing offline audit is installed before framework imports and forbids spawning.
--phase localhost requires permission to bind a local listener; no external traffic.
"""
import argparse
from datetime import datetime
from zoneinfo import ZoneInfo
import json
import os
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['offline','localhost'],default='offline');args=parser.parse_args()
    py=str(ROOT/'.venv311/bin/python');env=os.environ.copy();env['CAPSTONE_EVIDENCE_PREFIX']='final'
    jobs=[('dataset',['-m','tests.milestone_02_acceptance','--report','evidence/final_dataset.json']),
          ('dataset_repeat',['-m','tests.milestone_02_acceptance','--report','evidence/final_dataset_repeat.json']),
          ('rag',['-m','tests.milestone_03_acceptance']),
          ('crew',['-m','tests.milestone_04_acceptance','--report','evidence/final_crew.json']),
          ('crew_repeat',['-m','tests.milestone_04_acceptance','--report','evidence/final_crew_repeat.json']),
          ('focused',['-m','tests.milestone_05_focused']),
          ('acceptance',['-m','tests.milestone_06_acceptance']),
          ('framework',['-m','smoke_tests.run_offline']),
          ('evaluation',['-m','scripts.evaluate_support','--report','evidence/final_evaluation.json']),
          ('evaluation_repeat',['-m','scripts.evaluate_support','--report','evidence/final_evaluation_repeat.json'])]
    jobs += [('extra',['-m','scripts.evaluate_extra','--report','evidence/v2_extra_evaluation.json']),
             ('extra_repeat',['-m','scripts.evaluate_extra','--report','evidence/v2_extra_evaluation_repeat.json']),
             ('judge_fixtures',['-m','tests.v2_evaluation'])]
    if args.phase=='localhost':jobs=[('localhost',['-m','tests.milestone_05_localhost'])]
    report={'phase':args.phase,'started':datetime.now(ZoneInfo('Asia/Calcutta')).isoformat(),'jobs':[],'passed':False}
    result_path=ROOT/f'evidence/final_{args.phase}_execution.json'
    for name,argv in jobs:
        # Stream output to an excluded runtime file, then sanitize its complete text.
        temp=ROOT/f'.runtime/final-audit/{name}.txt';temp.parent.mkdir(parents=True,exist_ok=True)
        start=time.perf_counter()
        with temp.open('w') as output:result=subprocess.run([py,*argv],cwd=ROOT,env=env,stdout=output,stderr=subprocess.STDOUT)
        text=temp.read_text().replace(str(ROOT),'<PROJECT_CAPSTONE>').replace(str(Path.home()),'<HOME>')
        text=text.replace('98765'+'43210','[PHONE_MASKED]') # defensive persistence, tests separately detect leaks
        dest=ROOT/f'evidence/final_{name}.txt';dest.write_text(text)
        report['jobs'].append({'name':name,'command':'.venv311/bin/python '+' '.join(argv),
                              'environment':{'CAPSTONE_EVIDENCE_PREFIX':'final'},'exit_code':result.returncode,
                              'duration_seconds':round(time.perf_counter()-start,3),'output':dest.relative_to(ROOT).as_posix()})
        result_path.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
        print(name+': exit '+str(result.returncode),flush=True)
        if result.returncode:raise SystemExit(result.returncode)
    report['passed']=True;report['finished']=datetime.now(ZoneInfo('Asia/Calcutta')).isoformat()
    result_path.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')

if __name__=='__main__':main()
