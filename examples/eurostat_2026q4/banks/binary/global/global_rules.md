# 共通実行規約 / Global execution rules

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
