"""Offline clean-index setup using downloaded local model; preserve calibration."""
import argparse
import json
from pathlib import Path
from smoke_tests.runtime import prepare_runtime,install_offline_audit,NETWORK_ATTEMPTS,FORBIDDEN_PROCESS_ATTEMPTS
prepare_runtime();install_offline_audit()
from rag.config import ROOT,DB_DIR
from rag.chunking import load_documents
from rag.core import LocalRAG

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--db-dir',type=Path,default=DB_DIR)
    parser.add_argument('--report',type=Path,default=ROOT/'.runtime/index-rebuild.json');args=parser.parse_args()
    target=args.db_dir.resolve()
    if not target.is_relative_to(ROOT/'.runtime'):raise ValueError('Index storage must be inside project .runtime')
    calibration=json.loads((ROOT/'rag/calibration.json').read_text())
    rag=LocalRAG(load_documents(),db_dir=target)
    if rag.index_fingerprint!=calibration['index_fingerprint']:raise ValueError('Corpus/model changed: recalibration required')
    result={'upserts':rag.upsert_indexes(),'index_fingerprint':rag.index_fingerprint,
            'calibration_preserved':True,'offline':{'network_attempts':NETWORK_ATTEMPTS,'child_process_attempts':FORBIDDEN_PROCESS_ATTEMPTS}}
    for s,c in rag.collections.items():
        assert c.count()==len(rag.chunks[s])
        hits=rag.retrieve('When can a duplicate charge be refunded?',s)
        result.setdefault('sample_hits',{})[s]=hits
        assert hits[0]['document_id']=='04_refund_compensation'
    assert not NETWORK_ATTEMPTS and not FORBIDDEN_PROCESS_ATTEMPTS
    args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':main()
