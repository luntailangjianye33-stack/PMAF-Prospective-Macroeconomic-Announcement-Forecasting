# Eurostat 2026 Q4 — QuestionBank construction example

This repository contains two complete QuestionBanks for EU-related statistics scheduled for release in October–December 2026. A 30-target sample was drawn without replacement from 36 eligible release targets. The point bank reuses the same targets. These are 60 account representations of 30 targets across 17 release packages, not 60 independent observations.

| Artifact | Accounts | Response | Primary composite |
|---|---:|---|---|
| [Binary QB](banks/binary/README.md) | 30 | P(first-release value > fixed historical threshold) | Mean Brier score |
| [Point QB](banks/point/README.md) | 30 | Conditional mean of first-release numeric value | NMSE with frozen historical scales |

Both formats use identical archived 24-month histories, release targets, presentation times and information rules. Network access is disabled during a future response session; prediction markets and republications of their probabilities are prohibited. Forecasting, outcome collection and performance scoring have not been executed.

The scheduled times are tentative policy-derived plans and must be reconfirmed before execution. Local hashes and timestamps establish content correspondence only. No external timestamp or public registration is claimed.

## Construction manual

The construction guide presents the general PMAF workflow, with Eurostat examples at each relevant step. It covers preparation, experiment configuration, acquisition, screening, selection, account assembly, validation, a rebuild check from archived inputs, and formal freezing before forecasting begins. Concrete commands apply to the published Eurostat implementation; adapting it to other sources requires implementation changes.

| Documentation | English | 日本語 |
| --- | --- | --- |
| Task-based construction guide | [Read the guide](../../docs/QB_CONSTRUCTION_MANUAL_en.md) | [作成手順を読む](../../docs/QB_CONSTRUCTION_MANUAL_ja.md) |
| Configuration, file, and implementation reference | [Look up details](../../docs/QB_REFERENCE_en.md) | [設定・ファイル・実装の詳細](../../docs/QB_REFERENCE_ja.md) |

## Reproduce and verify

Use the Python version recorded in banks/binary/management/runtime.json and dependencies in requirements.txt.

```sh
python -B ../../scripts/verify_artifact.py ../..
python -B scripts/reproduce.py .
python -B banks/binary/scripts/validate.py banks/binary
python -B banks/point/scripts/validate_point.py --binary banks/binary --point banks/point
python -B scripts/verify_freeze.py banks/binary
python -B scripts/verify_freeze.py banks/point
```

Reproduction is offline, using archived responses. Every build-produced file is compared byte-for-byte by hash. Manifest checks cover post-build verification and freeze supplements. Raw acquisition failures and exploratory queries remain in the provenance records. The original local binary archive has not been modified; this distribution omits private manuscript reference copies and their local-path index, retaining all accounts, source responses, rules and build outputs.

## Publication and attribution

The artifact repository is [the PMAF repository](https://github.com/luntailangjianye33-stack/PMAF-Prospective-Macroeconomic-Announcement-Forecasting). Both Eurostat QBs and the bilingual construction manual are provided together. Original code is licensed under MIT; see [LICENSE](../../LICENSE). Cite the exact Git commit for the version used. No independent timestamp is claimed. The commit ID is obtained from Git rather than embedded in its own contents. Data and official metadata are attributed to Eurostat, with source URLs and retrieval provenance in each bank. No license to third-party source material is granted by this repository. Consult the linked original sources for their reuse terms.

## 日本語

二値確率版30口座と点予測版30口座の全文、過去データ、共通・個別規約、全候補・採否・乱数・原応答・再生成コードを収録する。両版は同じ30発表対象を共有する。論文では代表的口座と構築件数を示し、全件を本資料から参照する構成とした。工学的なQB作成マニュアルの日英両版も含め、両QBと同じ[PMAFリポジトリ](https://github.com/luntailangjianye33-stack/PMAF-Prospective-Macroeconomic-Announcement-Forecasting)に収録する。利用した版はGitコミットIDで指定する。独立したタイムスタンプの取得は主張しない。自作コードのライセンスはMITとし、第三者資料には元の利用条件を適用する。

[Representative paired accounts used in the paper](manuscript/paired_account_examples.md)

For exact byte-level binary regeneration, the example reproduction command uses management/build_input_config.json, which preserves the original JSON key order used in formatted strings. It has the same configuration values as global/config.json.

## Working directory and scope

Run the commands above from `examples/eurostat_2026q4/`. The shared guides give equivalent commands from the repository root. Store environments and new outputs outside the repository; adjust their relative paths accordingly. The banks are frozen construction artifacts. Do not fill their empty forecast or resolution fields with later results. Store execution records separately and reference the QB version, manifest hash, question ID, and run ID.

No forecasting runner, answer-reception service, browsing-history collector, or automatic Git push is implemented here. Manual, software-mediated, and AI-assisted execution are possible implementations of the protocol; see the [execution and record guide](../../docs/EXPERIMENT_RECORDS_en.md).

## Layout migration

The initial publication commit `34bee8d0622d4735da7ed28342fb8481e547529b` placed `banks/` at the repository root. This layout places the same bank files beneath this example directory. All bank-relative paths, bytes, manifests, and freeze records are preserved. Use the initial commit to reproduce the original layout. Documentation and the outer publication manifest have changed; exact verification results for this migration are in `layout_verification.json`.

この例は構築・検証の成果物です。凍結済み口座は上書きせず、回答・証拠・閲覧履歴・判定・得点は別の実験記録に保存します。現在のコードには予測実行や自動プッシュの機能はありません。[実行と記録のガイド](../../docs/EXPERIMENT_RECORDS_ja.md)を参照してください。旧版の提示予定には過去の日付が含まれるため、今から実際の予測実験を行う際は将来の対象と日程を設定した新しいQB版が必要です。
