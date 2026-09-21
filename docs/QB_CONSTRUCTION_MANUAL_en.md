# Create a QuestionBank with PMAF

Version: 0.4 / Updated: 2026-09-21

[日本語](QB_CONSTRUCTION_MANUAL_ja.md) · [Configuration, files, and implementation reference](QB_REFERENCE_en.md)

This guide explains how to configure an experiment, select questions from scheduled economic releases, and attach materials and rules to create a QuestionBank (QB). The completed QB contains questions, materials for forecasters, resolution rules, and construction records.

Choose geographical areas, statistical agencies, periods, and question counts to suit your evaluation objective. **Sections labeled “Example: Eurostat” describe the published construction example and its code.** Those choices are not general PMAF requirements.

**Sequence for a new QB:** Construct and validate the QB → reverify using a method appropriate to its construction → formally freeze → begin forecasting. For programmatic construction, a rebuild check immediately after construction and before forecasting is recommended.

**Choose an operating method:** Manual, software-mediated, AI-assisted, and combined operation are supported. Git-based version control and rebuild checks for programmatically constructed QBs are recommended options. Specific formats, automated execution, and automatic commits or pushes are not mandatory. Fix the QB version, link records, retain corrections, and preserve the required evidence using suitable methods. See the [execution and record guide](EXPERIMENT_RECORDS_en.md). Automatic Git commits and pushes are a possible future implementation that may help preserve and trace records. They are not implemented in this artifact, and their benefits have not been evaluated.

| Your task | Start here |
| --- | --- |
| Create a new QB | Follow the guide from [1. Prepare](#prepare) |
| Rebuild a QB from archived inputs | [7. Rebuild and check agreement](#regenerate) |
| Look up configuration items or files | [Configuration, files, and implementation reference](QB_REFERENCE_en.md) |
| Resolve an error or an unverified condition | [9. Troubleshoot](#troubleshoot) |

<a id="prepare"></a>
## 1. Prepare to create a QB

**Objective:** Establish the QB's purpose and identify the materials and implementation you will use.

1. Define the capability and participants to evaluate. These might be AI systems or human forecasters predicting economic statistics.
2. Identify sources for release schedules, statistical values, and definitions. Record the versions of the evaluation protocol and data schemas you will use.
3. Prepare a working directory and a location for source materials. Keep any existing frozen version in a separate location.
4. Assign responsibility and methods for collection, screening, and selection. You can combine manual collection, processing by AI or programs, and searches of databases made publicly available by economic-statistics institutions or private companies. Record the operator or implementation version and the basis for decisions.

**Check completion:** The evaluation objective, applicable rules, sources, responsibilities, and storage locations are specified.

**Example: Eurostat**

The published code constructs, validates, and regenerates QBs for selected Eurostat statistics. Applying it to other geographical areas or agencies requires changes to acquisition, generated text, and other components. Check the [implementation constraints](QB_REFERENCE_en.md#implementation). The code does not automate forecast delivery, submission, outcome collection, or scoring in an actual experiment.

<a id="configure"></a>
## 2. Configure the experiment

**Objective:** Decide what to collect and which conditions questions must satisfy before processing begins.

1. Record the evaluation subjects, geographical areas, statistical domains, publishers, experiment period, and release window in a configuration file or table.
2. Specify binary-probabilistic or point forecasting, the question count, lead time from presentation to release, response duration, and permitted materials and information sources.
3. Define eligibility criteria, selection and shortfall rules, outcome vintage, scoring, and exception handling. See the [configuration checklist](QB_REFERENCE_en.md#configuration).
4. Assign an ID and version to the configuration. Fix collection conditions before acquisition, and fix screening and selection rules before their respective operations. Record subsequent changes and rerun affected operations.

**Check completion:** Required items have concrete values or decision rules. Choices conform to the evaluation protocol. If a schema is available for the configuration, the configuration passes its checks.

**Example: Eurostat**

The example uses scheduled releases in October–December 2026, EU27_2020 and EA21, six datasets, 30 questions, a lead time of 336 hours, a response duration of 2 hours, and a post-release processing allowance of 24 hours. Settings are in `examples/eurostat_2026q4/banks/binary/global/config.json`. The implementation reads JSON; it does not directly load YAML or provide a complete schema for the entire configuration.

Fix timing tolerances, evaluation deadlines, primary-analysis inclusion rules, and comparison-set rules before collecting forecasts. Assess postponements against those conditions rather than excluding every postponed release. See [Handle departures from timing conditions](EXPERIMENT_RECORDS_en.md#timing-exceptions) for processing and reporting guidance.

<a id="collect"></a>
## 3. Collect release schedules and statistical data

**Before you begin:** Have the collection conditions, databases and release calendars made publicly available by economic-statistics institutions or private companies, statistical definitions, and storage locations ready.

Examples of databases and release calendars made publicly available by economic-statistics institutions or private companies include:

| Source | Examples of information available |
| --- | --- |
| [Eurostat database](https://ec.europa.eu/eurostat/web/main/data/database) | EU-related statistical values, series definitions, and metadata. Check scheduled releases separately in the official Release calendar. |
| [World Bank Open Data](https://data.worldbank.org/) | Economic and development indicators and historical observations for individual countries. Also verify the publication schedule before selecting a statistic as a forecasting target. |
| [Trading Economics economic calendar](https://tradingeconomics.com/calendar) | Scheduled economic-indicator releases for multiple countries, published by a private company. Cross-check selected releases against materials from the original publishing institution. |

Verify the availability of statistical values and release schedules separately. Public access to a webpage does not imply free API access or unrestricted data redistribution. Check the service's conditions for retrieval, storage, and redistribution.

1. Retrieve scheduled releases for the specified agencies, geographical areas, and period. Preserve the query conditions, retrieval times, and raw responses.
2. Identify the series, geographical area, reference period, unit, adjustment, and target vintage for each release. Expand releases containing multiple targets into individual targets.
3. Remove duplicate release targets and record which record you retain and why. Preserve schedule changes as the history of the same target.
4. Acquire the required historical values and definitions. Preserve unprocessed content with its URL, query, retrieval time, response status, byte size, and SHA-256.

**Check completion:** Every target in release candidate set U is traceable to source materials. Record collection scope, out-of-scope records, failed retrievals, and unverified coverage. Claiming coverage of all statistics in a geographical area requires separate supporting evidence.

**Example: Eurostat**

Of 55 release packages archived from the [official Release calendar](https://ec.europa.eu/eurostat/news/euro-indicators/release-calendar), 18 were within scope. Expanding them across two geographical areas produced 36 targets; 37 packages were outside scope. Numerical data came from the statistical API. Queries specify dimensions such as age, sex, unit, and geographical area in addition to a dataset name such as `une_rt_m`. See [acquisition records and JSON-stat](QB_REFERENCE_en.md#acquisition).

<a id="screen"></a>
## 4. Screen question eligibility

**Before you begin:** Have release candidate set U, question templates, eligibility criteria, and supporting materials ready.

1. Apply the prespecified finite set of templates to each release target to obtain candidate question set P.
2. Check the following items for each question. Record decisions as `PASS`, `FAIL`, or `UNVERIFIED`.

| Check | Required for acceptance |
| --- | --- |
| Scope | Within the specified agencies, geographical areas, and statistical domains |
| Question meaning | Clear series, unit, reference period, release vintage, and comparison condition or point-forecast target functional |
| Timing | Planned presentation, submission deadline, release, and outcome retrieval satisfy experiment conditions |
| Unpublished target | Materials exclude the target value; a procedure checks that the value is unpublished at forecasting time |
| Provided materials | Required history, comparison values, and definitions can be prepared |
| Resolution | The location and method for extracting the target from the specified vintage are supported by evidence |
| IDs and references | Unique question ID linked to its source release and materials |
| Point-forecast conditions | Target functional and loss are consistent; any normalization scale is positive and finite |

3. Attach the criterion version, mandatory status, source, evidence, reviewer or code version, and check time to each decision.
4. Include questions in eligible set C only when every mandatory condition is `PASS`. Recheck items that require completed materials before freezing the QB.

**Check completion:** Each acceptance or rejection has an explanation. Questions with unverified mandatory conditions are held. Check unpublished status again during subsequent forecast execution.

**Example: Eurostat**

The 36 questions passed the checks implemented during construction. The current code primarily uses Boolean decisions and does not fully implement three-state handling. `resolution_defined` checks whether a source-location description is nonempty. Separately test extraction of the required first-release values using previously published documents of the same kind. Some release times are provisional and require confirmation before an actual experiment. See [timing and validation constraints](QB_REFERENCE_en.md#implementation).

<a id="select"></a>
## 5. Select questions

**Before you begin:** Have eligible set C, the required count, and the prespecified selection, shortfall, and replacement rules ready.

1. Preserve the list of eligible question IDs as the set from which to select.
2. Apply the configured method, such as retaining all questions, random sampling, stratified sampling, or purposive selection. For purposive selection, record how decisions relate to the capability being measured.
3. For random sampling, record the fixed candidate order, sampling unit, random-number generator and implementation versions, seed, draw order, and selected IDs.
4. Apply the prespecified rules if too few candidates are available or material preparation fails. Record changes in count, replacements, or stopping decisions.

**Check completion:** Selected set Q matches the selection records. There are no duplicate targets or substitutions based on observed outcomes.

**Example: Eurostat**

The example sampled 30 of 36 questions without replacement, using seed 20260912 and candidates sorted by ID. The shortfall rule was to retain all eligible questions. The point-forecast bank inherited the same 30 targets. Its accounts and those of the binary bank provide two formats of 30 targets, totaling 60 accounts. See the [sampling example](QB_REFERENCE_en.md#sampling).

<a id="assemble"></a>
## 6. Attach materials and rules to questions

**Objective:** Assemble what forecasters receive and the conditions used to evaluate each question.

1. Write the target series, reference period, value or event to forecast, and submission format in the question text.
2. Acquire and prepare required historical data, comparison values, definitions, and related materials. Link the source materials, processed inputs, transformations, and vintages.
3. Add presentation time, response duration, permitted access, resolution criteria, and scoring conditions. Check for conflicts between global and local rules.
4. Store each question and its associated materials as one question account. Assemble the accounts into a QB with global rules, an index, and construction records.
5. Specify what forecasters receive. Leave future predictions, outcomes, and scores unavailable during construction.

**Check completion:** Each account references the necessary materials and rules, and its wording agrees with its configuration. Global rules are outside individual accounts but inside the QB.

**Example: Eurostat**

Each account contains `question.md`, `account.json`, `materials.md`, `local_rules.md`, and `data/history.csv`. The 24-month history uses the vintage retrieved at construction, not the first release of each historical month. News, policy documents, other indicators, and full copies of long definition documents are not attached.

The example disables network access during forecasting and prohibits prediction markets and republications of their probabilities. These are the information conditions chosen for this example.

The binary format asks for the probability that the first-release value strictly exceeds a fixed threshold; equality resolves to NO. The point format asks for the conditional mean of the same first-release value. Its aggregate metric is NMSE using fixed historical scales; MSE applies within each series–geographical-area group. See [account files and numerical conventions](QB_REFERENCE_en.md#accounts).

<a id="regenerate"></a>
## 7. Rebuild the QB from archived inputs and check agreement

**Scope:** Rerunning code is recommended for programmatically constructed QBs. For manual construction, retain source materials, settings, construction procedures, and selection decisions so that others can trace and reverify the work. The commands below apply to the Eurostat implementation.

**When to do this:** When a rebuild check is adopted, perform it immediately after constructing a new QB, before its formal freeze and the start of forecasting. Check early so that defects can be corrected; do not wait for the experiment to end.

**Objective:** Rebuild (regenerate) the QB from archived inputs using the same configuration, code, and dependency environment, and compare it with the initial build. This does not include retrieving updated data from the sources.

**Before you begin:** Have the source snapshots, construction configuration and code, dependency environment, reference QB, and a new output location ready.

1. Preserve the initial QB as the reference and obtain the inputs, configuration, code, and execution environment used to construct it. For a new build, the reference does not need to be formally frozen yet.
2. Build into a location separate from the original QB. Retain the archived inputs instead of replacing them with newly retrieved data.
3. Specify the files to compare in advance, then compare the rebuilt file inventory and hashes with the initial build. Keep changing execution times, run logs, and freeze records added after construction separate from build outputs, and document the comparison scope. Also run structure, reference, and calculation checks.
4. Record the comparison scope, differences, and environment. Resolve discrepancies; if inputs, configuration, or code change, repeat the check on the revised QB. See [Troubleshoot](#troubleshoot).
5. Once agreement is confirmed where a rebuild check is adopted, and content checks are complete, proceed to [8. Validate and freeze the QuestionBank](#freeze). Begin forecasting only after the formal freeze.

**Check completion:** Construction outputs agree under the specified comparison method. For byte-for-byte agreement, preserve line endings, encoding, and JSON key order as well. Check reproducibility and content correctness separately.

### Example: Rebuild and verify the published Eurostat banks

The following example allows a third party to verify QBs that have already been published and frozen. This check can be performed later. When constructing a new QB, follow the sequence above and check it immediately after construction, before its formal freeze.

This example uses PowerShell on Windows. Install Git and Python 3.13.9 first. Initial retrieval and environment setup use the network; regeneration is offline. Start in a location where you can create new directories.

Do not use `python -O`, because validation uses `assert`. `-B` suppresses bytecode caches. Keep environments, logs, and additional outputs outside the distribution directory.

1. Retrieve the public repository and record the displayed commit ID. Check out that ID to obtain the same version later. Initial publication commit 34bee8d uses a different layout; follow the instructions stored in that version when using it.

   ```powershell
   git clone https://github.com/luntailangjianye33-stack/PMAF-Prospective-Macroeconomic-Announcement-Forecasting.git pmaf-example
   Set-Location pmaf-example
   git rev-parse HEAD
   ```

2. Check that `python --version` reports `Python 3.13.9`, then create a dedicated environment. Use a new location for `../pmaf-qb-venv`.

   ```powershell
   python --version
   python -m venv ../pmaf-qb-venv
   & ../pmaf-qb-venv/Scripts/python.exe -m pip install -r examples/eurostat_2026q4/requirements.txt
   ```

3. Check that the distribution matches its inventory. Perform subsequent operations from the repository directory.

   ```powershell
   & ../pmaf-qb-venv/Scripts/python.exe -B scripts/verify_artifact.py .
   ```

   Continue when `PASS` appears and the exit code is 0. Stop if this check fails.

4. Regenerate both QBs from archived inputs.

   ```powershell
   & ../pmaf-qb-venv/Scripts/python.exe -B examples/eurostat_2026q4/scripts/reproduce.py examples/eurostat_2026q4
   ```

   Check that `status` is `PASS`, `binary_generated_files_identical` is 207, and `point_generated_files_identical` is 211. Generated files are placed in temporary directories and removed when the operation finishes. The original QBs remain unchanged.

5. Validate contents and freeze records. Run each line in order; if a command fails, investigate before proceeding.

   ```powershell
   & ../pmaf-qb-venv/Scripts/python.exe -B examples/eurostat_2026q4/banks/binary/scripts/validate.py examples/eurostat_2026q4/banks/binary
   & ../pmaf-qb-venv/Scripts/python.exe -B examples/eurostat_2026q4/banks/point/scripts/validate_point.py --binary examples/eurostat_2026q4/banks/binary --point examples/eurostat_2026q4/banks/point
   & ../pmaf-qb-venv/Scripts/python.exe -B examples/eurostat_2026q4/scripts/verify_freeze.py examples/eurostat_2026q4/banks/binary
   & ../pmaf-qb-venv/Scripts/python.exe -B examples/eurostat_2026q4/scripts/verify_freeze.py examples/eurostat_2026q4/banks/point
   ```

   All checks should pass. This archived version has 540 binary and 574 point validation checks, and 221 and 216 files covered by the respective freeze inventories. These inventories cover a different scope from generated-file counts.

See [retaining generated files](QB_REFERENCE_en.md#retain-output) and [implementation support](QB_REFERENCE_en.md#implementation) for further details.

<a id="freeze"></a>
## 8. Validate and freeze the QuestionBank

**Implementation example:** The manifest and SHA-256 procedure below is a recommended implementation of verifiable advance fixation. If another method is used, specify how contents, versions, changes, and any required time evidence will be checked.

**Before you begin:** Have the QB with completed materials, eligibility records, validation criteria, the proposed freeze inventory, and the results of the chosen reverification method (such as [the rebuild comparison](#regenerate) for programmatic construction) ready.

If inputs, configuration, code, or construction outputs change after the rebuild check, repeat the check on the revised QB before freezing. Hash verification at this stage checks whether the stored QB retains the contents recorded at freezing. The preceding rebuild check executes the construction process to determine whether it produces the same artifacts.

1. Check required fields, types, ranges, IDs, file references, series, units, time calculations, material vintages, sources, and stage counts. Compare question wording with the rules as well.
2. Resolve failures of mandatory conditions. Record automated checks separately from human content review.
3. Fix the scope to freeze: accounts, materials, rules, configuration, schemas, acceptance and sampling records, source inputs, construction code, and other required files. Manage subsequent changes as new versions.
4. With file contents stable, save an inventory of relative paths, byte sizes, and SHA-256 hashes. The distributed example names this file `manifest.json`.
5. Save the hash of the actual manifest, version, operator, declared time, and check results in a freeze record. Exclude the manifest itself and the freeze record from that manifest's inventory.
6. Recheck the saved inventory and hashes. If you need evidence that a version existed before presentation, obtain independent time evidence before the first presentation.

**Check completion:** A QB satisfying the mandatory conditions can be identified, and its inventory, contents, and version can be reverified. Local hashes and declared times alone do not prove past existence to third parties. See [freezing and publication](QB_REFERENCE_en.md#freeze-reference).

**Example: Eurostat**

Each QB has `manifest.json` and `freeze.json`; the distribution package has `ARTIFACT_MANIFEST.json`. Accounts are within the freeze scope, while manuals are in the outer `docs/` directory. No external timestamp was obtained. Store future prediction, resolution, and scoring records separately, referencing the QB version and question ID rather than overwriting the original accounts.

<a id="troubleshoot"></a>
## 9. Troubleshoot

| Symptom | Check or next action |
| --- | --- |
| Release time or target series cannot be identified | Consult official materials. Hold the item as unverified if a mandatory condition remains unknown |
| HTTP 200 but no numerical values | Check dimensions and reference periods. Preserve missing values rather than filling with zero |
| Too few eligible questions | Apply the prespecified shortfall rule and report the actual count. Do not start an experiment with zero questions |
| Required materials or comparison values are unavailable | Hold acceptance and apply the replacement, scope-reduction, or stopping rule |
| Point-forecast scale is zero or nonfinite, or history is insufficient | Check the calculation and source data. Stop processing and preserve the relationship to the selected sample |
| Schema validation passes but materials cannot be found | Check material paths, file existence, and ID correspondence separately |
| File hashes differ | Compare inputs, code, dependencies, line endings, JSON ordering, and additional files. Diagnose the cause before replacing a manifest |
| API values differ on later retrieval | Investigate revisions and retain the construction vintage. Obtain outcomes from the designated release vintage |
| Output location already exists | Choose a new location. Preserve existing frozen versions |

For support or verification records, include the QB ID and version, question ID, operation, error, and execution environment. Exclude credentials.

See the [configuration, files, and implementation reference](QB_REFERENCE_en.md) for detailed fields, layouts, sources, and code constraints.
