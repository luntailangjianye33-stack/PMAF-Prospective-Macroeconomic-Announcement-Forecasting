from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, sys, requests
ROOT=Path(__file__).resolve().parent
RAW=ROOT/'raw'; RAW.mkdir(exist_ok=True)
def fetch(name,url,params=None):
    start=datetime.now(timezone.utc).isoformat()
    r=requests.get(url,params=params,timeout=60)
    out=RAW/name; out.write_bytes(r.content)
    meta={'url':r.url,'requested_at':start,'retrieved_at':datetime.now(timezone.utc).isoformat(),'status':r.status_code,'content_type':r.headers.get('Content-Type'),'sha256':hashlib.sha256(r.content).hexdigest(),'bytes':len(r.content),'response_date':r.headers.get('Date')}
    (RAW/(name+'.provenance.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    print(name,r.status_code,len(r.content),flush=True)
    r.raise_for_status()
    return r
if __name__=='__main__':
    r=fetch('calendar_q4.json','https://ec.europa.eu/eurostat/o/calendars/eventsJson',{'start':'2026-10-01T00:00:00+02:00','end':'2027-01-01T00:00:00+01:00','theme':0,'category':0,'keywords':'','isEuroindicator':'true','authorInclude':'','authorExclude':''})
    d=r.json(); print(json.dumps(d,ensure_ascii=False)[:12000])
