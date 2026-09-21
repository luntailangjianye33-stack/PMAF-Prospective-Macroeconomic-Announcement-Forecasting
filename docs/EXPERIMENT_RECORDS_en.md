# Operating PMAF and preserving experiment records

[日本語](EXPERIMENT_RECORDS_ja.md) · [QB construction guide](QB_CONSTRUCTION_MANUAL_en.md) · [Eurostat example](../examples/eurostat_2026q4/README.md)

This guide explains how to preserve a frozen QB and records produced during execution and after publication. PMAF permits manual, software-mediated, AI-assisted, and combined operation. Git-based version control is recommended, but no product, storage format, automated execution method, automatic commit/push mechanism, or fixed update frequency is prescribed.

## 1. Separate methodological requirements from implementation choices

| Methodological requirement | Possible implementation |
| --- | --- |
| Fix QB contents and version before presentation and identify the version used | Content inventory, version identifier, manifest, SHA-256, Git commit |
| Separate frozen inputs from subsequent records | Separate directories, database areas, or repositories |
| Link each response to the question, QB version, forecaster, run, and receipt time | Reception ledger, electronic form, API receipt record |
| Preserve evidence needed to assess information-condition compliance | Distribution records, observer records, permitted browser/tool histories, acquired materials |
| Retain original contents, correction reasons, operators, and times | Correction ledger retaining old versions, appended corrections, Git history |
| Enable verification of construction, resolution, and scoring from saved materials | Source and decision checks, code reruns, independent resolution and score recalculation |

Different methods need not provide equally strong evidence. Before execution, specify the required records, acquisition methods, storage locations, recording times, and treatment of missing evidence. Missing required evidence remains unverified; the mere presence of a record does not establish compliance.

## 2. Fix the QB and verify the version actually presented

After construction and content checks, reverify using a method appropriate to construction. For programmatic construction, rebuilding into a separate location from archived inputs with the same configuration, code, and dependency environment and comparing the prespecified scope is recommended. Perform this immediately after construction, before formal freezing and forecasting. For manual construction, preserve sources, procedures, settings, and selection decisions so the work can be reverified.

Freeze the contents and version and identify them in the execution record. If a manifest is used, retain its scope and hash and compare the actual presentation materials with the corresponding frozen materials. If materials are transformed for presentation, record the transformation and its relationship to the presented output. Corrections to the QB create a new version while retaining the original.

Agreement after rerunning code checks reproducibility of construction; comparison against frozen hashes checks correspondence of stored contents. Retrieving updated source data later is distinct from rebuilding from archived inputs.

## 3. Store submissions and subsequent records separately

The following is an illustrative layout, not an implemented runner or mandatory directory specification.

```text
experiment/
├── questionbanks/qb_v1/      Fixed questions, materials, rules, and version records
├── runs/run_001/             Presentation, receipts, evidence, access history, exceptions
└── evaluation/run_001/       Published sources, resolution, scores, summaries, corrections
```

Do not populate empty forecast or outcome fields in frozen accounts later. Subsequent records reference the QB identifier and version, question ID, run ID, and submission ID, plus the manifest hash when one is used. They may be in the same repository or a separate storage location.

| Record | Contents to preserve |
| --- | --- |
| Execution identity | QB, question, forecaster/system, and run identifiers and versions; applicable conditions; submission destination |
| Presentation and receipt | Identifiers for supplied materials, actual availability/receipt times, measurement locations, and supporting evidence |
| Submission receipt | Original response, probability or point value, submission ID, receiver-side time, format checks, and link to the selected submission |
| Evidence and information use | Explanations/evidence required by the rules, sources, acquisition times, archived materials or content identifiers, required browsing/operation records |
| Exceptions and corrections | Non-submission, failures, suspected violations, original and corrected records, reasons, operators, and decision times |
| Resolution and scoring | Sources for the designated vintage, extracted outcome, resolver or code version, relevant submission, scoring rule/score, and end-of-period status |

Corrections append new records while retaining originals. Later resolution or score recalculation also preserves original results and reasons for change. Adding responses or scores normally changes the repository's commit ID. Verify the fixed QB scope and each finalized version of subsequent records separately.

## 4. Manual examples and proposals for automation

The right-hand column illustrates possible future implementations. Automatic Git commits and pushes are a possible future implementation that may help preserve and trace records. They are not implemented in this artifact, and their benefits have not been evaluated.

| Stage | Manual example | Software/AI-assisted example |
| --- | --- | --- |
| Presentation | An operator distributes the designated materials and records distribution | A distribution process checks the QB version and records contents and time |
| Submission receipt | A receiver links the original answer and receipt time to a ledger | A reception service stores original submissions and receipt times |
| Information use | Supplied materials and observer records are retained | Acquisition and operation records are obtained from permitted tools |
| Storage | An operator saves and checks records at specified milestones | Records are saved automatically and optionally committed and transmitted |

Distinguish answer receipt from transfer to storage. Specify retention, retransmission, and missing-record checks for transfer failures in advance; do not substitute transfer completion time for answer receipt time.

## 5. Recommendations when using Git

Use Git to identify versions, inspect differences, and access earlier records. Record the full commit ID of the QB used, leave its frozen files unchanged, and add subsequent records separately. The experimenter chooses commit and transmission milestones. Automatically pushing after each answer is a future proposal, not a requirement.

Restrict history rewriting/deletion and replicate records to remote storage. Live answers need not be sent to a public repository; align access to stored records with information conditions to avoid disclosure to other forecasters. Git does not automatically record uncommitted changes or actual browsing.

Git commit dates can be set by the user, so assess submission timing from reception evidence. Public evaluations requiring independent time evidence can combine records with external timestamps. Hashes, commits, or signatures alone do not establish scientific correctness, submission time, or continuous absence of changes throughout execution.

<a id="timing-exceptions"></a>
## 6. Handle departures from timing conditions

**Decide before the experiment:** In the evaluation protocol and experiment configuration, specify tolerances for presentation and publication timing and actual lead time, resolution and scoring deadlines, primary-analysis inclusion rules, and how to determine the common question set for comparisons. Fix these before collecting forecasts; do not relax them after inspecting forecasts or scores.

The alignment of objectives with events arising during a study and the distinction between primary and supplementary analyses draw on [ICH E9(R1), 2019, Sections A.2 and A.5.2–A.5.3](https://database.ich.org/sites/default/files/E9-R1_Step4_Guideline_2019_1203.pdf). That guideline concerns treatment-effect estimation. The forecast-evaluation inclusion rules below are proposed PMAF operating policy.

| Situation | Primary analysis and records |
| --- | --- |
| Publication shifts within prespecified tolerances | Include the question if prospective status, information conditions, other eligibility criteria, and evaluation deadlines also hold. Retain planned and actual times and their differences. |
| A postponement or other change breaches timing conditions | Exclude the question from primary analysis under the original conditions; retain the question, original submissions, conditions, and reasons. Report scoring after resolution as supplementary evaluation. |
| The outcome remains unavailable at the evaluation deadline | Preserve an unresolved status; do not impute NO, an incorrect forecast, or a provisional score. Later scoring does not retrospectively change end-of-period status or the primary analysis. |
| Early publication makes the target value public before submission | Exclude affected submissions from prospective evaluation of that value. For pre-publication submissions, also check actual timing conditions and comparison-set rules. |
| Only one forecaster misses the submission deadline | Exclude that submission from primary scoring and report its status for that forecaster. Do not automatically remove the entire question; apply prespecified comparison-set rules. |

**Follow this sequence:** Preserve source evidence, planned and measured times, and their basis. Distinguish question-level states from each forecaster's submission status. Hold matters that cannot be verified, and retain the rule-based decision, reason, reviewer, and decision time. Hold affected cases not covered by existing rules, document their handling, and identify any unplanned analysis. Append these records separately without modifying the frozen QB.

**Report:** Alongside scores and scored-question counts, provide initial, unresolved, and excluded question counts, reason-specific counts, forecaster-specific submission status, and all denominators. Identify overlapping reasons without counting them as independent questions. Apply the common-set rule to comparisons; any additional forecaster-specific scores identify their own sets and counts.

Compare the geographical and statistical-domain composition of included and excluded questions. Limit interpretation of primary scores to the questions and conditions that could be scored. Supplementary evaluation including later-resolved questions or different timing conditions identifies its set, actual timing conditions, and reporting cutoff. Exclusion is not assumed to guarantee unbiased evaluation.

This guidance helps specify rules for future experiments. It does not change the published Eurostat example's frozen rules or establish that exception handling or forecasting has been executed or validated in that example. If different rules are adopted, fix a new version before forecasting begins.

## 7. Current Eurostat construction example

`examples/eurostat_2026q4/` contains frozen banks, source materials, and construction/validation code. It does not implement forecast execution, answer reception, browsing-history collection, automated outcome acquisition/scoring, or automatic push. Before conducting an actual experiment, recheck target and schedule eligibility and provide a separate method for preserving execution records.

## Technical sources

- [Git: recording changes and snapshots](https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository)
- [Git: commit information and dates](https://git-scm.com/docs/git-commit)
- [GitHub: protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [RFC 3161: timestamps](https://www.rfc-editor.org/rfc/rfc3161.html)

These sources support implementation choices. GitHub and RFC 3161 are not mandatory for every PMAF implementation.
