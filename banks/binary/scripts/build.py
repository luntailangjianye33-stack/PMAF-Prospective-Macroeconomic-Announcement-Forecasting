"""Offline deterministic construction from archived Eurostat responses.
Run: python build.py --inputs INPUT_DIRECTORY --out NEW_OUTPUT_DIRECTORY
Inputs: config.json and raw/. No network; never overwrites an existing output.
"""
import argparse, csv, hashlib, io, json, math, platform, random, re, shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

VERSION='1.0'
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def digest(b): return hashlib.sha256(b).hexdigest()
def write(p,s):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def dump(p,j):write(p,json.dumps(j,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def csvwrite(p,rows,fields):
    f=io.StringIO(newline='');w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows);write(p,f.getvalue())
def month(s):
    names=['January','February','March','April','May','June','July','August','September','October','November','December']
    m=re.match(r'([A-Za-z]+)\s+(\d{4})',s)
    if not m: raise ValueError(f'Unknown reference month: {s}')
    n='September' if m[1]=='Sept' else m[1]
    return f'{m[2]}-{names.index(n)+1:02d}'
def monthnum(s):y,m=map(int,s.split('-'));return 12*y+m
def records(j,filters,geo):
    assert len(j['id'])==len(j['size']) and len(set(j['id']))==len(j['id'])
    for d,v in {**filters,'geo':geo}.items():assert v in j['dimension'][d]['category']['index'],(d,v)
    out=[]
    for t in sorted(j['dimension']['time']['category']['index']):
        ix=0
        for d,size in zip(j['id'],j['size']):
            key=t if d=='time' else (geo if d=='geo' else filters[d])
            ix=ix*size+j['dimension'][d]['category']['index'][key]
        v=j.get('value',{}).get(str(ix)); flag=j.get('status',{}).get(str(ix),'')
        if v is not None:
            assert isinstance(v,(int,float)) and math.isfinite(v)
            out.append({'period':t,'value':v,'status_flag':flag})
    return out

def build(inp,out):
    if out.exists():raise ValueError('Output already exists: use a new output directory.')
    config=read(inp/'config.json');raw=inp/'raw';out.mkdir(parents=True)
    shutil.copytree(raw,out/'management'/'raw')
    dump(out/'global'/'config.json',config)
    write(out/'scripts'/'build.py',Path(__file__).read_text(encoding='utf-8'))
    t=config['time_design'];H=timedelta(hours=t['H_hours']);D=timedelta(hours=t['D_hours']);b=timedelta(hours=t['resolution_buffer_hours'])
    tz=ZoneInfo(t['timezone']);t0=datetime.fromisoformat(t['experiment_start_utc']);t1=datetime.fromisoformat(t['experiment_end_utc'])
    assert timedelta(0)<D<H
    sources=read(raw/'calendar_q4.json');cm=read(raw/'calendar_q4.json.provenance.json')
    assert cm['status']==200 and digest((raw/'calendar_q4.json').read_bytes())==cm['sha256']
    titlemap={v['calendar_title']:k for k,v in config['series'].items()}
    pool=[];ledger=[];packages=[];histories={};checks=[]
    for event in sources:
        code=titlemap.get(event['title']);inside=(code is not None and event['euroindAuthor']=='estat' and code in event['datasetCodes'].split(','))
        packages.append({'package_id':event['recordid'],'title':event['title'],'raw_start':event['start'],'raw_period':event['period'],'scope_status':'IN_SCOPE' if inside else 'OUT_OF_SCOPE','reason':'declared exact title, publisher and dataset' if inside else 'outside declared six monthly indicator domains'})
        if not inside:continue
        spec=config['series'][code];j=read(raw/spec['raw_history']);jm=read(raw/(spec['raw_history']+'.provenance.json'))
        assert jm['status']==200 and digest((raw/spec['raw_history']).read_bytes())==jm['sha256']
        ref=month(event['period']);date=event['start'][:10]
        Rlocal=datetime.fromisoformat(date+'T'+t['release_local_time_assumption']).replace(tzinfo=tz)
        R=Rlocal.astimezone(timezone.utc);T=R-H;C=T+D
        for geo in config['collection_request']['geographies']:
            qid=f'{code}__{geo}__{ref}__first__above_anchor'
            rs=records(j,spec['filters'],geo);hist=rs[-24:];anchor=hist[-1] if hist else None
            histories[qid]=hist
            before=all(datetime.fromisoformat(m['retrieved_at'])<T for m in [cm,jm])
            consecutive=len(hist)==24 and all(monthnum(y['period'])-monthnum(x['period'])==1 for x,y in zip(hist,hist[1:]))
            v={
             'source_scope':(True,f'calendar package {event["recordid"]}; publisher estat; dataset {code}'),
             'series_identity':(all(k in j['id'] for k in spec['filters']),json.dumps({**spec['filters'],'geo':geo},ensure_ascii=False)),
             'planned_time_feasible':(t['release_date_start']<=date<=t['release_date_end'] and t0<=T and R+b<=t1 and C<R,'Policy-derived tentative 11:00 Europe/Luxembourg; assumption explicitly admitted by config; execution requires schedule confirmation'),
             'future_target_plan':(not any(x['period']==ref for x in rs) and before,'Target month has no numeric value in archived selected series; snapshot precedes planned presentation; actual submission-time unpublished status is not yet tested'),
             'anchor_and_history':(consecutive and anchor is not None and anchor['period']<ref,f'24 consecutive months; anchor {anchor}; fixed construction snapshot'),
             'resolution_defined':(bool(config['resolution_and_scoring']['source_locator']),f'First official release table for {code}, {geo}, {ref}; not yet retrieved'),
             'unique_id':(not any(a['question_id']==qid for a in pool),'series/geography/reference-month/first-publication/template key; date not part of identity')}
            status='PASS' if all(x[0] for x in v.values()) else 'FAIL'
            for criterion,(passed,evidence) in v.items():
                checks.append({'question_id':qid,'criterion_id':criterion,'criterion_version':'1.0','stage':'candidate_eligibility','applicability':'required','decision':'PASS' if passed else 'FAIL','evidence':evidence,'sources':[f'management/raw/{spec["raw_history"]}','management/raw/calendar_q4.json','global/config.json'],'reviewer_or_tool_version':'build.py '+VERSION,'checked_against_configuration_at':config['identity']['configured_at_utc']})
            geoja='EU27か国全体' if geo=='EU27_2020' else 'ユーロ圏21か国'
            a={'question_id':qid,'account_version':'1.0','release_target_id':f'{code}__{geo}__{ref}__first','calendar_package_id':event['recordid'],'series_cluster_id':f'{code}__{geo}','publisher':'Eurostat','dataset':code,'series_key':{**spec['filters'],'geo':geo},'reference_month':ref,'geography_label':j['dimension']['geo']['category']['label'][geo],'indicator_label_ja':spec['label_ja'],'unit_description':spec['unit_description'],'anchor':anchor,
              'question_ja':f'{geoja}について、{ref}を対象とする{spec["label_ja"]}の初回公表値は、保存済みの{anchor["period"]}の値（{anchor["value"]} %）を厳密に上回るか。YESの確率を0以上1以下で提出せよ。' if anchor else 'UNVERIFIED: no anchor',
              'question_en':f'For {j["dimension"]["geo"]["category"]["label"][geo]}, will the first published {ref} value of {event["title"]}, for the exact series key specified here, be strictly greater than the frozen {anchor["period"]} value of {anchor["value"]} percent? Submit P(YES) in [0,1].' if anchor else 'UNVERIFIED: no anchor',
              'time':{'scheduled_release_local':Rlocal.isoformat(),'scheduled_release_utc':R.isoformat(),'presentation_utc':T.isoformat(),'submission_deadline_utc':C.isoformat(),'resolution_deadline_utc':(R+b).isoformat(),'schedule_status':'POLICY_DERIVED_TENTATIVE','raw_calendar_start':event['start'],'raw_calendar_allDay':event['allDay'],'time_evidence':['management/raw/protocol_access.html','management/raw/calendar_ui.html'],'time_interpretation':t['release_time_basis']},
              'input_provenance':{'history_file':f'management/raw/{spec["raw_history"]}','history_url':jm['url'],'history_sha256':jm['sha256'],'retrieved_at':jm['retrieved_at'],'dataset_updated':j.get('updated'),'calendar_snapshot_sha256':cm['sha256']},
              'resolution':{'source_title':event['title'],'reference_month':ref,'value_operator':'>','threshold':anchor['value'] if anchor else None,'equal_means':'NO','vintage':'first official publication of target numeric value','source_entrypoint':config['resolution_and_scoring']['entrypoint'],'source_locator':config['resolution_and_scoring']['source_locator'],'future_document_url':None,'observed_value':None,'outcome':None,'status':'NOT_YET_RELEASED'},
              'forecast':{'p_yes':None,'submitted_at':None,'score':None},'eligibility_status':status,'global_rules':'../../global/global_rules.md','local_rules':'local_rules.md','materials':['question.md','account.json','data/history.csv','materials.md'],'execution_gate':'Reconfirm official schedule, detect early publication and enforce access rules before actual use.'}
            pool.append(a)
            ledger.append({'question_id':qid,'package_id':event['recordid'],'dataset':code,'geo':geo,'reference_month':ref,'scheduled_release_local':Rlocal.isoformat(),'status':status,'failed_criteria':';'.join(k for k,x in v.items() if not x[0]),'anchor_month':anchor['period'] if anchor else '', 'anchor_value':anchor['value'] if anchor else ''})
    eligible=sorted(a['question_id'] for a in pool if a['eligibility_status']=='PASS')
    n=min(config['selection']['target_n'],len(eligible));draw=random.Random(config['selection']['seed']).sample(eligible,n)
    selection={'eligible_ordered_ids':eligible,'draw_order_ids':draw,'selected_ids':sorted(draw),'requested_n':config['selection']['target_n'],'actual_n':n,'seed':config['selection']['seed'],'algorithm':config['selection']['implementation'],'python_version':platform.python_version(),'eligible_frame_sha256':digest(('\n'.join(eligible)+'\n').encode()),'replacement':False}
    dump(out/'management'/'selection.json',selection);dump(out/'management'/'eligibility.json',checks)
    dump(out/'management'/'candidate_questions.json',sorted(pool,key=lambda a:a['question_id']))
    for row in ledger:row['selected']=row['question_id'] in draw
    csvwrite(out/'management'/'candidates.csv',ledger,list(ledger[0]));csvwrite(out/'management'/'calendar_dispositions.csv',packages,list(packages[0]))
    shared='''# 共通実行規約 / Global execution rules

本QBは構築例であり、予測主体の実行・採点は未実施である。設定の正本はconfig.json。各口座の問い本文、系列キー、比較値、時刻はaccount.jsonと対応する。

## 提示・情報条件

同一口座の全主体へ、予定公表時刻の336時間前に同じ資料を提示し、2時間以内に回答を収集する。異なる口座の提示日は各公表予定に従う。UTCの経過時間で計算し、夏時間の切替を反映する。

提供するのは当該口座のmaterials一覧と、この共通規約のみ。management以下の構築用ファイルと他口座は配布しない。回答中はネットワークを無効化し、提供ファイルとローカル計算ツールだけを許可する。予測市場、その転載値・検索要約・市場由来データの取得は禁止。既存の記憶やモデルの学習済み知識の除去は保証しない。主体・モデル版、ツール、閲覧・計算、提示・提出時刻を記録する。

## 確率と正解

p_yesは有限の数値で0以上1以下。数値上昇の問いでは公表値が固定比較値を厳密に上回る場合のみYES（1）、同値または下回る場合NO（0）。失業率上昇は経済改善を意味しない。前月比を問う系列では前月比という数値の増減を問うため、活動水準自体の増減と区別する。

対象は指定参照月・指定地域・指定系列の初回公式公表値。実施者は該当Eurostatニュース公表の表・本文を発表時に保存し、URL、取得日時、ハッシュ、抽出箇所、値を記録する。公表済み桁数の十進数で比較する。後の改定値で置換しない。採点は(p_yes−y)^2、主体・条件ごとに有効な解決済み問の単純平均を計算する。未解決はnullとし、0点やNOに変換しない。提出率・有効率・解決率・除外件数を併記する。

## 予定と例外

公表日程は取得時点の予定。時刻は公式11 am CET方針をEurope/Luxembourgの現地時刻として適用した計画値であり、カレンダーAPIのallDayイベントに含まれる11:00Zを検証済みUTC時刻として採用していない。実施前に公式予定と時刻を再確認する。予定の変更・時刻根拠の不一致があれば元版を保存し、提示前に別版へ移すか当該口座を除外する。無断でT、C、Rを書き換えない。

提出前に対象値が公表されていれば汚染として除外。遅延回答・閲覧違反も記録付きで無効。R+24時間までに指定初回版の証拠が得られなければ未解決。現在APIの最新版を代用して初回値と見なさない。除外・未解決後の構成を報告し、この版での事後補充は行わない。

## English operational specification

For each account, all subjects receive identical permitted files at R−336 elapsed hours and submit within 2 hours. Network access is disabled; only supplied materials and logged local computations are allowed. Prediction markets and derivatives or republications of their probabilities are prohibited. Prior memory and pretrained knowledge are not erased. Present only the assigned account and these global rules; management files and other accounts are not participant inputs.

Submit a finite p_yes in [0,1]. YES means the specified first published value is strictly greater than its frozen historical threshold; ties are NO. Compare published decimal values. Archive the first official release document and its provenance; later revisions do not replace the target vintage. The primary loss is (p_yes−y)^2, averaged equally across valid resolved records for each subject/condition. Unresolved values remain null. Report submission, validity and resolution counts separately.

Schedules are tentative policy-derived plans: 11 am Luxembourg civil time, with elapsed UTC durations. Reconfirm before execution. Preserve changes in a separate version or exclude affected accounts. Reject contaminated, late or access-violating responses with evidence. Missing first-publication evidence by R+24 hours produces an unresolved record. Do not silently substitute latest API data or refill excluded questions.
'''
    write(out/'global'/'global_rules.md',shared)
    for a in pool:
        if a['question_id'] not in draw:continue
        p=out/'accounts'/a['question_id'];dump(p/'account.json',a)
        csvwrite(p/'data'/'history.csv',histories[a['question_id']],['period','value','status_flag'])
        write(p/'question.md',f'# {a["question_id"]}\n\n{a["question_ja"]}\n\n{a["question_en"]}\n\n系列キー：`{json.dumps(a["series_key"],ensure_ascii=False)}`\n\n- 提示：{a["time"]["presentation_utc"]}\n- 提出締切：{a["time"]["submission_deadline_utc"]}\n- 公表予定：{a["time"]["scheduled_release_local"]}（暫定計画値）\n\n[共通規約](../../global/global_rules.md)・[個別規約](local_rules.md)\n')
        write(p/'local_rules.md',f'# 個別規約\n\n共通規約を適用する。対象月は{a["reference_month"]}、対象系列はaccount.jsonのseries_keyで特定する。初回公表値を固定比較値 {a["anchor"]["value"]} % と比較し、同値はNO。比較値の参照月は{a["anchor"]["period"]}。後日改定・更新しない。\n\nPermitted inputs and outcome rule are fixed in account.json and global_rules.md. The numerical threshold remains unchanged after later revisions.\n')
        write(p/'materials.md',f'# 提供資料\n\n過去24か月の同一系列・同一地域の数値をdata/history.csvへ格納した。取得日時：{a["input_provenance"]["retrieved_at"]}。公表済みデータの構築時点の保存版であり、各過去月の初回公表値を再構成したものではない。\n\n単位：{a["unit_description"]}。系列条件：`{json.dumps(a["series_key"],ensure_ascii=False)}`。元表：{a["dataset"]}。欠測を補間せず、公表元のstatus_flagを保持する。データ取得URLはaccount.jsonに記録する。試験中はURLへアクセスせず保存資料を参照する。\n\nThe supplied history is a construction-time snapshot of the latest available vintage, not a reconstruction of each historical first release. Values, units, adjustment and geography follow the specified series key. Source flags are retained; no imputation is performed.\n')
    summary={'raw_calendar_packages':len(sources),'in_scope_packages':sum(x['scope_status']=='IN_SCOPE' for x in packages),'out_of_scope_packages':sum(x['scope_status']=='OUT_OF_SCOPE' for x in packages),'release_targets':len(pool),'candidate_questions':len(pool),'eligible_questions':len(eligible),'failed_questions':sum(a['eligibility_status']=='FAIL' for a in pool),'selected_accounts':n,'selected_release_packages':len(set(a['calendar_package_id'] for a in pool if a['question_id'] in draw)),'history_rows':24*n,'forecast_runs':0,'resolved_outcomes':0,'scores':0,'schedule_status':'tentative policy-derived; actual execution verification pending','configuration_phase':'after documented exploratory source discovery; before screening and sampling','per_indicator':{k:sum(a['dataset']==k and a['question_id'] in draw for a in pool) for k in config['series']},'per_geo':{g:sum(a['series_key']['geo']==g and a['question_id'] in draw for a in pool) for g in config['collection_request']['geographies']}}
    dump(out/'management'/'construction_summary.json',summary)
    schema={'$schema':'https://json-schema.org/draft/2020-12/schema','title':'PMAF demonstration question account v1','type':'object','required':['question_id','account_version','release_target_id','calendar_package_id','series_key','reference_month','anchor','time','resolution','global_rules','materials'],'properties':{'question_id':{'type':'string','minLength':1},'series_key':{'type':'object','required':['freq','unit','geo']},'reference_month':{'type':'string','pattern':'^20[0-9]{2}-(0[1-9]|1[0-2])$'},'anchor':{'type':'object','required':['period','value'],'properties':{'value':{'type':'number'}}},'eligibility_status':{'const':'PASS'},'forecast':{'type':'object','properties':{'p_yes':{'type':['number','null'],'minimum':0,'maximum':1}}}}}
    dump(out/'global'/'account.schema.json',schema)
    rows=['| 問い | 公表予定（現地時刻） | 比較月 | 比較値 (%) |','|---|---|---|---:|']
    for a in sorted((a for a in pool if a['question_id'] in draw),key=lambda a:(a['time']['scheduled_release_local'],a['question_id'])):
        rows.append(f'| [{a["question_id"]}](accounts/{a["question_id"]}/question.md) | {a["time"]["scheduled_release_local"]} | {a["anchor"]["period"]} | {a["anchor"]["value"]} |')
    write(out/'README.md',f'''# PMAF：EU関連統計のQuestionBank構築例（2026年Q4）

二値確率予測用の{n}口座を構築した。公式カレンダーの{len(sources)}公表パッケージから、設定した6統計に対応する{summary['in_scope_packages']}パッケージを取り出し、EU27全体・ユーロ圏21か国へ展開した{len(pool)}問いを審査した。適格な{len(eligible)}問いから、乱数シード20260912による単純無作為・非復元抽出で{n}問いを選定した。層別配分は行っていない。

## 設定と成果物

- 公表予定の対象期間：2026-10-01〜2026-12-31。参照月は口座ごとに異なる。
- 実験期間の設定：2026-09-15〜2027-01-02（UTC）。今回は構築と保存入力からの再生成を実施する。
- 同一口座の各主体へ公表予定の14日前に提示、回答時間2時間、結果取得期限は予定公表の24時間後。
- 予測市場の閲覧禁止。未指定の情報条件には「提供資料とローカル計算のみ、回答中ネット無効」を採用した。
- 比較値は構築時点の保存データから取得した直近の公表済み値。予測実施直前の前月値へ更新しない。過去24か月の同一系列データを各口座へ添付した。
- 正解は指定月の初回公式公表値。主要指標は平均Brier score。実行・解決・採点はすべて0件。

設定の選択理由・取得後に設定した経緯・探索段階のクエリ修正は[config.json](global/config.json)のconfiguration_historyに記録した。30件・無作為抽出・二値確率・予測市場禁止はユーザー指定。地域集計、6統計、時間幅、履歴長、閉鎖資料方式は今回の例示用に補完した設定である。

```text
QuestionBank/
├── accounts/                 問い口座×{n}
│   └── <question_id>/
│       ├── account.json      問い・閾値・系列・時間・結果判定
│       ├── question.md       日英の問い本文
│       ├── data/history.csv  公表済み24か月分
│       ├── materials.md     入力データの意味と版
│       └── local_rules.md    個別規約
├── global/                   共通規約・設定・口座の型定義
├── management/               原資料・来歴・全候補・審査・抽出記録
└── scripts/                  保存入力による再構築・検証
```

## 構築の検証範囲

対象は指定Eurostatカレンダーから取得できた6系列・2集計地域。EU域内の全経済統計、加盟各国統計、全経済部門の網羅を意味しない。{n}口座は{summary['selected_release_packages']}公表パッケージに対応し、EUとユーロ圏の重なりや同一系列の繰返しがある。独立した{n}標本という仮定は置かない。

時刻は公式の11 am CET方針とカレンダー画面のEurope/Luxembourg設定に基づく計画上の解釈。APIではallDay=trueのイベントに11:00Zが含まれており、これを実公表UTC時刻の確認証拠として用いていない。暫定予定を許容する構築条件で審査し、実施時の予定確認は別途必要とした。延期・前倒し・時刻根拠の不一致は版管理・除外規約に従う。将来の実公表時刻や期間内の解決成功はまだ検証していない。

入力のAPI値は構築時点の公表済み保存版。正解には将来の初回公表文書を別途保存する。今回の凍結証拠はローカルのSHA-256と日時であり、第三者タイムスタンプや事前登録は未取得。

## 記録

- [全候補と採否](management/candidates.csv)
- [審査証拠](management/eligibility.json)
- [抽出順・乱数・標本](management/selection.json)
- [公表パッケージの範囲内外](management/calendar_dispositions.csv)
- [構築集計](management/construction_summary.json)
- [共通規約](global/global_rules.md)

## 30口座一覧

'''+ '\n'.join(rows)+'''

## 公式資料

- [Eurostat Euro indicators release calendar](https://ec.europa.eu/eurostat/news/euro-indicators/release-calendar)：公表予定と対象表の対応。
- [2026 release calendar](https://ec.europa.eu/eurostat/web/products-eurostat-news/w/wdn-20260105-1)：年間予定の暫定性。
- [Impartial access protocol](https://ec.europa.eu/eurostat/about-us/impartiality-protocol)：2025年9月適用版の公表時刻方針。
- [STS metadata](https://ec.europa.eu/eurostat/cache/metadata/en/sts_esms.htm)：系列・調整・率の解釈。
- [Monthly unemployment metadata](https://ec.europa.eu/eurostat/cache/metadata/en/une_rt_m_esms.htm)：失業率の定義。
- [API introduction](https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-introduction)：現行データ取得仕様。各APIクエリ・応答・日時・ハッシュはmanagement/raw内に保存。

## 再生成

空の作業ディレクトリにglobal/config.jsonをconfig.jsonとして、management/rawをrawとしてコピーし、`python scripts/build.py --inputs <入力> --out <新規出力>`を実行する。保存済み応答だけを使い、現在のウェブ再取得は行わない。公開予定の後日変更を含む再収集は別版として扱う。
''')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    return summary

if __name__=='__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    ap=argparse.ArgumentParser();ap.add_argument('--inputs',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();build(a.inputs,a.out)
