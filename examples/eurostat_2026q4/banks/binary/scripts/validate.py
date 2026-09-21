"""Validate a constructed bank, without fetching or predicting outcomes."""
import argparse, csv, hashlib, itertools, json, math, random, sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from decimal import Decimal
import jsonschema

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(root):
    errors=[];passed=0
    def check(ok,name):
        nonlocal passed
        if ok:passed+=1
        else:errors.append(name)
    cfg=read(root/'global/config.json');sel=read(root/'management/selection.json')
    accounts=sorted((root/'accounts').glob('*/account.json'))
    check(len(accounts)==sel['actual_n']==min(cfg['selection']['target_n'],len(sel['eligible_ordered_ids'])),'N and declared shortfall')
    check(len(set(sel['selected_ids']))==len(accounts),'unique sampled accounts')
    check(sel['eligible_ordered_ids']==sorted(sel['eligible_ordered_ids']),'frame ordering')
    expected=random.Random(sel['seed']).sample(sel['eligible_ordered_ids'],sel['actual_n'])
    check(expected==sel['draw_order_ids'],'seeded draw replay')
    check(hashlib.sha256(('\n'.join(sel['eligible_ordered_ids'])+'\n').encode()).hexdigest()==sel['eligible_frame_sha256'],'frame hash')
    check(sorted(p.parent.name for p in accounts)==sel['selected_ids'],'directory/selection identity')
    criteria=read(root/'management/eligibility.json');byid={}
    for c in criteria:byid.setdefault(c['question_id'],[]).append(c)
    check(all(len(v)==len(cfg['quality_and_eligibility']['required']) for v in byid.values()),'all mandatory checks recorded')
    raw=root/'management/raw';source_status=Counter()
    for p in raw.glob('*.provenance.json'):
        m=read(p);q=p.with_name(p.name.removesuffix('.provenance.json'))
        check(q.is_file() and sha(q)==m['sha256'] and q.stat().st_size==m['bytes'],'raw integrity '+p.name)
        source_status[str(m['status'])]+=1
    schema=read(root/'global/account.schema.json')
    calendar=read(raw/'calendar_q4.json');calendar_ids={e['recordid']:e for e in calendar}
    for p in accounts:
        a=read(p);qid=a['question_id']
        try:jsonschema.validate(a,schema);check(True,'schema')
        except jsonschema.ValidationError as e:check(False,qid+' schema '+e.message)
        check(all(x['decision']=='PASS' for x in byid[qid]),qid+' eligibility')
        check(a['calendar_package_id'] in calendar_ids,qid+' source package')
        tt={k:datetime.fromisoformat(a['time'][k]) for k in ['scheduled_release_utc','scheduled_release_local','presentation_utc','submission_deadline_utc','resolution_deadline_utc']}
        R=tt['scheduled_release_utc'];T=tt['presentation_utc'];C=tt['submission_deadline_utc']
        check(R==tt['scheduled_release_local'],qid+' timezone conversion')
        check(R-T==timedelta(hours=cfg['time_design']['H_hours']) and C-T==timedelta(hours=cfg['time_design']['D_hours']) and T<C<R,qid+' timing durations')
        check(datetime.fromisoformat(cfg['time_design']['experiment_start_utc'])<=T and tt['resolution_deadline_utc']<=datetime.fromisoformat(cfg['time_design']['experiment_end_utc']),qid+' experiment boundaries')
        check(datetime.fromisoformat(a['input_provenance']['retrieved_at'])<T,qid+' input predates presentation')
        rows=list(csv.DictReader((p.parent/'data/history.csv').open(encoding='utf-8')))
        check(len(rows)==24 and len(set(r['period'] for r in rows))==24,qid+' history length uniqueness')
        check(rows[-1]['period']==a['anchor']['period'] and Decimal(rows[-1]['value'])==Decimal(str(a['anchor']['value']))==Decimal(str(a['resolution']['threshold'])),qid+' threshold history equality')
        check(all(r['period']<a['reference_month'] for r in rows),qid+' historic reference bounds')
        # Independent decoding by Cartesian position enumeration, rather than build.py stride lookup.
        j=read(root/a['input_provenance']['history_file']);cats=[]
        for d in j['id']:
            cats.append([k for k,v in sorted(j['dimension'][d]['category']['index'].items(),key=lambda x:x[1])])
        found={}
        for i,keys in enumerate(itertools.product(*cats)):
            dims=dict(zip(j['id'],keys));v=j['value'].get(str(i))
            if all(dims[k]==v2 for k,v2 in a['series_key'].items()) and v is not None:found[dims['time']]=v
        check(all(r['period'] in found and Decimal(r['value'])==Decimal(str(found[r['period']])) for r in rows),qid+' independent source value reconstruction')
        check(a['reference_month'] not in found,qid+' target numeric value absent in input snapshot')
        check(a['anchor']['period']==max(found),qid+' latest nonmissing frozen anchor')
        check(a['forecast']=={'p_yes':None,'score':None,'submitted_at':None} and a['resolution']['outcome'] is None,qid+' no fabricated forecast outcome score')
        check(all((p.parent/f).is_file() for f in a['materials']),qid+' permitted material references')
        check((p.parent/a['global_rules']).resolve()==(root/'global/global_rules.md').resolve(),qid+' global rules outside account')
        check(a['resolution']['equal_means']=='NO' and a['resolution']['value_operator']=='>',qid+' binary boundary')
    result={'status':'PASS' if not errors else 'FAIL','passed_checks':passed,'errors':errors,'raw_retrieval_status_counts':dict(source_status),'account_count':len(accounts),'scope':'construction and archived data integrity; does not validate actual future release times, execution controls or forecasting performance'}
    return result

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    ap=argparse.ArgumentParser();ap.add_argument('bank',type=Path);a=ap.parse_args();result=validate(a.bank)
    print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(0 if result['status']=='PASS' else 1)
