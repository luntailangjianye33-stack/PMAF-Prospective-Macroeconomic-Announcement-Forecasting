# PMAF：EU関連統計のQuestionBank構築例（2026年Q4）

二値確率予測用の30口座を構築した。公式カレンダーの55公表パッケージから、設定した6統計に対応する18パッケージを取り出し、EU27全体・ユーロ圏21か国へ展開した36問いを審査した。適格な36問いから、乱数シード20260912による単純無作為・非復元抽出で30問いを選定した。層別配分は行っていない。

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
├── accounts/                 問い口座×30
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

対象は指定Eurostatカレンダーから取得できた6系列・2集計地域。EU域内の全経済統計、加盟各国統計、全経済部門の網羅を意味しない。30口座は17公表パッケージに対応し、EUとユーロ圏の重なりや同一系列の繰返しがある。独立した30標本という仮定は置かない。

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

| 問い | 公表予定（現地時刻） | 比較月 | 比較値 (%) |
|---|---|---|---:|
| [une_rt_m__EA21__2026-08__first__above_anchor](accounts/une_rt_m__EA21__2026-08__first__above_anchor/question.md) | 2026-10-01T11:00:00+02:00 | 2026-07 | 6.4 |
| [une_rt_m__EU27_2020__2026-08__first__above_anchor](accounts/une_rt_m__EU27_2020__2026-08__first__above_anchor/question.md) | 2026-10-01T11:00:00+02:00 | 2026-07 | 6.1 |
| [sts_inppd_m__EA21__2026-08__first__above_anchor](accounts/sts_inppd_m__EA21__2026-08__first__above_anchor/question.md) | 2026-10-05T11:00:00+02:00 | 2026-07 | 1.8 |
| [sts_trtu_m__EA21__2026-08__first__above_anchor](accounts/sts_trtu_m__EA21__2026-08__first__above_anchor/question.md) | 2026-10-06T11:00:00+02:00 | 2026-07 | -0.6 |
| [sts_trtu_m__EU27_2020__2026-08__first__above_anchor](accounts/sts_trtu_m__EU27_2020__2026-08__first__above_anchor/question.md) | 2026-10-06T11:00:00+02:00 | 2026-07 | -0.4 |
| [sts_sepr_m__EA21__2026-07__first__above_anchor](accounts/sts_sepr_m__EA21__2026-07__first__above_anchor/question.md) | 2026-10-07T11:00:00+02:00 | 2026-06 | -0.3 |
| [sts_sepr_m__EU27_2020__2026-07__first__above_anchor](accounts/sts_sepr_m__EU27_2020__2026-07__first__above_anchor/question.md) | 2026-10-07T11:00:00+02:00 | 2026-06 | -0.2 |
| [sts_inpr_m__EA21__2026-08__first__above_anchor](accounts/sts_inpr_m__EA21__2026-08__first__above_anchor/question.md) | 2026-10-15T11:00:00+02:00 | 2026-06 | 0.0 |
| [sts_inpr_m__EU27_2020__2026-08__first__above_anchor](accounts/sts_inpr_m__EU27_2020__2026-08__first__above_anchor/question.md) | 2026-10-15T11:00:00+02:00 | 2026-06 | 0.2 |
| [sts_copr_m__EA21__2026-08__first__above_anchor](accounts/sts_copr_m__EA21__2026-08__first__above_anchor/question.md) | 2026-10-20T11:00:00+02:00 | 2026-06 | -1.3 |
| [sts_copr_m__EU27_2020__2026-08__first__above_anchor](accounts/sts_copr_m__EU27_2020__2026-08__first__above_anchor/question.md) | 2026-10-20T11:00:00+02:00 | 2026-06 | -1.0 |
| [une_rt_m__EA21__2026-09__first__above_anchor](accounts/une_rt_m__EA21__2026-09__first__above_anchor/question.md) | 2026-10-30T11:00:00+01:00 | 2026-07 | 6.4 |
| [une_rt_m__EU27_2020__2026-09__first__above_anchor](accounts/une_rt_m__EU27_2020__2026-09__first__above_anchor/question.md) | 2026-10-30T11:00:00+01:00 | 2026-07 | 6.1 |
| [sts_inppd_m__EA21__2026-09__first__above_anchor](accounts/sts_inppd_m__EA21__2026-09__first__above_anchor/question.md) | 2026-11-05T11:00:00+01:00 | 2026-07 | 1.8 |
| [sts_inppd_m__EU27_2020__2026-09__first__above_anchor](accounts/sts_inppd_m__EU27_2020__2026-09__first__above_anchor/question.md) | 2026-11-05T11:00:00+01:00 | 2026-07 | 1.6 |
| [sts_trtu_m__EA21__2026-09__first__above_anchor](accounts/sts_trtu_m__EA21__2026-09__first__above_anchor/question.md) | 2026-11-06T11:00:00+01:00 | 2026-07 | -0.6 |
| [sts_trtu_m__EU27_2020__2026-09__first__above_anchor](accounts/sts_trtu_m__EU27_2020__2026-09__first__above_anchor/question.md) | 2026-11-06T11:00:00+01:00 | 2026-07 | -0.4 |
| [sts_sepr_m__EA21__2026-08__first__above_anchor](accounts/sts_sepr_m__EA21__2026-08__first__above_anchor/question.md) | 2026-11-09T11:00:00+01:00 | 2026-06 | -0.3 |
| [sts_sepr_m__EU27_2020__2026-08__first__above_anchor](accounts/sts_sepr_m__EU27_2020__2026-08__first__above_anchor/question.md) | 2026-11-09T11:00:00+01:00 | 2026-06 | -0.2 |
| [sts_inpr_m__EA21__2026-09__first__above_anchor](accounts/sts_inpr_m__EA21__2026-09__first__above_anchor/question.md) | 2026-11-16T11:00:00+01:00 | 2026-06 | 0.0 |
| [sts_copr_m__EA21__2026-09__first__above_anchor](accounts/sts_copr_m__EA21__2026-09__first__above_anchor/question.md) | 2026-11-19T11:00:00+01:00 | 2026-06 | -1.3 |
| [une_rt_m__EA21__2026-10__first__above_anchor](accounts/une_rt_m__EA21__2026-10__first__above_anchor/question.md) | 2026-12-02T11:00:00+01:00 | 2026-07 | 6.4 |
| [une_rt_m__EU27_2020__2026-10__first__above_anchor](accounts/une_rt_m__EU27_2020__2026-10__first__above_anchor/question.md) | 2026-12-02T11:00:00+01:00 | 2026-07 | 6.1 |
| [sts_inppd_m__EA21__2026-10__first__above_anchor](accounts/sts_inppd_m__EA21__2026-10__first__above_anchor/question.md) | 2026-12-03T11:00:00+01:00 | 2026-07 | 1.8 |
| [sts_inppd_m__EU27_2020__2026-10__first__above_anchor](accounts/sts_inppd_m__EU27_2020__2026-10__first__above_anchor/question.md) | 2026-12-03T11:00:00+01:00 | 2026-07 | 1.6 |
| [sts_trtu_m__EA21__2026-10__first__above_anchor](accounts/sts_trtu_m__EA21__2026-10__first__above_anchor/question.md) | 2026-12-04T11:00:00+01:00 | 2026-07 | -0.6 |
| [sts_trtu_m__EU27_2020__2026-10__first__above_anchor](accounts/sts_trtu_m__EU27_2020__2026-10__first__above_anchor/question.md) | 2026-12-04T11:00:00+01:00 | 2026-07 | -0.4 |
| [sts_inpr_m__EA21__2026-10__first__above_anchor](accounts/sts_inpr_m__EA21__2026-10__first__above_anchor/question.md) | 2026-12-15T11:00:00+01:00 | 2026-06 | 0.0 |
| [sts_inpr_m__EU27_2020__2026-10__first__above_anchor](accounts/sts_inpr_m__EU27_2020__2026-10__first__above_anchor/question.md) | 2026-12-15T11:00:00+01:00 | 2026-06 | 0.2 |
| [sts_copr_m__EA21__2026-10__first__above_anchor](accounts/sts_copr_m__EA21__2026-10__first__above_anchor/question.md) | 2026-12-18T11:00:00+01:00 | 2026-06 | -1.3 |

## 公式資料

- [Eurostat Euro indicators release calendar](https://ec.europa.eu/eurostat/news/euro-indicators/release-calendar)：公表予定と対象表の対応。
- [2026 release calendar](https://ec.europa.eu/eurostat/web/products-eurostat-news/w/wdn-20260105-1)：年間予定の暫定性。
- [Impartial access protocol](https://ec.europa.eu/eurostat/about-us/impartiality-protocol)：2025年9月適用版の公表時刻方針。
- [STS metadata](https://ec.europa.eu/eurostat/cache/metadata/en/sts_esms.htm)：系列・調整・率の解釈。
- [Monthly unemployment metadata](https://ec.europa.eu/eurostat/cache/metadata/en/une_rt_m_esms.htm)：失業率の定義。
- [API introduction](https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-introduction)：現行データ取得仕様。各APIクエリ・応答・日時・ハッシュはmanagement/raw内に保存。

## 再生成

空の作業ディレクトリにglobal/config.jsonをconfig.jsonとして、management/rawをrawとしてコピーし、`python scripts/build.py --inputs <入力> --out <新規出力>`を実行する。保存済み応答だけを使い、現在のウェブ再取得は行わない。公開予定の後日変更を含む再収集は別版として扱う。
