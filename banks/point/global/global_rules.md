# 点予測版：共通実行規約 / Point-forecast global rules

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
