# PMAFの設定・ファイル・実装リファレンス

版：0.3／更新日：2026-09-21

[作成ガイドへ戻る](QB_CONSTRUCTION_MANUAL_ja.md) · [English](QB_REFERENCE_en.md)

作業中に必要な設定項目、ファイルの意味、検査条件を確認するための資料です。一般的な要件に加えて、**Eurostat版の保存場所・設定値・コード上の制約を具体例として掲載**しています。パスや固定値を別の実験に適用する場合は、実装との対応を確認してください。

- [設定項目を調べる](#configuration)
- [用語とファイルの配置を調べる](#files)
- [例：Eurostatの応答を取得・解釈する](#acquisition)
- [適格性と時間条件を確認する](#eligibility)
- [例：無作為抽出の記録を確認する](#sampling)
- [例：口座のファイルと数値を確認する](#accounts)
- [検査の範囲を確認する](#validation)
- [凍結と後続記録を管理する](#freeze-reference)
- [例：公開コードを別の実験へ適用する](#implementation)
- [例：再生成の詳細と出力を保存する](#retain-output)
- [公開する資料と利用条件を確認する](#publication)
- [検証記録と出典を確認する](#sources)

<a id="configuration"></a>
## 1. 設定項目を調べる

次表の事項を、具体値または決定規則として記録する。PMAFの一般的な設定項目と、この配布コードが解釈できる項目は同一ではない。新しい設定を使う際は[実装の制約](#implementation)も確認する。

| 設定する事項 | 決める内容 | 既存の保存先 |
| --- | --- | --- |
| 評価目的・主体 | 何の能力を、誰・どのシステムで測るか | `objective` |
| 管理情報 | QB ID、設定の版、作成者、日時、変更理由 | `identity`, `configuration_history` |
| 期間 | 実験開始・終了、公表予定の対象期間、参照期間の条件 | `time_design`, `collection_request` |
| 対象 | 公表機関、地域、統計分野、データセット、次元・分類の版 | `collection_request`, `series` |
| 収集 | 情報源、クエリ、基準時点、列挙・停止・重複処理、保存方法 | `collection_request` と取得記録 |
| 問い | 二値／点、初回値等の対象版、単位、変換、閾値または目的量 | `question_generation` |
| 時間 | 提示から公表までのH、回答時間D、公表後の処理時間b | `time_design` |
| 適格性 | 必須条件、根拠、PASS・FAIL・UNVERIFIED、裁定方法 | `quality_and_eligibility` |
| 選定 | 件数N、抽出単位・方法・候補順序・乱数実装・不足時処理 | `selection` |
| 提供資料 | 必須の履歴・定義資料・比較値、その版と更新方針 | `materials_and_access` |
| 情報条件 | ネット、予測市場、他者予測、計算ツール、記録範囲 | `materials_and_access` |
| 結果・採点 | 公式根拠、版、取得期限、境界、指標、尺度、集約単位 | `resolution_and_scoring` |
| 例外・凍結 | 延期・欠測・取得失敗・違反・補充・変更と存在時刻の証拠 | `exceptions_and_records` |

今回の設定は、公表予定が2026年10〜12月、EU27_2020・EA21、6データセット、30問、非復元抽出、H=336時間、D=2時間、b=24時間、履歴24か月である。これらは例示用の選択であり、PMAF全体の固定値ではない。

設定をJSONやYAMLで記述することと、その設定を検証するスキーマを定めることを区別する。現行コードの入力はJSONであり、YAMLをそのまま読み込む機能はない。設定の構造を検証する完全なスキーマも現行配布物にはなく、`account.schema.json` は生成された口座用である。

<a id="files"></a>
## 2. 用語とファイルの配置を調べる

| 単位 | 意味 | Eurostat構築例 |
| --- | --- | --- |
| 実験設定 | 対象範囲、日時、問い数、資料、採点等の具体値・選択 | `global/config.json` |
| データスキーマ | 保存データの構造、型、必須項目、値の制約 | `global/account.schema.json` |
| 評価プロトコル | 選定・提示・結果判定・採点・例外処理の条件と規則 | 共通規約・個別規約と論文第3・4章 |
| 公表パッケージ | カレンダー上の一件の発表記録 | 複数の地域や系列を含むことがある |
| 発表候補集合 U | 系列・地域・参照期間・公表版まで特定した発表対象の集合 | 設定範囲の18パッケージから36対象を得た |
| 問い候補集合 P | 発表対象とテンプレートから生成した問い | 今回は1対象につき1問 |
| 適格集合 C | 必須条件を満たすと確認した問い | 今回は36問。無作為抽出する際の問いの抽出枠 |
| 採用集合 Q | Cから選定した問い | 今回は30問 |
| 問い口座 | 一つの問い、資料、時間・情報条件、判定規則を対応付けた単位 | `accounts/<question_id>/` |
| QuestionBank | 問い口座と共通規約・索引・構築記録を含む管理単位 | `examples/eurostat_2026q4/banks/binary/` または `examples/eurostat_2026q4/banks/point/` |

データセットコードと系列を区別する。例えば `une_rt_m` だけでは一つの失業率系列は決まらない。`freq=M`、`s_adj=SA`、`age=TOTAL`、`sex=T`、`unit=PC_ACT`、`geo=EU27_2020` 等の次元の値を合わせて指定する。[Eurostatのメタデータ](https://ec.europa.eu/eurostat/cache/metadata/en/une_rt_m_esms.htm)を用いて、その組合せが意図する対象を表すか確認する。

```text
repository/
├── README.md
├── LICENSE
├── release_status.json
├── ARTIFACT_MANIFEST.json
├── docs/                         PMAF guides / 共通ガイド
├── scripts/
│   └── verify_artifact.py
└── examples/
    └── eurostat_2026q4/
        ├── README.md
        ├── requirements.txt
        ├── verification.json
        ├── layout_verification.json
        ├── scripts/
        │   ├── reproduce.py
        │   └── verify_freeze.py
        ├── manuscript/paired_account_examples.md
        └── banks/
            ├── binary/
            │   ├── global/
            │   ├── accounts/<question_id>/
            │   ├── management/
            │   ├── scripts/
            │   ├── manifest.json
            │   └── freeze.json
            └── point/
```

共通規約は口座の外、QBの内側に置く。予測者に配布する範囲は口座の `materials` と共通規約で指定する。`management/` や他の口座まで一括配布しない。マニュアルは凍結済みQBの外側の `docs/` に置き、説明を更新するたびに既存口座のハッシュが変わることを避ける。

<a id="acquisition"></a>
## 3. 例：Eurostatの応答を取得・解釈する

### 日程と数値を別々の情報源から取得する

Eurostat版は、[公式Release calendar](https://ec.europa.eu/eurostat/news/euro-indicators/release-calendar)を日程の出典とし、統計APIとメタデータを系列・履歴値の出典とした。公開カレンダー画面の配信応答として、`https://ec.europa.eu/eurostat/o/calendars/eventsJson` の応答を保存している。この配信先を、永続的な契約を持つ汎用APIとみなさない。利用時には公式画面との対応と応答構造を再確認する。

統計APIのクエリ例は次の形である。これはクエリの構造を示す例であり、今回の保存時点を再現するURLではない。

```text
https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/une_rt_m
  ?lang=en&freq=M&s_adj=SA&age=TOTAL&sex=T&unit=PC_ACT
  &geo=EU27_2020&sinceTimePeriod=2024-01
```

各応答を加工前のバイト列で保存し、その隣に取得記録を置く。

```text
raw/history_une_rt_m.json
raw/history_une_rt_m.json.provenance.json
```

取得記録には、最終的なURLとクエリ、要求・取得日時、HTTP状態、Content-Type、応答サイズ、SHA-256を含める。HTTP失敗や数値のない応答も理由の記録として残す。200であることだけでは必要な系列・期間の数値があることを確認したことにならない。

### 数値の取り出し方

EurostatのStatistics APIが返すJSON-statでは、`id`、`size`、各次元の `category.index` に従って値の位置を求める。オブジェクトの表示順やラベルの見た目から位置を推定しない。`value` の欠損を0へ変換せず、`status` に記録された注記を保持する。形式は [JSON-stat公式仕様](https://json-stat.org/format/) に従う。

既存の `build.py` は保存応答のオブジェクト形式の `value`・`category.index` を前提としている。JSON-statが許す別の配列形式を扱う場合は、デコーダーの対応を追加してから使用する。`validate.py` は構築側の添字計算とは別の列挙方法で履歴値を再照合する。

<a id="eligibility"></a>
## 4. 適格性と時間条件を確認する

Uの各発表対象に有限のテンプレートを適用し、Pを得る。次の必須項目を審査する。具体的な閾値や履歴長は事前設定に従う。

| 検査 | PASSの例 | 不適格・未確認の例 |
| --- | --- | --- |
| 範囲 | 指定機関・地域・統計分野に一致 | 対象外の統計や地域 |
| 対象の識別 | 次元、単位、調整区分、参照月、公表版が一意 | 水準か前月比か未確定、同名の別系列 |
| 時間 | T=R−H、C=T+D、0<D<H、t0≤T、R+b≤t1 | 提示が実験開始前、結果取得期限が終了後 |
| 未公表性の計画 | 保存入力に対象値がなく、資料取得が提示前 | 対象値が既に含まれる。実際の提出時点の未公表性は後で再確認する |
| 資料・比較値 | 同一系列の必要履歴・固定閾値を確認 | 履歴不足、異なる単位のアンカー、対象値を資料へ混入 |
| 解決可能性 | 指定版の取得先・対象箇所・抽出規則を根拠資料で確認 | 初回公表を求めるのに最新版APIしか指定していない |
| 一意性 | 問いIDが一意で元発表へ追跡できる | 同じIDに異なる問い、参照先不明 |
| 点予測の追加条件 | 目的量・単位・許容範囲と正の有限な尺度を確認 | 尺度0、無限値、条件付き平均を求めながら主要損失が不整合 |

各判定には `question_id`、基準ID・版、必須かどうか、判定、根拠、出典、担当者またはコード版、確認した時点を記録する。必須項目が未確認ならCへ含めない。研究目的への適合は人間の審査も可能だが、採否の根拠を残す。

既存の二値コードは、各条件の真偽からPASS／FAILを生成し、不明状態の多くを独立したUNVERIFIEDとして扱う機能はない。また、`resolution_defined` は取得先の説明が空でないことの検査にとどまる。公式文書から必要な初回値を実際に抽出できることは、既公表の同種文書を使って別途確認する。現在のPASSは構築時の検査範囲に対する判定である。

時刻については、今回の保存版は「11 am CET」の方針をEurope/Luxembourgの現地時刻として適用した暫定値を使う。カレンダーの `allDay` と `start` の値だけから厳密な実公表時刻を確定しない。現地時刻からUTCへの変換にはIANAの時間帯情報を使用し、夏時間の境界をまたぐH・DはUTCの経過時間で計算する。[Python zoneinfo](https://docs.python.org/3.13/library/zoneinfo.html)

<a id="sampling"></a>
## 5. 例：無作為抽出の記録を確認する

Cを問いの抽出枠として保存する。単純無作為・非復元抽出の例では、候補IDの順序、乱数種、Pythonと実装の版、抽出順、最終採用IDを残す。乱数種だけの保存では十分でない。[Python randomの仕様](https://docs.python.org/3.13/library/random.html#random.sample)

```python
ordered_ids = sorted(eligible_question_ids)
k = min(requested_count, len(ordered_ids))
draw_order = random.Random(seed).sample(ordered_ids, k)
selected_ids = sorted(draw_order)
```

上例の不足時処理は「足りなければ全件採用」という今回の設定に対応する。層化・意図的選定・別の不足時処理を使う場合は、その規則と実装を対応させる。選定後に都合のよい問いへ差し替えない。資料作成で失敗したときの補充・停止も事前設定に従う。

保存版では、`management/selection.json` に36候補の順序、seed=20260912、抽出順、採用30ID、抽出枠のハッシュを格納する。点予測版は対応するIDへ変換し、同じ標本を引き継ぐ。60口座は30発表対象の二つの表現であり、独立な60対象ではない。

<a id="accounts"></a>
## 6. 例：口座のファイルと数値を確認する

各口座に次を用意する。

| ファイル | 内容と確認する点 |
| --- | --- |
| `question.md` | 日英の問い。対象月、対象系列、提出形式が `account.json` と一致する |
| `account.json` | ID、系列キー、参照月、時間、閾値または目的量、資料参照、判定・採点条件 |
| `data/history.csv` | `period,value,status_flag`。同一系列・地域の必要期間の履歴 |
| `materials.md` | データの意味、単位、出典、取得時点、版、変換・欠測処理 |
| `local_rules.md` | 共通規約を適用した上で、その問いに固有の条件 |

既存の口座には24か月分の履歴を付けている。これは構築時点で取得した保存版であり、各過去月の初回公表値を集めたものではない。ニュース、政策文書、他の指標のデータは添付していない。長い公式定義文書の全文も各口座には添付せず、系列の次元・短い定義・資料説明を持つ。別の課題でそれらが必要なら、提供資料として新たに収集・固定する。

二値方式は、指定初回値が固定閾値を厳密に上回る確率を求める。等号はNO。点予測方式は同じ初回値の条件付き平均を数値で求める。履歴の直近値は点予測では参考情報として保持する。

今回の点予測の総合指標は、事前固定した尺度sで誤差を割った二乗の平均NMSEである。同一系列・地域内ではMSEを併記する。sは24履歴値について平方根内の分母を23とする標本標準偏差で、対象値や提出予測から再計算しない。割合・変化率は%表示の数値、差とsはパーセントポイント、MSEはパーセントポイントの二乗となる。

将来の回答・結果・得点を作成時に埋めない。二値版の `forecast.p_yes`、点予測版の `forecast.point_estimate`、各版の結果・得点は未取得を表すnullとする。未解決をNOや0点で置換しない。

<a id="validation"></a>
## 7. 検査の範囲を確認する

1. **構造**：必須フィールド、型、形式、値域。JSON Schemaで検査する。
2. **参照**：口座IDとフォルダー、採用IDと実在口座、資料パス、共通規約参照。
3. **意味・計算**：系列と次元、単位、期間、履歴値、閾値、H・D・b、正規化尺度。
4. **出典**：元応答とSHA-256、文書の対象、公表版の取得手順。
5. **件数**：収集、範囲外、候補、適格、採用、失敗・未確認を対応付ける。
6. **二つの方式の対応**：対象発表、系列、資料、時間・情報条件が一致し、形式固有の規則だけが変わっているか確認する。
7. **文章**：`question.md`、`account.json`、共通・個別規約の数値と意味を照合する。現行の自動検査は自然言語の全記述を検証しない。

JSON Schemaの `$ref` は別のスキーマを参照して適用する仕組みである。資料ファイルの存在や、別の口座にあるIDとの一致は追加検査で確認する。[JSON Schema公式説明](https://json-schema.org/understanding-json-schema/structuring)

すべての必須項目を確認して作成完了とする。自動検査のPASS、独立した内容審査、実際の予測実験の成立はそれぞれ記録する。同じコードから同じ誤りを再生成できる場合もあるため、バイト一致を内容の正しさの代用にしない。

プログラムで構築する新しいQBでは、構築直後、正式な凍結および予測実験の開始前に、保存した入力、同じ設定・コード・依存環境から別の保存先へ再構築し、最初の構築結果との一致を確認することを推奨する。比較するファイルの範囲を事前に定め、毎回変わる実行日時や実行ログ、構築後に追加する凍結記録とは区別する。不一致の原因を解消し、入力・設定・コードを変更した場合は変更後のQBで再確認する。一致と内容検査を確認してから正式に凍結し、予測実験を開始する。ここでの再構築は保存した入力を用いるため、後日の最新データの再取得を伴わない。凍結後も同じ検証を実施できるが、実験終了を待つ必要はない。この確認は構築処理の再現性を調べるものであり、凍結済みファイルの変更の有無をハッシュで確認する操作や、問い・資料の内容を審査する操作と区別する。

**運用方法の選択：** 手動、ソフトウェア、AI、またはそれらの組合せを利用できます。Git等の版管理と、プログラムで構築したQBの再構築確認は推奨手段です。特定の保存形式、自動実行、自動コミット・プッシュは必須ではありません。凍結版の固定、記録の対応付け、訂正履歴、必要な証拠の保存は、方式に応じた手段で実施します。[実行と記録のガイド](EXPERIMENT_RECORDS_ja.md)を参照してください。 Gitによる自動コミット・プッシュは、記録の保存や追跡に役立つ可能性がある将来の実装案です。本成果物では実装しておらず、導入効果も検証していません。

<a id="freeze-reference"></a>
## 8. 凍結と後続記録を管理する

この節のmanifestとハッシュによる手順は、電子ファイルを用いる推奨実装例です。他の保存方式でも、固定内容・版・事前固定の根拠と変更履歴を検証できるようにします。

### 凍結対象を確定する

凍結対象には口座、提供資料、共通・個別規約、設定、スキーマ、採否・抽出記録、構築に用いた原応答とコードを含める。検査後に変更が入った場合は必要な検査を再実施する。ファイルを読み出している間に内容が変化しない状態にする。

### ファイル一覧と内容のハッシュを保存する

本配布形式に合わせる場合の手順は次のとおりである。既存版のmanifestを再発行して、変更をなかったことにしてはならない。

```text
対象ファイルを相対パスで列挙・整列する
  → 各ファイルのサイズとSHA-256を計算する
  → manifest.jsonに algorithm と files[{path,bytes,sha256}] を保存する
  → 保存されたmanifest.jsonそのもののSHA-256を計算する
  → freeze.jsonにその値、版、実施者、申告時刻、検査結果を保存する
  → 保存後に一覧とハッシュをもう一度照合する
```

manifest自身とfreeze記録を同じmanifestの計算対象から外し、循環参照を避ける。UTF-8の文字列が同じでも改行・空白・JSONキー順が違えばバイト列とハッシュは変わる。バイト一致を要件にする場合は、シリアライズ方法・改行・エンコーディングを固定する。既存の `verify_freeze.py` はこの配布物用の照合器であり、新規凍結を生成するCLIではない。

ファイル一覧とチェックサムの考え方は [BagIt RFC 8493](https://www.rfc-editor.org/rfc/rfc8493) を参考にする。本配置はBagIt完全準拠を主張しない。

### 存在時刻を示す証拠

ローカルの時計とハッシュは内容の照合を支える。公開比較で「提示前までにこの版を固定していた」と第三者へ示す場合は、最初の提示前にmanifest等のダイジェストへ独立した時刻の証拠を対応付ける。[RFC 3161](https://www.rfc-editor.org/rfc/rfc3161)に基づくタイムスタンプを一つの方法として使える。今回の保存版には外部タイムスタンプがない。後日取得した証拠で、過去の存在時刻を遡って証明したとしない。

予測・解決・採点の記録は、凍結版の外側に追記し、QB ID・版・問いID・run ID、およびmanifestを採用した場合はそのハッシュで対応付ける。口座にあるnullを実験結果で上書きする運用は、元の凍結版には行わない。配布用に私的ファイルを除く場合は別のmanifestを持つ配布版として、除外した内容と元版との関係を記録する。

<a id="implementation"></a>
## 9. 例：公開コードを別の実験へ適用する

| 箇所 | 実物に残る制約 | 新しいQBで必要な対応 |
| --- | --- | --- |
| `build.py` の履歴取得・検査 | 24か月をコード内に固定 | 設定、抽出、検査、説明文の全箇所を対応させる |
| 生成する共通規約・README | 336時間、2時間、24時間、Q4等の説明を含む | 計算した日時と生成文章が一致するよう改修する |
| `fetch.py` | カレンダーの期間が固定。スクリプトの隣に `raw/` を作る | 保存先・期間を新規版へ明示的に変更して実行する |
| `acquire.py` | 同じフォルダーの `series.json` を前提とするが、配布版にはその場所のファイルがない | 現状のまま収集コマンドとして実行しない。新しい収集入力と保存先を用意する |
| API応答のデコード | 保存例のJSON-stat表現に依存 | 応答形式の変更と欠測表現への対応を検証する |
| 適格性の状態 | 二値の真偽判定中心。未確認の三値管理は全面実装されていない | 不明を採用に流さず、理由を保存して停止・保留する |
| 解決手順 | 取得先の説明の有無を検査する部分がある | 既公表文書から対象値を抽出する検証を追加する |
| 点予測変換・検査 | 30口座・36候補・24履歴値を前提とする箇所がある | 新しい件数、適格性、単位・値域・損失に対応させる |
| 将来の実験 | 配布・提出・公表値取得・採点は未実装 | 第4章の規約に従う別の運用手順と記録を用意する |

設定ファイルだけを変更した出力を、別条件に正しく適応したQBと扱わない。コード、スキーマ、自動検査、問い本文、共通規約を同じ実験設定へ対応させる。新規版では、対象値が既に公表されていないかも収集時と提示時に確認する。

保存例には失業率の日本語ラベル「全年齢」が残っている。`age=TOTAL` に対応する公式定義は15〜74歳であり、論文にはその説明がある。既存の証拠を保持しつつ、実際の予測実験に用いる版では問いの文章を公式定義へ対応させる。また、現時点から元版の過去の提示予定へ遡って実験を開始したことにはできない。将来の適格な対象と日程を再設定する。

<a id="retain-output"></a>
## 10. 例：再生成の詳細と出力を保存する

### 環境を揃える

構築時の環境は `examples/eurostat_2026q4/banks/binary/management/runtime.json` に保存されている。

| 項目 | 保存された版 |
| --- | --- |
| Python | 3.13.9 |
| jsonschema | 4.25.0 |
| tzdata | 2025.2 |
| requests | 2.32.5 |

Python 3.13.9を利用できる環境で、`python --version` を確認する。新しい環境を作る場合のPowerShell例を示す。実行場所はリポジトリのルートである。

```powershell
python -m venv ../pmaf-qb-venv
& ../pmaf-qb-venv/Scripts/python.exe -m pip install -r examples/eurostat_2026q4/requirements.txt
```

以下の `python` は、この環境の実行ファイルに読み替える。環境構築のパッケージ取得には通信が必要だが、構築結果の再生成には保存済み応答だけを使用する。仮想環境・ログ・再生成出力は、配布パッケージ全体のファイル照合を妨げないようリポジトリの外に保存する。

### 実行コマンド

各コマンドの終了コードと出力を確認し、失敗した段階で停止する。`python -O` は使用しない。この実装の検査には `assert` が含まれ、最適化オプションで省略されるためである。

```powershell
python -B scripts/verify_artifact.py .
python -B examples/eurostat_2026q4/scripts/reproduce.py examples/eurostat_2026q4
python -B examples/eurostat_2026q4/banks/binary/scripts/validate.py examples/eurostat_2026q4/banks/binary
python -B examples/eurostat_2026q4/banks/point/scripts/validate_point.py --binary examples/eurostat_2026q4/banks/binary --point examples/eurostat_2026q4/banks/point
python -B examples/eurostat_2026q4/scripts/verify_freeze.py examples/eurostat_2026q4/banks/binary
python -B examples/eurostat_2026q4/scripts/verify_freeze.py examples/eurostat_2026q4/banks/point
```

`-B` はバイトコードキャッシュの書き込みを抑える。`reproduce.py` は一時ディレクトリに出力し、終了時にその一時出力を片付ける。元のQBに上書きしない。検査のJSONを保存する場合も、保存先をQBの外側にする。

| 確認対象 | この保存版での期待値 |
| --- | --- |
| 二値版の再生成 | 207生成ファイルのパス・SHA-256が一致 |
| 点予測版の再生成 | 211生成ファイルのパス・SHA-256が一致 |
| 二値版の検査 | PASS、540項目 |
| 点予測版の検査 | PASS、574項目 |
| 配布用の二値版manifest | 221ファイルの内容を照合 |
| 配布用の点予測版manifest | 216ファイルの内容を照合 |

件数はこの保存版に対する値である。再生成ファイル数は構築プログラムの出力数であり、その後に追加した検証記録等を含むmanifestの件数とは異なる。配布用コピーでは私的な論文参照ファイル等を除外し、再生成用の補足記録も保持している。元のアーカイブとの関係は、件数の一致だけで判断せず、`examples/eurostat_2026q4/banks/binary/management/distribution.json` と各manifestのファイル一覧で確認する。

この再生成は、元応答からの構築を再実行する検査である。同じURLへ再アクセスして過去の応答を回収する操作ではない。Eurostatの通常APIは最新のデータセットを返すため、後日の再取得では改定値や予定変更を含み得る。[Eurostat API公式案内](https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-introduction)

### 再生成出力を手元に残す場合

次のPowerShell例は、新規ディレクトリへ二値版の構築出力を保存する。`../pmaf-replay-inputs`、`../pmaf-rebuilt-binary`、`../pmaf-rebuilt-point` が存在しない状態で実行する。

```powershell
New-Item -ItemType Directory -Path ../pmaf-replay-inputs
Copy-Item -LiteralPath examples/eurostat_2026q4/banks/binary/management/build_input_config.json -Destination ../pmaf-replay-inputs/config.json
Copy-Item -LiteralPath examples/eurostat_2026q4/banks/binary/management/raw -Destination ../pmaf-replay-inputs/raw -Recurse
python -B examples/eurostat_2026q4/banks/binary/scripts/build.py --inputs ../pmaf-replay-inputs --out ../pmaf-rebuilt-binary
python -B examples/eurostat_2026q4/banks/binary/scripts/validate.py ../pmaf-rebuilt-binary
python -B examples/eurostat_2026q4/banks/point/scripts/build_point.py --binary examples/eurostat_2026q4/banks/binary --settings examples/eurostat_2026q4/banks/point/global/point_settings.json --out ../pmaf-rebuilt-point
python -B examples/eurostat_2026q4/banks/point/scripts/validate_point.py --binary examples/eurostat_2026q4/banks/binary --point ../pmaf-rebuilt-point
```

完全なバイト一致を調べる二値版再生成には `management/build_input_config.json` を使う。このファイルと `global/config.json` の設定値は同じだが、元のJSONキー順を保持している。既存の構築コードではキー順が文章内のJSON表示に影響する。点予測版は親QBのmanifestハッシュを保存するため、上例では元の配布用二値版を入力としている。manifestをまだ作っていない再生成途中の二値版を入力にすると、親版の記録まで同じにはならない。

新規出力には構築後の凍結・検査の補足ファイルは含まれない。独立した新版として保存・配布する場合には、[凍結の手順](#freeze-reference)を別途行う。

<a id="publication"></a>
## 11. 公開する資料と利用条件を確認する

公開時には次を同じリポジトリの同じリリースから参照できるようにする。

- 二値確率版・点予測版の全口座、履歴CSV、設定・規約。
- 原応答・取得記録、全候補と採否、抽出順・乱数種。
- 構築・検査・再生成コード、依存環境。
- 本マニュアルの日英両版と、論文に掲載した対応例。
- QBごとのmanifest・凍結記録、配布パッケージのmanifest。

公開先は[PMAFリポジトリ](https://github.com/luntailangjianye33-stack/PMAF-Prospective-Macroeconomic-Announcement-Forecasting)とする。リリースタグとコミットIDは公開時に記録し、論文の参照先をその版に対応付ける。DOIを取得する場合も同じ版との対応を記録する。[GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)と [CITATION.cff](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files)は、固定版の配布と引用情報の提供に使える。

自作コードは著者がMITで公開する方針を選択済みである。著作権表示を含むLICENSEをリポジトリ直下に置く。Eurostat等の第三者資料には各出典の利用条件を適用し、MITを一括で適用したと記載しない。APIキー、私的な原稿、個人の絶対パスや不用意な実行ログが含まれないかを配布対象について確認する。

マニュアルやREADME等を変更すると、外側の `ARTIFACT_MANIFEST.json` の対象が変わる。配布候補の内容を確認した上で外側の一覧を更新し、全体を再照合する。凍結済みの `examples/eurostat_2026q4/banks/*/manifest.json` と口座ファイルを文書更新に合わせて変更しない。

<a id="sources"></a>
## 12. 検証記録と出典を確認する

2026-09-20に、配布コード、設定、系列キー、来歴、スキーマ、manifestを確認した。[再生成・検査コマンド](#retain-output)の実行結果は、同じ `docs/` の `QB_MANUAL_VERIFICATION_20260920.json` に記録する。新しい期間に対する収集・予測・採点を実行した記録ではない。

Web資料は2026-09-20に参照した。主な根拠は、Eurostatの公式API・カレンダー・系列メタデータ、JSON-stat、JSON Schema、Pythonの乱数・時間帯仕様、RFC 8493・3161、およびGitHubの公開・引用資料である。これらの仕様が定める部分と、PMAFが選択した手順や今回の実装上の制約を区別して利用する。

上記の2026年9月20日の検証記録は当時の配置を示すため、そのまま保持しています。現在の例示フォルダーへの移動と内容の一致は、`examples/eurostat_2026q4/layout_verification.json`に記録しています。

### このガイドの編集方針

操作を目的ごとに分け、準備・手順・結果を近くに置く構成には、[Appleのサポート記事](https://support.apple.com/ja-jp/104984)、[AWSのチュートリアル](https://docs.aws.amazon.com/AmazonS3/latest/userguide/tutorial-s3-mpu-additional-checksums.html)、[Googleの手順記述ガイド](https://developers.google.com/style/procedures)、[Microsoftの手順記述ガイド](https://learn.microsoft.com/en-us/style-guide/procedures-instructions/writing-step-by-step-instructions)を参考にした（2026-09-21参照）。
