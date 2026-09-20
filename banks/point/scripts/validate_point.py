"""Validate paired point accounts and fixed scales against the binary bank."""
import argparse,csv,hashlib,json,math,random,sys
from pathlib import Path
import jsonschema
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(binary,point):
    errors=[];n=0
    def check(ok,msg):
        nonlocal n
        if ok:n+=1
        else:errors.append(msg)
    bs=read(binary/'management/selection.json');ps=read(point/'management/selection.json');schema=read(point/'global/account.schema.json');cfg=read(point/'global/config.json')
    check(random.Random(bs['seed']).sample(bs['eligible_ordered_ids'],bs['actual_n'])==bs['draw_order_ids'],'source random draw replay')
    mapping=lambda x:x.removesuffix('__above_anchor')+'__conditional_mean'
    check(ps['selected_ids']==sorted(mapping(x) for x in bs['selected_ids']),'paired selected IDs')
    check(ps['draw_order_ids']==[mapping(x) for x in bs['draw_order_ids']],'paired original draw order')
    paths=list((point/'accounts').glob('*/account.json'));check(len(paths)==len(bs['selected_ids'])==30,'30 accounts in both formats')
    bc=read(binary/'global/config.json')
    for k in ['time_design','collection_request','series','exceptions_and_records']:
        check(cfg[k]==bc[k],'shared config '+k)
    checks=read(point/'management/eligibility.json');candidates=read(point/'management/candidate_questions.json')
    check(len(candidates)==36 and len(checks)==36*len(cfg['quality_and_eligibility']['required']),'36 candidate complete criteria')
    check(all(x['decision']=='PASS' for x in checks),'all point construction criteria pass')
    check(all(a['normalization']['scale_s']>0 for a in candidates),'all 36 scales positive')
    for p in paths:
        a=read(p);qid=a['question_id'];bpath=binary/'accounts'/a['paired_binary_question_id'];b=read(bpath/'account.json')
        try:jsonschema.validate(a,schema);check(True,qid+' schema')
        except jsonschema.ValidationError as e:check(False,qid+' schema '+e.message)
        for k in ['release_target_id','calendar_package_id','series_cluster_id','series_key','reference_month','time','input_provenance']:
            check(a[k]==b[k],qid+' inherited '+k)
        check(sha(p.parent/'data/history.csv')==sha(bpath/'data/history.csv'),qid+' identical historical CSV')
        check(a['historical_reference']==b['anchor'],qid+' context preserved')
        rs=list(csv.DictReader((p.parent/'data/history.csv').open(encoding='utf-8')));v=[float(r['value']) for r in rs]
        mean=math.fsum(v)/len(v);s=(math.fsum((x-mean)**2 for x in v)/(len(v)-1))**0.5
        check(len(v)==24 and s>0 and math.isclose(s,a['normalization']['scale_s'],rel_tol=1e-12,abs_tol=1e-12),qid+' independent sample SD')
        check(a['normalization']['scale_s']==a['scoring']['normalization_scale'],qid+' scoring scale reference')
        check(a['normalization']['period_start']==rs[0]['period'] and a['normalization']['period_end']==rs[-1]['period'],qid+' scale window')
        check(a['forecast']=={'point_estimate':None,'submitted_at':None,'squared_error':None,'normalized_squared_error':None},qid+' no fabricated forecast/score')
        check(a['resolution']['numeric_outcome'] is None and 'threshold' not in a['resolution'] and 'value_operator' not in a['resolution'],qid+' numeric outcome contract')
        check(a['response_contract']['target_functional']=='conditional_mean' and a['response_contract']['unit']=='percent',qid+' estimand and units')
        check(a['response_contract']['minimum']==(0 if a['dataset']=='une_rt_m' else -100),qid+' support')
        check(all((p.parent/f).is_file() for f in a['materials']),qid+' material references')
    for p in (point/'management/raw').glob('*.provenance.json'):
        m=read(p);file=p.with_name(p.name.removesuffix('.provenance.json'));check(sha(file)==m['sha256'],'raw integrity '+file.name)
    return {'status':'PASS' if not errors else 'FAIL','passed_checks':n,'errors':errors,'paired_accounts':len(paths),'eligible_candidates':len(candidates),'scope':'paired construction, archived data, numeric target definition and fixed normalization; no prospective execution or score results'}
if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');ap=argparse.ArgumentParser();ap.add_argument('--binary',type=Path,required=True);ap.add_argument('--point',type=Path,required=True);a=ap.parse_args();r=validate(a.binary,a.point);print(json.dumps(r,ensure_ascii=False,indent=2));sys.exit(0 if r['status']=='PASS' else 1)
