"""Derive a point-forecast QB from the fixed binary QB, without new sampling.
python build_point.py --binary BINARY_BANK --settings point_settings.json --out NEW_DIR
Only reads archived inputs. The source bank remains unchanged.
"""
import argparse, csv, hashlib, io, json, math, shutil, statistics, sys
from copy import deepcopy
from pathlib import Path

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def dump(p,x):put(p,json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def csvput(p,rows):
    s=io.StringIO();w=csv.DictWriter(s,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows);put(p,s.getvalue())
def point_id(q):return q.removesuffix('__above_anchor')+'__conditional_mean'
def history(binary,a):
    j=read(binary/a['input_provenance']['history_file']);r=[]
    for t in sorted(j['dimension']['time']['category']['index']):
        ix=0
        for d,size in zip(j['id'],j['size']):
            key=t if d=='time' else a['series_key'][d]
            ix=ix*size+j['dimension'][d]['category']['index'][key]
        v=j.get('value',{}).get(str(ix))
        if v is not None:r.append({'period':t,'value':v,'status_flag':j.get('status',{}).get(str(ix),'')})
    return r[-24:]

def build(binary,settings,out):
    if out.exists():raise ValueError('Use a new output directory; existing banks are immutable.')
    original=read(binary/'global/config.json');cfg=deepcopy(original);setting=read(settings)
    out.mkdir(parents=True);shutil.copytree(binary/'management/raw',out/'management/raw')
    cfg['identity']={**cfg['identity'],'bank_id':'PMAF_EU_Q4_2026_POINT_30_v0.1','configured_at_utc':setting['configured_at_utc'],'phase':'paired point-forecast construction demonstration; no execution'}
    cfg['objective']['ability']='Forecast the conditional mean of the first published numeric value under the supplied information conditions.'
    cfg['question_generation']={'templates_per_target':1,'format':'point_forecast','target_functional':'conditional_mean','target_value':'first official publication of exactly the series/geography/reference month specified in the account','transform':'identity','input_reference':'latest observed value retained as historical context, not a classification threshold','unit':'percent; 6.1 means 6.1%, not 0.061','rounding':'submit finite decimal number; no additional rounding or clipping before scoring'}
    cfg['selection']={**cfg['selection'],'method':'paired reuse of the previously randomly selected release targets','unit':'release target inherited from binary sample','implementation':'verify original random.Random(seed).sample selection; map binary question IDs to point question IDs; no new draw','source_selection_sha256':sha(binary/'management/selection.json')}
    cfg['quality_and_eligibility']['required']=['source_scope','series_identity','planned_time_feasible','future_target_plan','history_available','point_target_defined','positive_normalization_scale','resolution_defined','unique_id']
    cfg['materials_and_access']['required_historical_reference']='same 24-month inputs as corresponding binary account; reference value is context only'
    cfg['resolution_and_scoring']={**cfg['resolution_and_scoring'],'loss':'((point_estimate - observed_value) / scale_s)^2','primary_metric':'NMSE','aggregation':'equal-weight mean normalized squared error over valid resolved point forecasts, per subject/condition','within_series_summary':'MSE in squared percentage points; report by exact series/geography, not pooled as the primary composite','target_functional':'conditional_mean','rounding':'compare on published numeric scale without binarization or further rounding; no clipping','normalization':setting['normalization']}
    cfg['configuration_history'].append({'phase':'point conversion before generation','decision':'User requested same schema with point forecasts. Preserve the binary sample and all shared release/data/time/access conditions; change response, outcome and loss definitions; compute fixed sample SD from the same 24 historical values. Reference value remains input context.'})
    dump(out/'global/config.json',cfg);dump(out/'global/point_settings.json',setting)
    dump(out/'management/parent_reference.json',{'binary_bank_id':original['identity']['bank_id'],'binary_config_sha256':sha(binary/'global/config.json'),'binary_selection_sha256':sha(binary/'management/selection.json'),'binary_manifest_sha256':sha(binary/'manifest.json') if (binary/'manifest.json').exists() else None,'relationship':'paired format variants of the same 30 release targets, not two independent samples'})
    sel=read(binary/'management/selection.json');converted=deepcopy(sel)
    for key in ['eligible_ordered_ids','draw_order_ids','selected_ids']:converted[key]=[point_id(q) for q in sel[key]]
    converted['eligible_ordered_ids']=sorted(converted['eligible_ordered_ids']);converted['selected_ids']=sorted(converted['selected_ids'])
    converted['algorithm']='paired mapping of archived binary draw; not a new point-format random sample'
    converted['eligible_frame_sha256']=hashlib.sha256(('\n'.join(converted['eligible_ordered_ids'])+'\n').encode()).hexdigest()
    dump(out/'management/selection.json',converted);dump(out/'management/source_binary_selection.json',sel)
    shutil.copy2(binary/'management/calendar_dispositions.csv',out/'management/calendar_dispositions.csv')
    candidates=read(binary/'management/candidate_questions.json');source_checks=read(binary/'management/eligibility.json');all_a=[];mapping=[];checks=[];all_hist={}
    for b in candidates:
        a=deepcopy(b);hist=history(binary,b);vals=[r['value'] for r in hist]
        assert len(vals)==24 and all(math.isfinite(x) for x in vals)
        scale=statistics.stdev(vals);assert math.isfinite(scale) and scale>0,(b['question_id'],'nonpositive scale; do not silently replace sample')
        qid=point_id(b['question_id']);all_hist[qid]=hist
        a['question_id']=qid;a['paired_binary_question_id']=b['question_id'];a['forecast_format']='point_forecast'
        a['historical_reference']=a.pop('anchor')
        a['normalization']={'scale_s':scale,'method':'sample_standard_deviation','ddof':1,'n':24,'period_start':hist[0]['period'],'period_end':hist[-1]['period'],'source':'data/history.csv','unit':'percentage points','role':'fixed positive error normalization; not a forecast or target value'}
        label='EU27か国全体' if a['series_key']['geo']=='EU27_2020' else 'ユーロ圏21か国'
        a['question_ja']=f'{label}について、{a["reference_month"]}を対象とする{a["indicator_label_ja"]}の初回公表値を予測せよ。提供情報に条件付けた平均の推定値を、%単位の数値一つで提出せよ（例：6.1 %は6.1と記入する）。'
        a['question_en']=f'For {a["geography_label"]}, forecast the first published {a["reference_month"]} value of the exact series specified in series_key. Submit one numerical estimate of its conditional mean given the supplied information, in percent (enter 6.1 for 6.1%).'
        a['response_contract']={'field':'point_estimate','type':'finite_real','unit':'percent','target_functional':'conditional_mean','minimum':0 if a['dataset']=='une_rt_m' else -100,'maximum':100 if a['dataset']=='une_rt_m' else None,'out_of_range':'invalid; retain raw submission; no clipping'}
        a['resolution']={k:v for k,v in a['resolution'].items() if k not in ['value_operator','threshold','equal_means','outcome']}
        a['resolution'].update({'numeric_outcome':None,'transform':'identity','rule':'use the archived first-release published numeric value directly; no YES/NO conversion'})
        a['forecast']={'point_estimate':None,'submitted_at':None,'squared_error':None,'normalized_squared_error':None}
        a['scoring']={'primary_metric':'NMSE','per_question_loss':'((point_estimate-numeric_outcome)/scale_s)^2','within_series_metric':'MSE','normalization_scale':scale,'unresolved':'null, excluded with denominator reported'}
        all_a.append(a)
        selected=b['question_id'] in sel['selected_ids']
        mapping.append({'binary_question_id':b['question_id'],'point_question_id':qid,'release_target_id':b['release_target_id'],'selected':selected,'scale_s':scale,'n_history':24})
        for criterion in cfg['quality_and_eligibility']['required']:
            source_key='anchor_and_history' if criterion=='history_available' else criterion
            evidence=[x for x in source_checks if x['question_id']==b['question_id'] and x['criterion_id']==source_key]
            if criterion in ['point_target_defined','positive_normalization_scale','resolution_defined']:
                decision='PASS';reason={'point_target_defined':'conditional mean, identity transform, percent units, finite response and support defined','positive_normalization_scale':f'24 archived observations, ddof=1, scale_s={scale}>0','resolution_defined':'first-release numeric value in exact series and reference month; no binary threshold'}[criterion]
            else:
                assert len(evidence)==1
                decision=evidence[0]['decision'];reason=evidence[0]['evidence']
            checks.append({'question_id':qid,'criterion_id':criterion,'decision':decision,'stage':'point_conversion_eligibility','criterion_version':'1.0','evidence':reason,'source_binary_question_id':b['question_id'],'checked_against_configuration_at':setting['configured_at_utc']})
        assert all(x['decision']=='PASS' for x in checks if x['question_id']==qid)
    dump(out/'management/candidate_questions.json',all_a);dump(out/'management/eligibility.json',checks);csvput(out/'management/format_mapping.csv',mapping)
    csvput(out/'management/candidates.csv',[{'question_id':a['question_id'],'release_target_id':a['release_target_id'],'calendar_package_id':a['calendar_package_id'],'dataset':a['dataset'],'geo':a['series_key']['geo'],'reference_month':a['reference_month'],'status':'PASS','selected':a['question_id'] in converted['selected_ids'],'scale_s':a['normalization']['scale_s']} for a in all_a])
    rules='''# 点予測版：共通実行規約 / Point-forecast global rules

## 対象と入力

各問いの指定系列・地域・参照月の初回公式公表値について、提供情報に条件付けた平均の推定値を提出する。%単位で記入する（6.1 %は6.1）。前月比系列では前月比をそのまま数値予測する。過去の参照値は背景情報として保持し、閾値判定には使わない。

対応する二値版と同一の30発表対象、過去24か月の保存データ、公表予定、提示・締切を用いる。公表予定の336時間前に同一口座を各主体へ提示し、2時間以内に回答を収集する。時刻はUTCの経過時間で計算する。各主体には当該口座のmaterialsと本共通規約を配布する。他口座・management以下は配布しない。両形式を同じ主体へ連続提示する実験は実施していない。

回答中のネットワークを無効化する。提供ファイルと記録付きのローカル計算を許可し、予測市場、その確率の転載・検索要約・市場由来資料は禁止する。事前知識・学習済み知識の除去は保証しない。主体・版・ツール・閲覧・計算・提示受信提出時刻を別途記録する。

## 提出と採点

point_estimateは有限の数値。失業率は0以上100以下、前月比は−100以上とする。範囲外は記録して無効とし、クリッピングしない。本文の提出対象は条件付き平均であり、実現値を事前に既知とみなさない。

指定された初回公表値をnumeric_outcomeとして保存する。最初の公式公表文書のURL・取得日時・ハッシュ・表の位置・値を記録し、後の改定値で置換しない。欠測はnull。未解決に0を割り当てない。

個別の二乗誤差は(point_estimate−numeric_outcome)^2。同一系列・地域内の要約はMSE。6統計を総合する主要指標は、各誤差を固定尺度sで割った二乗の単純平均NMSEとする。sは当該口座の同一系列24履歴値の標本標準偏差（ddof=1）、凍結前に計算し、全主体へ共通適用する。sが非正・非有限、または24か月を取得できない口座は採用しない。この派生では該当時に停止し、別の問いを黙って補充しない。実現値や予測値からsを再計算しない。計画・提出・有効・解決件数と採点分母を併記する。Brier scoreとNMSEの数値を横断して性能順位を付けない。

## 予定・例外

公表日程は暫定。公式11 am CET方針をEurope/Luxembourgの現地時刻として解釈した計画値であり、APIのallDayイベントの11:00Zは検証済みUTC時刻として使わない。実施前に公式時刻・予定を再確認し、変更時は提示前に別版へ移すか除外する。時刻の無断変更はしない。提出前の早期公表は汚染、遅延提出・アクセス違反は無効として保存する。予定公表から24時間以内に初回版証拠を取得できなければ未解決。最新版APIの値を初回値の代替としない。

## English specification

Predict the conditional mean of the first officially published numerical value for the specified series, geography and reference month, given the supplied information. Submit a finite point_estimate in percent (6.1 for 6.1%). The permitted range is [0,100] for unemployment rates and [−100,infinity) for month-on-month changes. Invalid values are retained and rejected without clipping. The historical reference is context, not a binary threshold.

Use the same 30 underlying release targets, 24-month archived histories and temporal/access conditions as the binary bank. Present each assigned account and these rules at R−336 elapsed hours; collect submissions within 2 hours. Disable network access; allow supplied materials and logged local calculations. Prohibit prediction markets and republications or derivatives of their probabilities. Prior or pretrained knowledge is not erased. Management files and other accounts are not supplied. No sequential administration of the two formats to the same subjects has been performed.

Resolve to the exact first-release numerical value, with document URL, timestamp, hash and extraction location. Keep unresolved values null; later revisions do not replace the target. Squared error is (point_estimate−numeric_outcome)^2. Report MSE within each exact series/geography; the primary composite across the six indicators is mean normalized squared error. Its scale s is the fixed sample standard deviation of the same 24 historical observations, ddof=1, computed before freeze and shared across subjects. Missing, nonfinite or nonpositive scales stop construction; no silent replacement occurs. Do not recalculate scales using outcomes or forecasts. Report all denominators and exclusions. Do not rank performance across Brier and NMSE values.

Schedules remain tentative policy-derived plans at 11 am Luxembourg civil time; reconfirm before execution. Preserve schedule changes in separate versions or exclusions, and reject early-publication contamination, late responses and access violations with records. Missing first-publication evidence by R+24 hours remains unresolved. A latest API value is not a substitute for missing first-publication evidence.
'''
    put(out/'global/global_rules.md',rules)
    chosen=[a for a in all_a if a['question_id'] in converted['selected_ids']]
    for a in chosen:
        p=out/'accounts'/a['question_id'];bp=binary/'accounts'/a['paired_binary_question_id']
        dump(p/'account.json',a);(p/'data').mkdir();shutil.copy2(bp/'data/history.csv',p/'data/history.csv')
        put(p/'question.md',f'# {a["question_id"]}\n\n{a["question_ja"]}\n\n{a["question_en"]}\n\n- 提示：{a["time"]["presentation_utc"]}\n- 締切：{a["time"]["submission_deadline_utc"]}\n- 公表予定：{a["time"]["scheduled_release_local"]}（暫定）\n- 主要総合指標：NMSE、固定尺度s={a["normalization"]["scale_s"]}\n\n[共通規約](../../global/global_rules.md)・[個別規約](local_rules.md)\n')
        put(p/'local_rules.md',f'# 個別規約\n\n対象系列はaccount.jsonのseries_keyで特定する。初回公表の数値を直接評価対象とし、条件付き平均の推定を求める。単位・許容範囲はresponse_contractに従う。固定尺度s={a["normalization"]["scale_s"]}。\n\nThe target is the first published numeric value for series_key. Submit its estimated conditional mean. Follow response_contract for units and support. Use the fixed normalization scale in account.json.\n')
        shutil.copy2(bp/'materials.md',p/'materials.md')
    schema={'$schema':'https://json-schema.org/draft/2020-12/schema','title':'PMAF point account v1','type':'object','required':['question_id','paired_binary_question_id','release_target_id','series_key','reference_month','time','response_contract','normalization','resolution','forecast','scoring'],'properties':{'forecast_format':{'const':'point_forecast'},'normalization':{'type':'object','required':['scale_s','n','ddof'],'properties':{'scale_s':{'type':'number','exclusiveMinimum':0},'n':{'const':24},'ddof':{'const':1}}},'resolution':{'type':'object','required':['numeric_outcome'],'not':{'required':['threshold']}},'forecast':{'type':'object','required':['point_estimate'],'not':{'required':['p_yes']}},'eligibility_status':{'const':'PASS'}}}
    dump(out/'global/account.schema.json',schema)
    summary={'candidate_questions':len(all_a),'eligible_questions':len(all_a),'selected_accounts':len(chosen),'selected_release_targets':len({a['release_target_id'] for a in chosen}),'selected_release_packages':len({a['calendar_package_id'] for a in chosen}),'positive_scales_candidates':len(all_a),'history_rows':24*len(chosen),'new_random_draws':0,'forecast_runs':0,'resolved_outcomes':0,'scores':0,'primary_metric':'NMSE','source_binary_selection_sha256':sha(binary/'management/selection.json')}
    dump(out/'management/construction_summary.json',summary)
    put(out/'scripts/build_point.py',Path(__file__).read_text(encoding='utf-8'))
    table=['| 口座 | 公表予定（現地） | 固定尺度s |','|---|---|---:|']
    for a in sorted(chosen,key=lambda a:(a['time']['scheduled_release_local'],a['question_id'])):table.append(f'| [{a["question_id"]}](accounts/{a["question_id"]}/question.md) | {a["time"]["scheduled_release_local"]} | {a["normalization"]["scale_s"]:.6f} |')
    put(out/'README.md','''# PMAF：EU関連統計の点予測QuestionBank（2026年Q4）

二値確率版と同じ30発表対象について、点予測の問い口座を作成した。元の36適格候補からの無作為抽出結果を対応付け、追加抽出は行っていない。両版の参照月・地域・系列・履歴データ・提示時刻・回答時間・公表予定・情報条件を保持した。

提出対象は指定公表値の条件付き平均。初回の数値公表を正解とし、6統計の総合採点はNMSEを指定する。正規化尺度は同一系列の保存済み24か月履歴から計算した標本標準偏差（ddof=1）。同一系列・地域内の誤差要約にはMSEを用いる。未来の正解・回答・得点は未取得で、全件nullである。

## 内容

- [具体的設定](global/config.json)／[共通規約](global/global_rules.md)
- [二値版との36候補の対応](management/format_mapping.csv)／[選定記録](management/selection.json)
- [点予測の審査](management/eligibility.json)／[構築集計](management/construction_summary.json)

各accountsフォルダーに日英の問い、機械可読口座、24か月のhistory.csv、個別規約と資料説明を収める。共通規約は口座の外側に置く。元応答と来歴はmanagement/rawに保存する。

公表時刻は二値版と同じ暫定計画値であり、実施前に公式予定との再照合が必要。今回は構築と保存入力からの再生成を検証した。前向き実行、期間内解決、予測性能の検証は未実施である。30口座は17公表パッケージに対応し、同一系列やEU・ユーロ圏の依存性を含む。

## 再生成

`python scripts/build_point.py --binary <二値版QB> --settings global/point_settings.json --out <新規出力>`

保存された二値QBだけを入力に使用し、外部APIの再取得は行わない。別版への変換記録と入力ハッシュを保持する。生成ファイルの内容固定はmanifest.jsonとfreeze.jsonで確認する。ローカルのハッシュ・日時は第三者タイムスタンプではない。

## 30口座一覧

'''+ '\n'.join(table)+'\n')
    return summary

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');ap=argparse.ArgumentParser();ap.add_argument('--binary',type=Path,required=True);ap.add_argument('--settings',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();print(json.dumps(build(a.binary,a.settings,a.out),ensure_ascii=False,indent=2))
