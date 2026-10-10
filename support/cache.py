"""Only policy grounded-generation artifacts; never complete/session responses."""
import copy
import hashlib
import json
from pathlib import Path
from threading import RLock
from rag.config import ROOT
from rag.chunking import load_documents

class StaleEvidence(ValueError):
    pass

class PolicyCache:
    def __init__(self, enabled=True):
        self.enabled=enabled
        self.entries={}
        self.hits=self.misses=0
        self.lock=RLock()

    @staticmethod
    def normalize(query):
        return ' '.join(query.casefold().split())

    def key(self,query,rag,calibration):
        # Read live policy bytes, as well as evaluated index/config/model identity.
        if load_documents()!=rag.documents:
            raise StaleEvidence("Policies changed: rebuild and recalibrate index before answering")
        corpus={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'knowledge_base').glob('*.md'))}
        identity={'corpus':corpus,'index':rag.index_fingerprint,'calibration':calibration,
                  'renderer':'grounded_answer-v1','model':'all-MiniLM-L6-v2'}
        fingerprint=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
        return (self.normalize(query),fingerprint)

    def get(self,key):
        with self.lock:
            if not self.enabled:return None
            if key in self.entries:
                self.hits+=1
                return copy.deepcopy(self.entries[key])
            self.misses+=1
            return None

    def put(self,key,result):
        if not self.enabled:return
        # Only policy schema. Prevent accidental storage of whole session/ticket output.
        if set(result)!={'answer','citations','excerpts','fallback','hits','threshold','strategy','collection'}:
            raise ValueError('Cache accepts only grounded policy results')
        with self.lock:self.entries[key]=copy.deepcopy(result)

    def invalidate(self):
        with self.lock:self.entries.clear()

    def counters(self):
        return {'hits':self.hits,'misses':self.misses,'entries':len(self.entries),'enabled':self.enabled}
