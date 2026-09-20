# 提供資料

過去24か月の同一系列・同一地域の数値をdata/history.csvへ格納した。取得日時：2026-09-12T04:21:49.479951+00:00。公表済みデータの構築時点の保存版であり、各過去月の初回公表値を再構成したものではない。

単位：percent change on previous month。系列条件：`{"freq": "M", "indic_bt": "PRC_PRR_DOM", "nace_r2": "B-D", "s_adj": "NSA", "unit": "PCH_PRE", "geo": "EA21"}`。元表：sts_inppd_m。欠測を補間せず、公表元のstatus_flagを保持する。データ取得URLはaccount.jsonに記録する。試験中はURLへアクセスせず保存資料を参照する。

The supplied history is a construction-time snapshot of the latest available vintage, not a reconstruction of each historical first release. Values, units, adjustment and geography follow the specified series key. Source flags are retained; no imputation is performed.
