# PMAF：EU関連統計の点予測QuestionBank（2026年Q4）

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

| 口座 | 公表予定（現地） | 固定尺度s |
|---|---|---:|
| [une_rt_m__EA21__2026-08__first__conditional_mean](accounts/une_rt_m__EA21__2026-08__first__conditional_mean/question.md) | 2026-10-01T11:00:00+02:00 | 0.058359 |
| [une_rt_m__EU27_2020__2026-08__first__conditional_mean](accounts/une_rt_m__EU27_2020__2026-08__first__conditional_mean/question.md) | 2026-10-01T11:00:00+02:00 | 0.080645 |
| [sts_inppd_m__EA21__2026-08__first__conditional_mean](accounts/sts_inppd_m__EA21__2026-08__first__conditional_mean/question.md) | 2026-10-05T11:00:00+02:00 | 1.126460 |
| [sts_trtu_m__EA21__2026-08__first__conditional_mean](accounts/sts_trtu_m__EA21__2026-08__first__conditional_mean/question.md) | 2026-10-06T11:00:00+02:00 | 0.478146 |
| [sts_trtu_m__EU27_2020__2026-08__first__conditional_mean](accounts/sts_trtu_m__EU27_2020__2026-08__first__conditional_mean/question.md) | 2026-10-06T11:00:00+02:00 | 0.508604 |
| [sts_sepr_m__EA21__2026-07__first__conditional_mean](accounts/sts_sepr_m__EA21__2026-07__first__conditional_mean/question.md) | 2026-10-07T11:00:00+02:00 | 0.445733 |
| [sts_sepr_m__EU27_2020__2026-07__first__conditional_mean](accounts/sts_sepr_m__EU27_2020__2026-07__first__conditional_mean/question.md) | 2026-10-07T11:00:00+02:00 | 0.401605 |
| [sts_inpr_m__EA21__2026-08__first__conditional_mean](accounts/sts_inpr_m__EA21__2026-08__first__conditional_mean/question.md) | 2026-10-15T11:00:00+02:00 | 1.082260 |
| [sts_inpr_m__EU27_2020__2026-08__first__conditional_mean](accounts/sts_inpr_m__EU27_2020__2026-08__first__conditional_mean/question.md) | 2026-10-15T11:00:00+02:00 | 0.909521 |
| [sts_copr_m__EA21__2026-08__first__conditional_mean](accounts/sts_copr_m__EA21__2026-08__first__conditional_mean/question.md) | 2026-10-20T11:00:00+02:00 | 1.212069 |
| [sts_copr_m__EU27_2020__2026-08__first__conditional_mean](accounts/sts_copr_m__EU27_2020__2026-08__first__conditional_mean/question.md) | 2026-10-20T11:00:00+02:00 | 1.236287 |
| [une_rt_m__EA21__2026-09__first__conditional_mean](accounts/une_rt_m__EA21__2026-09__first__conditional_mean/question.md) | 2026-10-30T11:00:00+01:00 | 0.058359 |
| [une_rt_m__EU27_2020__2026-09__first__conditional_mean](accounts/une_rt_m__EU27_2020__2026-09__first__conditional_mean/question.md) | 2026-10-30T11:00:00+01:00 | 0.080645 |
| [sts_inppd_m__EA21__2026-09__first__conditional_mean](accounts/sts_inppd_m__EA21__2026-09__first__conditional_mean/question.md) | 2026-11-05T11:00:00+01:00 | 1.126460 |
| [sts_inppd_m__EU27_2020__2026-09__first__conditional_mean](accounts/sts_inppd_m__EU27_2020__2026-09__first__conditional_mean/question.md) | 2026-11-05T11:00:00+01:00 | 1.084943 |
| [sts_trtu_m__EA21__2026-09__first__conditional_mean](accounts/sts_trtu_m__EA21__2026-09__first__conditional_mean/question.md) | 2026-11-06T11:00:00+01:00 | 0.478146 |
| [sts_trtu_m__EU27_2020__2026-09__first__conditional_mean](accounts/sts_trtu_m__EU27_2020__2026-09__first__conditional_mean/question.md) | 2026-11-06T11:00:00+01:00 | 0.508604 |
| [sts_sepr_m__EA21__2026-08__first__conditional_mean](accounts/sts_sepr_m__EA21__2026-08__first__conditional_mean/question.md) | 2026-11-09T11:00:00+01:00 | 0.445733 |
| [sts_sepr_m__EU27_2020__2026-08__first__conditional_mean](accounts/sts_sepr_m__EU27_2020__2026-08__first__conditional_mean/question.md) | 2026-11-09T11:00:00+01:00 | 0.401605 |
| [sts_inpr_m__EA21__2026-09__first__conditional_mean](accounts/sts_inpr_m__EA21__2026-09__first__conditional_mean/question.md) | 2026-11-16T11:00:00+01:00 | 1.082260 |
| [sts_copr_m__EA21__2026-09__first__conditional_mean](accounts/sts_copr_m__EA21__2026-09__first__conditional_mean/question.md) | 2026-11-19T11:00:00+01:00 | 1.212069 |
| [une_rt_m__EA21__2026-10__first__conditional_mean](accounts/une_rt_m__EA21__2026-10__first__conditional_mean/question.md) | 2026-12-02T11:00:00+01:00 | 0.058359 |
| [une_rt_m__EU27_2020__2026-10__first__conditional_mean](accounts/une_rt_m__EU27_2020__2026-10__first__conditional_mean/question.md) | 2026-12-02T11:00:00+01:00 | 0.080645 |
| [sts_inppd_m__EA21__2026-10__first__conditional_mean](accounts/sts_inppd_m__EA21__2026-10__first__conditional_mean/question.md) | 2026-12-03T11:00:00+01:00 | 1.126460 |
| [sts_inppd_m__EU27_2020__2026-10__first__conditional_mean](accounts/sts_inppd_m__EU27_2020__2026-10__first__conditional_mean/question.md) | 2026-12-03T11:00:00+01:00 | 1.084943 |
| [sts_trtu_m__EA21__2026-10__first__conditional_mean](accounts/sts_trtu_m__EA21__2026-10__first__conditional_mean/question.md) | 2026-12-04T11:00:00+01:00 | 0.478146 |
| [sts_trtu_m__EU27_2020__2026-10__first__conditional_mean](accounts/sts_trtu_m__EU27_2020__2026-10__first__conditional_mean/question.md) | 2026-12-04T11:00:00+01:00 | 0.508604 |
| [sts_inpr_m__EA21__2026-10__first__conditional_mean](accounts/sts_inpr_m__EA21__2026-10__first__conditional_mean/question.md) | 2026-12-15T11:00:00+01:00 | 1.082260 |
| [sts_inpr_m__EU27_2020__2026-10__first__conditional_mean](accounts/sts_inpr_m__EU27_2020__2026-10__first__conditional_mean/question.md) | 2026-12-15T11:00:00+01:00 | 0.909521 |
| [sts_copr_m__EA21__2026-10__first__conditional_mean](accounts/sts_copr_m__EA21__2026-10__first__conditional_mean/question.md) | 2026-12-18T11:00:00+01:00 | 1.212069 |
