# PMAF — Prospective Macroeconomic Announcement Forecasting

PMAF is a methodological framework for planning prospective forecasting evaluations around scheduled macroeconomic announcements. It specifies question eligibility, temporal and information conditions, advance fixation, and the records needed to connect questions, submissions, outcomes, and scores.

**The protocol permits manual, software-mediated, AI-assisted, and combined operation. Git-based version control is recommended, not required.** A particular database, directory layout, file format, automatic execution system, or commit/push frequency is not prescribed.

## Start here

| Resource | English | 日本語 |
| --- | --- | --- |
| Construct a QuestionBank | [Construction guide](docs/QB_CONSTRUCTION_MANUAL_en.md) | [QB作成ガイド](docs/QB_CONSTRUCTION_MANUAL_ja.md) |
| Configure and inspect artifacts | [Detailed reference](docs/QB_REFERENCE_en.md) | [設定・ファイル・実装の詳細](docs/QB_REFERENCE_ja.md) |
| Separate frozen inputs and execution records | [Execution and record guide](docs/EXPERIMENT_RECORDS_en.md) | [実行と記録のガイド](docs/EXPERIMENT_RECORDS_ja.md) |
| Inspect the concrete example | [Eurostat 2026 Q4](examples/eurostat_2026q4/README.md) | 同じページに日本語の説明があります |

## What is implemented

The Eurostat example provides two frozen banks, each containing 30 accounts for the same 30 release targets, together with archived inputs and construction, validation, and reproduction code. These are 60 representations of 30 targets, not 60 independent observations. Forecast execution, outcome collection, and forecasting-performance scoring have not been performed. The example is not a general-purpose PMAF execution engine.

Keep frozen QBs unchanged. Store later submissions, supporting evidence, access records, outcomes, and scores separately, linking them to the appropriate QB version and question. Actual experiment records can be held in an experimenter's own storage; this public repository need not receive live answers. The execution guide explains manual operation and possible future automation. Automatic Git commits and pushes are a possible future implementation that may help preserve and trace records. They are not implemented in this artifact, and their benefits have not been evaluated.

## Repository layout

```text
docs/                         General PMAF guidance, with labeled examples
examples/eurostat_2026q4/      Eurostat banks, inputs, scripts, and validation records
scripts/verify_artifact.py    Verify the outer publication-package inventory
ARTIFACT_MANIFEST.json        Inventory of the current publication package
```

## Verify the example

From the repository root, use Python 3.13.9 and install the versions in `examples/eurostat_2026q4/requirements.txt` in an environment outside this repository. Do not use `python -O`. Stop and investigate any failed check.

```sh
python -B scripts/verify_artifact.py .
python -B examples/eurostat_2026q4/scripts/reproduce.py examples/eurostat_2026q4
python -B examples/eurostat_2026q4/banks/binary/scripts/validate.py examples/eurostat_2026q4/banks/binary
python -B examples/eurostat_2026q4/banks/point/scripts/validate_point.py --binary examples/eurostat_2026q4/banks/binary --point examples/eurostat_2026q4/banks/point
python -B examples/eurostat_2026q4/scripts/verify_freeze.py examples/eurostat_2026q4/banks/binary
python -B examples/eurostat_2026q4/scripts/verify_freeze.py examples/eurostat_2026q4/banks/point
```

## Versions and attribution

Record the exact Git commit used. The initial publication is commit `34bee8d0622d4735da7ed28342fb8481e547529b`; its root-level layout remains accessible through Git history. The current example README documents the layout migration and preserves the original bank contents. Updated documentation describes recommendations, not experimental procedures newly performed on those banks.

Original code is licensed under [MIT](LICENSE). Eurostat data and metadata retain their original terms; source URLs and retrieval provenance are preserved. A commit ID identifies a saved version; it does not independently prove submission time, scientific validity, or actual use of those materials.

## 日本語

PMAFは、予定された経済統計の公表に基づき、問いの選定、時間・情報条件、事前固定、予測・判定・採点の記録を定める方法論です。手動・ソフトウェア・AIによる実行を許容し、Git等による版管理を推奨します。特定製品や自動コミット・プッシュを必須にしません。Gitによる自動コミット・プッシュは、記録の保存や追跡に役立つ可能性がある将来の実装案です。本成果物では実装しておらず、導入効果も検証していません。

共通説明は `docs/`、今回のEurostat構築例は `examples/eurostat_2026q4/` に分けています。凍結済みQBには回答を書き込まず、実験ごとの保存先へ記録し、QBの版と問いIDで対応付けます。公開コードは構築・検証までを扱い、予測実行・受付・採点の自動運用は未実装です。
