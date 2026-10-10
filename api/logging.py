"""Single-owner JSONL audit; mask before validation and on final persistence."""
import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from uuid import uuid4
from support.guardrails import PHONE


def generated_id():
    # Preserve UUID entropy without digit runs that resemble phone-number PII.
    return uuid4().hex.translate(str.maketrans('0123456789abcdef','abcdefghijklmnop'))


def sanitize(value):
    if isinstance(value,str): return PHONE.sub('[PHONE_MASKED]',value)
    if isinstance(value,list): return [sanitize(v) for v in value]
    if isinstance(value,dict): return {sanitize(str(k)):sanitize(v) for k,v in value.items()}
    # Invalid numeric fields can contain a fixed-format phone too.
    if isinstance(value,(int,float)) and not isinstance(value,bool):
        rendered=str(value)
        # Do not turn an invalid numeric query/session ID into a valid string.
        if PHONE.search(rendered): return None
    return value


def masked_payload(raw: bytes) -> tuple[bytes,str,bool]:
    """Decode JSON escapes before masking. Never retain malformed body text."""
    try:
        decoded=json.loads(raw.decode('utf-8'))
    except (ValueError,UnicodeError):
        if not raw: return raw,'',False
        return b'!invalid-json!', '[INVALID_JSON_OR_ENCODING]',False
    safe=sanitize(decoded)
    encoded=json.dumps(safe,ensure_ascii=False,separators=(',',':')).encode('utf-8')
    return encoded,encoded.decode('utf-8'),safe!=decoded


class JsonlWriter:
    def __init__(self,path: Path):
        self.path=path
        self.lock=threading.Lock()

    def write(self,entry: dict):
        # Defense at final persistence boundary, including paths/session values.
        encoded=json.dumps(sanitize(entry),ensure_ascii=False,sort_keys=True)+'\n'
        with self.lock:
            self.path.parent.mkdir(parents=True,exist_ok=True)
            with self.path.open('a',encoding='utf-8') as stream:
                stream.write(encoded)


class RequestRecord:
    def __init__(self,transport,route):
        self.trace_id=generated_id()
        self.started=perf_counter()
        self.timestamp=datetime.now(timezone.utc).isoformat()
        self.transport=transport
        self.route=PHONE.sub('[PHONE_MASKED]',route)
        self.masked_request_text=''
        self.phone_masked=False
        self.outcome='internal_error'
        self.status_code=500
        self.crew_executed=False
        self.session_id=None

    def entry(self):
        return {'trace_id':self.trace_id,'timestamp':self.timestamp,'transport':self.transport,
                'route':self.route,'masked_request_text':self.masked_request_text,
                'phone_masked':self.phone_masked,'session_id':self.session_id,
                'duration_ms':round((perf_counter()-self.started)*1000,3),
                'outcome':self.outcome,'status_code':self.status_code,
                'crew_executed':self.crew_executed}


class RequestAuditMiddleware:
    """Pure ASGI middleware owns exactly one entry for each HTTP request.

    WebSocket user-message records are owned by the WebSocket handler, not this
    middleware. No access/error traceback logger sees body text from this layer.
    """
    def __init__(self,app,writer): self.app,self.writer=app,writer

    async def __call__(self,scope,receive,send):
        if scope['type']!='http':
            await self.app(scope,receive,send);return
        record=RequestRecord('http',scope['path'])
        scope.setdefault('state',{})['audit']=record
        started_response=False
        try:
            chunks=[]
            while True:
                message=await receive()
                if message['type']=='http.disconnect':
                    record.outcome='client_disconnected';record.status_code=499;return
                chunks.append(message.get('body',b''))
                if not message.get('more_body',False): break
            safe,text,masked=masked_payload(b''.join(chunks))
            record.masked_request_text=text;record.phone_masked=masked
            scope['headers']=[(k,v) for k,v in scope['headers'] if k.lower()!=b'content-length']+[(b'content-length',str(len(safe)).encode())]
            delivered=False
            async def safe_receive():
                nonlocal delivered
                if not delivered:
                    delivered=True;return {'type':'http.request','body':safe,'more_body':False}
                return await receive()
            async def tracked_send(message):
                nonlocal started_response
                if message['type']=='http.response.start':
                    started_response=True;record.status_code=message['status']
                    if record.outcome=='internal_error' and message['status']<500:
                        record.outcome='http_'+str(message['status'])
                    message['headers']=list(message.get('headers',[]))+[(b'x-trace-id',record.trace_id.encode())]
                await send(message)
            await self.app(scope,safe_receive,tracked_send)
        except Exception:
            # Never interpolate exception strings/tracebacks; they may contain PII.
            record.outcome='internal_error';record.status_code=500
            if not started_response:
                payload=json.dumps({'trace_id':record.trace_id,'error':'internal_error'}).encode()
                await send({'type':'http.response.start','status':500,'headers':[(b'content-type',b'application/json'),(b'x-trace-id',record.trace_id.encode())]})
                await send({'type':'http.response.body','body':payload})
        finally:
            self.writer.write(record.entry())
