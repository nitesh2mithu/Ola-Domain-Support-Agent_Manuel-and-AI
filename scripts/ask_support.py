"""Offline text CLI; consecutive query arguments share memory in one process."""
import argparse
import json
from smoke_tests.runtime import (prepare_runtime, install_offline_audit,
                                NETWORK_ATTEMPTS, FORBIDDEN_PROCESS_ATTEMPTS)
prepare_runtime()
install_offline_audit()
from support.session import SupportSession


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('queries',nargs='+')
    parser.add_argument('--session',default='cli-session')
    args=parser.parse_args()
    app=SupportSession()
    turns=[]
    for query in args.queries:
        result=app.ask(query,args.session)
        turns.append({'masked_query':result['masked_query'],'response':result['response'],
                      'history_messages_before':result['history_messages_before'],
                      'kickoff_executed':result['kickoff_executed'],
                      'tool_calls':[{'tool':e['tool'],'arguments':e['arguments']}
                                    for e in result['events'] if e['event']=='tool_executed']})
    if NETWORK_ATTEMPTS or FORBIDDEN_PROCESS_ATTEMPTS:
        raise RuntimeError('Offline execution attempted a prohibited operation')
    print(json.dumps({'turns':turns,'transcript':app.transcript(args.session),
                      'offline':{'network_attempts':NETWORK_ATTEMPTS,
                                 'child_process_attempts':FORBIDDEN_PROCESS_ATTEMPTS}},indent=2,sort_keys=True))


if __name__=='__main__': main()
