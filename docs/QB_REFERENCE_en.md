# PMAF Configuration, Files, and Implementation Reference

Version: 0.2 / Updated: 2026-09-21

[Return to the construction guide](QB_CONSTRUCTION_MANUAL_en.md) · [日本語](QB_REFERENCE_ja.md)

Use this reference to look up configuration fields, files, and validation conditions while following the guide. Alongside general requirements, **Eurostat paths, values, and code constraints are provided as concrete examples**. Check implementation support before applying those paths or choices to another experiment.

- [Look up configuration items](#configuration)
- [Look up terms and file locations](#files)
- [Example: Acquire and interpret Eurostat responses](#acquisition)
- [Check eligibility and timing conditions](#eligibility)
- [Example: Inspect random-sampling records](#sampling)
- [Example: Inspect account files and numerical conventions](#accounts)
- [Check the scope of validation](#validation)
- [Manage freezing and subsequent records](#freeze-reference)
- [Example: Adapt the published code to another experiment](#implementation)
- [Example: Regeneration details and retained outputs](#retain-output)
- [Check publication contents and reuse terms](#publication)
- [Consult verification records and sources](#sources)

<a id="configuration"></a>
## 1. Look up configuration items

Record the following as concrete values or decision rules. The general configuration items in PMAF exceed the items supported by this distribution's code. Check the [implementation constraints](#implementation) before using new settings.

| Item | Decisions to record | Existing storage location |
| --- | --- | --- |
| Evaluation objective and participants | Which capability is measured, and for which people or systems | `objective` |
| Identification and administration | QB ID, configuration version, author, date, and reason for changes | `identity`, `configuration_history` |
| Periods | Experiment start and end, release window, and reference-period conditions | `time_design`, `collection_request` |
| Scope | Publisher, geographical area, statistical domain, dataset, dimensions, and classification versions | `collection_request`, `series` |
| Acquisition | Sources, queries, cutoff, enumeration, stopping and deduplication rules, and preservation | `collection_request` and acquisition records |
| Questions | Binary or point format, target vintage such as the first release, units, transformations, and threshold or target functional | `question_generation` |
| Timing | Lead time H from presentation to release, response duration D, and post-release processing allowance b | `time_design` |
| Eligibility | Mandatory conditions, evidence, PASS/FAIL/UNVERIFIED, and adjudication | `quality_and_eligibility` |
| Selection | Count N, sampling unit and method, candidate order, random-number implementation, and shortfall rules | `selection` |
| Provided materials | Required history, definitions, comparison values, vintages, and update policy | `materials_and_access` |
| Information conditions | Web access, prediction markets, others' forecasts, computational tools, and logging scope | `materials_and_access` |
| Resolution and scoring | Official evidence, vintage, retrieval deadline, boundary cases, metric, scale, and aggregation unit | `resolution_and_scoring` |
| Exceptions and freezing | Postponements, missing data, retrieval failures, violations, replacements, changes, and evidence of existence at a given time | `exceptions_and_records` |

The example uses scheduled releases in October–December 2026, EU27_2020 and EA21, six datasets, 30 questions sampled without replacement, H=336 hours, D=2 hours, b=24 hours, and 24 months of history. These are illustrative choices, not fixed values for PMAF generally.

Distinguish writing configuration values in JSON or YAML from defining a schema that validates those values. The current code reads JSON and cannot directly load YAML. The distribution also lacks a complete configuration schema; `account.schema.json` applies to generated accounts.

<a id="files"></a>
## 2. Look up terms and file locations

| Unit | Meaning | Eurostat construction example |
| --- | --- | --- |
| Experiment configuration | Concrete values and choices for scope, timing, question count, materials, scoring, and related conditions | `global/config.json` |
| Data schema | Structure, types, required fields, and value constraints for stored data | `global/account.schema.json` |
| Evaluation protocol | Conditions and rules for selection, presentation, resolution, scoring, and exceptions | Global and local rules; Sections 3 and 4 of the paper |
| Release package | One release record in the calendar | May cover multiple geographical areas or series |
| Release candidate set U | Release targets identified by series, geographical area, reference period, and release vintage | 36 targets obtained from 18 packages within the configured scope |
| Candidate question set P | Questions generated from release targets and templates | One question per target in this example |
| Eligible set C | Questions confirmed to satisfy mandatory conditions | 36 questions; the question-level sampling frame |
| Selected set Q | Questions selected from C | 30 questions |
| Question account | A unit linking one question to its materials, time and information conditions, and resolution rules | `accounts/<question_id>/` |
| QuestionBank | A managed collection of question accounts, global rules, indexes, and construction records | `banks/binary/` or `banks/point/` |

Distinguish a dataset code from a series. For example, `une_rt_m` alone does not identify one unemployment-rate series. Specify the dimension values as well, such as `freq=M`, `s_adj=SA`, `age=TOTAL`, `sex=T`, `unit=PC_ACT`, and `geo=EU27_2020`. Use the [Eurostat metadata](https://ec.europa.eu/eurostat/cache/metadata/en/une_rt_m_esms.htm) to check that the combination represents the intended target.

```text
repository/
├── README.md
├── requirements.txt
├── release_status.json
├── ARTIFACT_MANIFEST.json       Inventory for the distribution package
├── docs/
│   ├── QB_CONSTRUCTION_MANUAL_ja.md
│   ├── QB_CONSTRUCTION_MANUAL_en.md
│   ├── QB_REFERENCE_ja.md
│   └── QB_REFERENCE_en.md
├── scripts/
│   ├── reproduce.py
│   ├── verify_artifact.py
│   └── verify_freeze.py
├── manuscript/
│   └── paired_account_examples.md
└── banks/
    ├── binary/
    │   ├── global/              Global rules, configuration, account schema
    │   ├── accounts/<question_id>/
    │   │   ├── question.md
    │   │   ├── account.json
    │   │   ├── materials.md
    │   │   ├── local_rules.md
    │   │   └── data/history.csv
    │   ├── management/          Candidates, decisions, draws, raw responses, provenance
    │   ├── scripts/
    │   ├── manifest.json        Inventory of files covered by this QB's manifest
    │   └── freeze.json          Record referencing the manifest hash
    └── point/                  Point-forecast bank; same basic layout
```

Place global rules outside individual accounts but inside the QB. Specify what forecasters receive through the account's `materials` entries and the global rules. Do not distribute `management/` or other accounts indiscriminately. Keep the manual in `docs/`, outside the frozen QBs, so that documentation updates do not alter existing account hashes.

<a id="acquisition"></a>
## 3. Example: Acquire and interpret Eurostat responses

### Obtain schedules and numerical data from their respective sources

The Eurostat example uses the [official Release calendar](https://ec.europa.eu/eurostat/news/euro-indicators/release-calendar) for schedules and the statistical API and metadata for series definitions and historical values. It preserves responses from `https://ec.europa.eu/eurostat/o/calendars/eventsJson`, which supplies the public calendar interface. Do not assume this endpoint is a general-purpose API with a permanent service contract. Recheck its correspondence with the official interface and its response structure when using it.

The statistical API query below illustrates the query structure. It is not a URL that reproduces the original retrieval date.

```text
https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/une_rt_m
  ?lang=en&freq=M&s_adj=SA&age=TOTAL&sex=T&unit=PC_ACT
  &geo=EU27_2020&sinceTimePeriod=2024-01
```

Preserve each response as unprocessed bytes and place its acquisition record alongside it.

```text
raw/history_une_rt_m.json
raw/history_une_rt_m.json.provenance.json
```

The record should contain the final URL and query, request and retrieval times, HTTP status, Content-Type, response size, and SHA-256. Retain records of HTTP failures and responses without numerical data. HTTP 200 alone does not establish that values for the required series and periods are present.

### Extract numerical values

For JSON-stat responses from Eurostat's Statistics API, locate values using `id`, `size`, and each dimension's `category.index`. Do not infer positions from object display order or the appearance of labels. Preserve missing entries in `value` as missing rather than replacing them with zero, and retain annotations in `status`. Follow the [official JSON-stat specification](https://json-stat.org/format/).

The existing `build.py` assumes the object representations of `value` and `category.index` found in the archived responses. Add decoder support before using other array representations permitted by JSON-stat. `validate.py` rechecks historical values using an enumeration method separate from the builder's index calculation.

<a id="eligibility"></a>
## 4. Check eligibility and timing conditions

Apply a finite set of templates to each release target in U to obtain P. Review the mandatory items below. Follow the prespecified configuration for thresholds and history length.

| Check | Example of PASS | Example of failure or an unverified condition |
| --- | --- | --- |
| Scope | Matches the specified publisher, geographical area, and domain | Statistic or geographical area outside scope |
| Target identification | Dimensions, unit, adjustment, reference month, and release vintage are unambiguous | Unclear whether the target is a level or month-on-month change; another series with the same name |
| Timing | T=R−H, C=T+D, 0<D<H, t0≤T, and R+b≤t1 | Presentation before the experiment starts; outcome retrieval deadline after it ends |
| Planning for an unpublished target | Archived inputs exclude the target value, and materials are retrieved before presentation | Target value already included; its unpublished status at actual submission must be rechecked later |
| Materials and comparison values | Required same-series history and fixed threshold are available | Insufficient history, anchor in different units, or target value included in materials |
| Resolvability | Evidence identifies where and how to obtain the specified vintage and value | First-release value required, but only a latest-value API specified |
| Uniqueness | Unique question ID traceable to its source release | Different questions share an ID, or a reference cannot be traced |
| Additional point-forecast conditions | Target functional, units, admissible range, and positive finite scale are specified | Zero scale, infinite values, or a primary loss inconsistent with the requested conditional mean |

For each decision, record `question_id`, criterion ID and version, whether it is mandatory, decision, evidence, source, reviewer or code version, and check time. Exclude a question from C if any mandatory item remains unverified. Humans may judge suitability for the research objective, with reasons for acceptance or rejection recorded.

The existing binary code produces PASS/FAIL from Boolean conditions; it does not separately represent many unknown states as UNVERIFIED. Moreover, `resolution_defined` checks only that the source-location description is nonempty. Separately verify that the required first-release value can actually be extracted from official documents, using previously published documents of the same kind. A current PASS refers to the checks implemented during construction.

For timing, the archived version uses provisional values obtained by interpreting the “11 am CET” policy as local civil time in Europe/Luxembourg. Calendar fields `allDay` and `start` alone do not establish the exact actual release time. Convert local time to UTC using IANA time-zone information, and calculate H and D as elapsed time in UTC when daylight-saving boundaries are involved. See [Python zoneinfo](https://docs.python.org/3.13/library/zoneinfo.html).

<a id="sampling"></a>
## 5. Example: Inspect random-sampling records

Preserve C as the question-level sampling frame. For simple random sampling without replacement, record the candidate ID order, seed, Python and implementation versions, draw order, and final selected IDs. A seed alone is insufficient. See the [Python random specification](https://docs.python.org/3.13/library/random.html#random.sample).

```python
ordered_ids = sorted(eligible_question_ids)
k = min(requested_count, len(ordered_ids))
draw_order = random.Random(seed).sample(ordered_ids, k)
selected_ids = sorted(draw_order)
```

The example implements the configured shortfall rule: retain all eligible questions if fewer than requested are available. If using stratification, purposive selection, or another shortfall rule, implement the specified rule explicitly. Do not replace selected questions with more convenient ones after selection. Follow prespecified replacement or stopping rules when material preparation fails.

In the archived version, `management/selection.json` contains the order of 36 candidates, seed=20260912, draw order, 30 selected IDs, and the sampling-frame hash. The point-forecast version maps the IDs and inherits the same sample. The 60 accounts represent two formats of 30 release targets, not 60 independent targets.

<a id="accounts"></a>
## 6. Example: Inspect account files and numerical conventions

Prepare the following files for each account.

| File | Contents and checks |
| --- | --- |
| `question.md` | Japanese and English question text; target month, series, and submission format agree with `account.json` |
| `account.json` | ID, series key, reference month, timing, threshold or target functional, material references, and resolution and scoring conditions |
| `data/history.csv` | `period,value,status_flag`; required historical periods for the same series and geographical area |
| `materials.md` | Meaning, units, sources, retrieval time, vintage, transformations, and missing-data treatment |
| `local_rules.md` | Question-specific conditions that apply together with the global rules |

The existing accounts include 24 months of history. These values come from the snapshot retrieved during construction; they are not a collection of first-release values for each historical month. News, policy documents, and data for other indicators are not attached. Accounts contain dimension values, short definitions, and descriptions of materials rather than full copies of long official definition documents. If another task requires those materials, acquire and fix them as additional inputs.

The binary format requests the probability that the specified first-release value strictly exceeds a fixed threshold. Equality resolves to NO. The point format requests a numerical forecast of the conditional mean of the same first-release value. The most recent historical value remains contextual information in the point-forecast account.

The aggregate point-forecast metric in this example is NMSE: divide each forecast error by its prespecified scale s, square the result, and average across questions. MSE is also reported within each series–geographical-area group. Each s is the sample standard deviation of 24 historical values, with denominator 23 inside the square root; it is not recalculated from target values or submitted forecasts. For this example's percentage-valued series, values are expressed in percent, differences and s in percentage points, and MSE in squared percentage points.

Do not populate future submissions, outcomes, or scores during construction. Use null for unavailable values in binary `forecast.p_yes`, point `forecast.point_estimate`, and each format's outcome and score fields. Do not replace an unresolved outcome with NO or a score of zero.

<a id="validation"></a>
## 7. Check the scope of validation

1. **Structure:** Required fields, types, formats, and ranges, checked with JSON Schema.
2. **References:** Account IDs and directories, selected IDs and existing accounts, material paths, and references to global rules.
3. **Meaning and calculations:** Series and dimensions, units, periods, historical values, thresholds, H, D, b, and normalization scales.
4. **Sources:** Raw responses and SHA-256, document targets, and procedures for retrieving the required vintage.
5. **Counts:** Reconcile collected, out-of-scope, candidate, eligible, selected, failed, and unverified items.
6. **Correspondence between formats:** Confirm matching release targets, series, materials, and time and information conditions, with changes confined to format-specific rules.
7. **Prose:** Compare values and meanings across `question.md`, `account.json`, and global and local rules. Current automated checks do not validate every natural-language statement.

JSON Schema's `$ref` refers to another schema and applies it. Additional checks are needed to verify the existence of material files or agreement with IDs in other accounts. See the [official JSON Schema explanation](https://json-schema.org/understanding-json-schema/structuring).

Mark construction complete after all mandatory items have been checked. Record automated PASS results, independent content review, and the validity of an actual forecasting experiment separately. Identical code can reproduce identical errors, so byte-for-byte agreement does not substitute for content validation.

For a new QB, we recommend rebuilding it into a separate location from archived inputs using the same configuration, code, and dependency environment immediately after construction, before formal freezing and the start of forecasting, and checking agreement with the initial build. The comparison scope is specified in advance and distinguished from changing execution times, run logs, and freeze records added after construction. Discrepancies are resolved; changes to inputs, configuration, or code require a new check on the revised QB. Formal freezing and forecasting follow confirmation of agreement and content checks. Rebuilding uses archived inputs and does not retrieve updated source data. The same verification may also be performed after freezing, but need not wait until the experiment ends. This check evaluates the reproducibility of construction and is distinguished from using hashes to detect changes to frozen files and from reviewing the contents of questions and materials.

<a id="freeze-reference"></a>
## 8. Manage freezing and subsequent records

### Fix the scope of the freeze

Include accounts, provided materials, global and local rules, configuration, schemas, acceptance and sampling records, raw construction inputs, and code. Rerun the relevant checks if changes occur after validation. Ensure that file contents remain stable while they are read.

### Preserve the file inventory and content hashes

The procedure below follows this distribution's format. Do not reissue an existing version's manifest to conceal modifications.

```text
Enumerate and sort target files by relative path
  → Calculate each file's byte size and SHA-256
  → Store algorithm and files[{path,bytes,sha256}] in manifest.json
  → Calculate SHA-256 of the actual saved manifest.json bytes
  → Store that hash, version, operator, declared time, and check results in freeze.json
  → Recheck the inventory and hashes after saving
```

Exclude the manifest itself and its freeze record from that manifest's file inventory to avoid circular references. Identical UTF-8 text content can have different bytes and hashes because of line endings, whitespace, or JSON key order. Fix serialization, line endings, and encoding when byte-for-byte agreement is required. The existing `verify_freeze.py` verifies this distribution; it is not a CLI for generating a new freeze.

The file-inventory and checksum approach draws on [BagIt RFC 8493](https://www.rfc-editor.org/rfc/rfc8493). This layout does not claim full BagIt compliance.

### Provide evidence of when the version existed

Local clocks and hashes support checks of preserved content. To demonstrate to third parties that a version was fixed before presentation, associate its manifest digest or an equivalent digest with independent time evidence before the first presentation. A timestamp based on [RFC 3161](https://www.rfc-editor.org/rfc/rfc3161) is one option. The archived version has no external timestamp. Evidence obtained later does not retroactively establish an earlier existence time.

Append prediction, resolution, and scoring records outside the frozen version, linking them through QB ID, version, question ID, run ID, and manifest hash. Do not overwrite null fields in the original frozen accounts with experimental results. If private files are omitted for distribution, create a distribution version with a separate manifest and record the omissions and its relationship to the original version.

<a id="implementation"></a>
## 9. Example: Adapt the published code to another experiment

| Component | Constraint in the existing implementation | Required action for a new QB |
| --- | --- | --- |
| History extraction and validation in `build.py` | History length fixed at 24 months in code | Align configuration, extraction, checks, and explanatory text |
| Generated global rules and README | Text includes 336 hours, 2 hours, 24 hours, Q4, and related choices | Make generated prose agree with computed dates and times |
| `fetch.py` | Fixed calendar period; creates `raw/` beside the script | Explicitly set a new period and output location before running |
| `acquire.py` | Expects an adjacent `series.json`, which is absent at that location in the distribution | Prepare new acquisition inputs and destinations before running it; it is not ready to use unchanged |
| API response decoding | Depends on the JSON-stat representation in the archived example | Check support for response changes and missing-value representations |
| Eligibility states | Primarily Boolean decisions; full three-state handling is not implemented | Preserve reasons and stop or hold items with unknown mandatory conditions |
| Resolution procedure | Some checks only establish that a retrieval description exists | Add tests that extract target values from previously published documents |
| Point conversion and validation | Some parts assume 30 accounts, 36 candidates, and 24 historical values | Adapt counts, eligibility, units, ranges, and loss functions |
| Future experiment operation | Delivery, submission, outcome retrieval, and scoring are not implemented | Prepare separate operating procedures and records consistent with Section 4 of the paper |

Changing a configuration file alone does not establish that the output correctly implements different conditions. Align code, schemas, automated checks, question text, and global rules with the same experiment configuration. For each new version, check at acquisition and presentation that target values have not already been published.

The archived example retains the Japanese unemployment label “全年齢” (“all ages”). The official definition corresponding to `age=TOTAL` is ages 15–74, as explained in the paper. Preserve the original evidence, and align question wording with the official definition in any version used for an actual forecasting experiment. An experiment also cannot be started retroactively at a presentation time that has already passed. Select eligible future targets and schedules for a new run.

<a id="retain-output"></a>
## 10. Example: Regeneration details and retained outputs

### Match the environment

The construction environment is recorded in `banks/binary/management/runtime.json`.

| Component | Recorded version |
| --- | --- |
| Python | 3.13.9 |
| jsonschema | 4.25.0 |
| tzdata | 2025.2 |
| requests | 2.32.5 |

Use an environment with Python 3.13.9 and check `python --version`. The following PowerShell example creates a new environment. Run it from the repository root.

```powershell
python -m venv ../pmaf-qb-venv
& ../pmaf-qb-venv/Scripts/python.exe -m pip install -r requirements.txt
```

In subsequent commands, replace `python` with the executable in this environment. Installing packages requires network access; regeneration uses only archived responses. Store virtual environments, logs, and regeneration outputs outside the repository to avoid introducing extra files into the package inventory.

### Run the checks

Inspect the exit code and output of each command, and stop when a command fails. Do not use `python -O`: some checks in this implementation use `assert`, which optimization disables.

```powershell
python -B scripts/verify_artifact.py .
python -B scripts/reproduce.py .
python -B banks/binary/scripts/validate.py banks/binary
python -B banks/point/scripts/validate_point.py --binary banks/binary --point banks/point
python -B scripts/verify_freeze.py banks/binary
python -B scripts/verify_freeze.py banks/point
```

`-B` suppresses bytecode-cache writes. `reproduce.py` writes to temporary directories and removes those temporary outputs when it finishes. It does not overwrite the original QBs. Save any JSON verification output outside the QBs as well.

| Check | Expected result for this archived version |
| --- | --- |
| Binary regeneration | Identical paths and SHA-256 hashes for 207 generated files |
| Point-forecast regeneration | Identical paths and SHA-256 hashes for 211 generated files |
| Binary validation | PASS, 540 checks |
| Point-forecast validation | PASS, 574 checks |
| Binary distribution manifest | Contents of 221 files verified |
| Point-forecast distribution manifest | Contents of 216 files verified |

These counts apply to this archived version. Generated-file counts cover builder outputs; manifest counts also include records added after construction, such as verification results. Distribution copies omit private manuscript-reference files and retain additional regeneration records. Establish the relationship to the original archive using `banks/binary/management/distribution.json` and the actual manifest inventories, rather than file counts alone.

Regeneration reruns construction from archived source responses. It does not retrieve past responses by revisiting the same URLs. Eurostat's standard API returns the latest dataset, so subsequent retrievals may include revised values or schedule changes. See the [official Eurostat API introduction](https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-introduction).

### Retain the regenerated outputs

The following PowerShell example saves construction outputs to new directories. Run it only when `../pmaf-replay-inputs`, `../pmaf-rebuilt-binary`, and `../pmaf-rebuilt-point` do not already exist.

```powershell
New-Item -ItemType Directory -Path ../pmaf-replay-inputs
Copy-Item -LiteralPath banks/binary/management/build_input_config.json -Destination ../pmaf-replay-inputs/config.json
Copy-Item -LiteralPath banks/binary/management/raw -Destination ../pmaf-replay-inputs/raw -Recurse
python -B banks/binary/scripts/build.py --inputs ../pmaf-replay-inputs --out ../pmaf-rebuilt-binary
python -B banks/binary/scripts/validate.py ../pmaf-rebuilt-binary
python -B banks/point/scripts/build_point.py --binary banks/binary --settings banks/point/global/point_settings.json --out ../pmaf-rebuilt-point
python -B banks/point/scripts/validate_point.py --binary banks/binary --point ../pmaf-rebuilt-point
```

Use `management/build_input_config.json` when regenerating the binary bank for byte-for-byte comparison. Its settings equal those in `global/config.json`, but it retains the original JSON key order. In the existing builder, key order affects JSON representations embedded in prose. The point-forecast bank records its parent QB's manifest hash, so this example uses the original distributed binary bank as input. Using an intermediate rebuilt bank without its manifest would not reproduce the same parent-version record.

New construction outputs do not include supplementary freeze and verification files added after construction. To preserve or distribute them as an independent new version, carry out [the freezing procedure](#freeze-reference) separately.

<a id="publication"></a>
## 11. Check publication contents and reuse terms

Make the following accessible from the same release of the same repository:

- All accounts, historical CSV files, configurations, and rules for both forecast formats.
- Raw responses, acquisition records, all candidates and decisions, draw orders, and seeds.
- Construction, validation, and regeneration code, with dependency specifications.
- Japanese and English versions of this manual and the paired examples presented in the paper.
- Each QB's manifest and freeze record, and the distribution-package manifest.

Use the [PMAF repository](https://github.com/luntailangjianye33-stack/PMAF-Prospective-Macroeconomic-Announcement-Forecasting). Record the release tag and commit ID upon publication and align the paper's artifact reference with that version. If a DOI is obtained, record its correspondence to the same version. [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases) and [CITATION.cff](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files) support distribution of fixed versions and provision of citation information.

The author has selected MIT for the original code. The LICENSE, including the copyright notice, is included at the repository root. Apply the original terms to third-party materials such as Eurostat data; do not describe the entire collection as covered by MIT. Check distribution contents for API keys, private manuscripts, personal absolute paths, and unintended execution logs.

Changes to the manual, README, or other documentation affect the outer `ARTIFACT_MANIFEST.json`. Review the publication candidate, update that outer inventory, and verify the package again. Do not modify frozen `banks/*/manifest.json` or account files to accommodate documentation updates.

<a id="sources"></a>
## 12. Consult verification records and sources

The distribution code, configurations, series keys, provenance, schemas, and manifests were inspected on 2026-09-20. Results from the [regeneration and validation commands](#retain-output) are recorded in `QB_MANUAL_VERIFICATION_20260920.json` in the same `docs/` directory. This record does not document acquisition for a new period, forecasting, or scoring.

The web sources were consulted on 2026-09-20. They include Eurostat's official API, calendar, and series metadata; JSON-stat; JSON Schema; Python's random-number and time-zone documentation; RFC 8493 and RFC 3161; and GitHub documentation on releases and citations. Distinguish requirements established by these specifications from procedures chosen for PMAF and constraints of this particular implementation.

### Editorial approach

The task-based structure, with prerequisites, actions, and results presented together, draws on [Apple support](https://support.apple.com/ja-jp/104984), [an AWS tutorial](https://docs.aws.amazon.com/AmazonS3/latest/userguide/tutorial-s3-mpu-additional-checksums.html), [Google's procedure-writing guide](https://developers.google.com/style/procedures), and [Microsoft's procedure-writing guide](https://learn.microsoft.com/en-us/style-guide/procedures-instructions/writing-step-by-step-instructions), consulted on 2026-09-21.
