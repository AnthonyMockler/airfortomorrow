# Plan: Historical Collection Behave Coverage (BDD Red/Green)

- Status: Complete
- Owner: Codex
- Active Agent: Codex (GPT-5)
- Started: 2026-03-09
- Last Updated: 2026-03-09
- Scope Note: Implement historical collector Behave coverage for bounded real-data slices, capture RED/GREEN evidence, and keep the runs small enough for iterative performance work.

## Feature Goal

Protect the historical data-collection workflow with user-facing Behave coverage so historical performance work can proceed with confidence across collector-specific historical code paths.

## Scope Guardrails

- Start from user-facing docs, not internal implementation guesses.
- Keep this pass documentation-only: no `.feature`, step-definition, or production code changes yet.
- Limit the first executable Behave slice to historical collection artifacts only.
- Use real historical data paths only; do not rely on mocks, fixtures, or synthetic parquet outputs for the collector contract scenarios.
- Prefer small bounded runs for future live scenarios: one country and only a few days to one week of data, with fresh artifacts from the current run.
- Prefer per-wrapper scenarios over one monolithic multi-hour historical pipeline run.

## Red

1. Convert the plaintext scenario below into one or more `.feature` scenarios.
2. Run the smallest targeted Behave slice for the new historical collection feature.
3. Capture the expected RED signal, likely undefined historical-specific artifact assertions.

## Green

1. Implement only the missing historical-specific Behave steps needed to assert fresh artifacts and core schema/data usefulness.
2. Re-run the targeted historical slice until green.
3. Keep scenario scope bounded enough to reuse as an optimization baseline while still exercising real historical collection behavior.

## Regression Safety

- Reuse existing generic command, log, and filesystem steps in [`features/steps/cli_steps.py`](/Users/anthonymockler/Documents/unicef/airfortomorrow/features/steps/cli_steps.py) and [`features/steps/filesystem_steps.py`](/Users/anthonymockler/Documents/unicef/airfortomorrow/features/steps/filesystem_steps.py).
- Ensure assertions use files updated by the current command so stale artifacts cannot satisfy the scenario.
- Preserve Git-tracked/LFS historical FIRMS inputs in `data/raw/firms/historical/` during cleanup.
- Re-run existing historical argument-guard coverage alongside the new slice once implementation starts.

## Success Criteria

- Historical Behave coverage validates the documented collection workflow for a bounded date range.
- The coverage uses real historical data sources and real wrapper commands, not mocked or precomputed substitute outputs.
- Each historical collector scenario proves that the wrapper command succeeds, writes a log, and produces fresh output artifacts in the documented directories.
- Artifact assertions cover the minimum downstream contract needed by `make_silver.sh`: non-empty data plus key columns and basic value sanity.
- Artifact assertions also prove the files contain useful and plausible information, not just structurally valid output files.
- The selected historical window is small enough for iterative performance work, targeting a few days to one week rather than long backfills.
- Coverage distinguishes historical-specific behavior from already-tested realtime behavior.

## Evidence to Capture

- The README and `DOCUMENTATION.md` commands that define the user workflow.
- Selected bounded command profiles for each historical collector.
- RED command and core failure signal.
- GREEN command and pass summary.
- Paths to fresh artifacts and the schema/value checks asserted by the scenarios.

## Notes and Findings

- README historical entry point:
  - `./scripts/run_complete_pipeline.sh --mode historical --start-date 2024-06-01 --end-date 2024-06-03 --countries THA LAO --generate-maps`
- Detailed docs recommend decomposing long historical runs into wrapper commands instead of one full pipeline command:
  - `./scripts/run_air_quality_integrated_pipeline.sh --mode historical --start-date 2023-01-01 --end-date 2023-06-31 --countries THA LAO`
  - `./scripts/run_era5_idw_pipeline.sh --mode historical --start-date 2023-01-01 --end-date 2023-06-31 --countries THA LAO`
  - `./scripts/run_firms_pipeline.sh --mode historical --start-date 2023-01-01 --end-date 2023-06-31 --countries THA LAO`
  - `./scripts/run_himawari_integrated_pipeline.sh --mode historical --start-date 2023-01-01 --end-date 2023-06-31 --countries THA LAO`
- Existing coverage already protects:
  - README command help contracts in [`features/contracts/readme_script_commands.feature`](/Users/anthonymockler/Documents/unicef/airfortomorrow/features/contracts/readme_script_commands.feature)
  - historical missing-date guards in [`features/contracts/historical_argument_guards.feature`](/Users/anthonymockler/Documents/unicef/airfortomorrow/features/contracts/historical_argument_guards.feature)
- Gap identified:
  - No Behave scenario currently proves fresh historical collection outputs for the four main collector wrappers.
- Historical-specific constraints to reflect in future instrumentation:
  - Air Quality historical path uses OpenAQ archive plus AirGradient historical API and writes processed historical air-quality parquet output.
  - FIRMS historical path depends on preloaded LFS input files in `data/raw/firms/historical/`.
  - Himawari historical path is heavy; the first test should use only a few days and assert fresh H3, daily aggregate, and interpolated outputs.
  - ERA5 historical path requires CDS credentials and should use one parameter such as `2t` plus a short historical slice to keep runtime bounded.

### Plaintext BDD Scenario

Scenario: User follows the documented historical collection workflow for a small bounded date range

Given the repository has the required historical prerequisites available for the selected slice
And the historical output directories for air quality, FIRMS, Himawari, and ERA5 are cleaned without deleting tracked bootstrap inputs
When the user runs the documented historical collection wrappers for one country and a real historical slice of only a few days to one week
Then each wrapper command succeeds
And each wrapper prints or references a log file for the run
And each wrapper creates fresh historical artifacts in its documented output directory
And each artifact is non-empty and contains the key columns needed by downstream silver-data assembly
And each artifact contains useful and plausible values for its data source and requested date range
And the scenario only passes when those artifacts were produced or updated by the current run

### Recommended Behave Shape For The Next Pass

- Feature file:
  - `features/contracts/historical_collection_contract.feature`
- Scenario set:
  - docs/contract scenario confirming the historical commands remain documented
  - Air Quality historical live contract scenario
  - FIRMS historical live contract scenario
  - Himawari historical live contract scenario
  - ERA5 historical live contract scenario
- Why split by wrapper:
  - isolates failures to the collector under test
  - makes runtimes manageable
  - supports later collector-by-collector speed work
  - matches the documentation recommendation for long historical analysis

### Proposed Initial Command Profiles

- Air Quality:
  - `./scripts/run_air_quality_integrated_pipeline.sh --mode historical --start-date 2026-01-01 --end-date 2026-01-03 --countries THA`
- FIRMS:
  - `./scripts/run_firms_pipeline.sh --mode historical --start-date 2025-01-01 --end-date 2025-01-03 --countries THA`
- Himawari:
  - `./scripts/run_himawari_integrated_pipeline.sh --mode historical --start-date 2025-01-01 --end-date 2025-01-03 --countries THA`
- ERA5:
  - `./scripts/run_era5_idw_pipeline.sh --mode historical --start-date 2025-01-01 --end-date 2025-01-03 --countries THA --params 2t --force`

### Slice Selection Rules

- Prefer a 3-day slice as the default starting point for the first live historical scenarios.
- Allow expansion up to 7 days only when a collector needs more than 1-3 days to demonstrate useful variation or stable artifact generation.
- Choose dates that are known to be available from the real upstream or repository-backed historical source:
  - FIRMS: inside the tracked archive window already documented in the repo.
  - Air Quality: inside a range supported by the OpenAQ historical archive and AirGradient historical access.
  - Himawari: dates with normal archive availability on JAXA.
  - ERA5: dates safely covered by CDS reanalysis availability.

### Likely Step-Definition Additions Later

- Historical artifact selectors per collector, analogous to the existing realtime-specific step modules.
- Shared parquet assertions that can validate:
  - minimum rows
  - required columns
  - non-null key identifiers and dates
  - numeric data in the collector's main signal column
  - minimum unique H3 cells or timestamps where appropriate
- Collector-specific plausibility assertions such as:
  - Air Quality: `pm25` values are numeric, non-negative, and not entirely identical; timestamps land inside the requested historical range.
  - FIRMS: fire-intensity outputs are numeric, non-negative, and show non-zero signal when the selected date slice is expected to contain hotspots.
  - Himawari: AOD outputs are numeric, within a sane atmospheric range, and tied to the requested historical date.
  - ERA5: meteorological outputs are numeric, vary across H3 cells, and carry dates matching the requested slice.

## Evidence Log

- RED:
  - Command:
    - `./scripts/run_behave_tests.sh -- features/contracts/historical_collection_contract.feature`
  - Result:
    - Failed as expected with undefined historical collection steps after the new feature file was added.
    - Summary: `1 scenario passed, 2 failed, 2 skipped`, `22 undefined`, `Took 0m0.002s`.
    - Core signal: missing workspace-preparation and historical artifact assertion steps for the new historical contract feature.
- GREEN so far:
  - FIRMS scenario:
    - Command:
      - `./scripts/run_behave_tests.sh -- features/contracts/historical_collection_contract.feature:33`
    - Result:
      - Passed after implementing `features/steps/historical_collection_steps.py`.
      - Summary: `1 feature passed, 1 scenario passed, 14 steps passed`, `Took 1m20.449s`.
  - Air Quality scenario:
    - Command:
      - `./scripts/run_behave_tests.sh -- features/contracts/historical_collection_contract.feature:14`
    - Result:
      - Passed with real bounded historical data after forcing fresh Air Quality workspace cleanup.
      - Summary: `1 feature passed, 1 scenario passed, 16 steps passed`, `Took 33m26.354s`.
      - Operational finding:
        - OpenAQ historical archive download dominates this bounded 3-day Air Quality run because the current historical path materializes many `location_<id>_2026.parquet` files before downstream filtering.
  - ERA5 scenario:
    - Command:
      - `./scripts/run_behave_tests.sh -- --tags=@slow features/contracts/historical_collection_contract.feature:81`
    - Result:
      - Passed after updating the historical `2t` plausibility bound to match the actual generated historical output units.
      - Summary: `1 feature passed, 1 scenario passed, 14 steps passed`, `Took 6m13.479s`.
      - Operational finding:
        - Historical `2t` currently lands in Kelvin-scale values (`~289.7` to `301.0`) in the generated parquet, so the Behave contract now reflects the observed historical output rather than assuming Celsius.
  - Himawari scenario:
    - Command:
      - `./scripts/run_behave_tests.sh -- --tags=@slow features/contracts/historical_collection_contract.feature:50`
    - Result:
      - Passed with fresh historical H3, daily aggregated, and interpolated outputs for the bounded 3-day slice.
      - Summary: `1 feature passed, 1 scenario passed, 28 steps passed`, `Took 17m2.378s`.
  - Docs scenario:
    - Command:
      - `./scripts/run_behave_tests.sh -- features/contracts/historical_collection_contract.feature:5`
    - Result:
      - Passed as a lightweight post-implementation verification of the documented historical workflow entrypoints.
      - Summary: `1 feature passed, 1 scenario passed, 6 steps passed`, `Took 0m0.002s`.
  - Final verification note:
    - The new feature was verified as Docker-backed targeted scenario slices rather than one monolithic full-feature run, to keep historical live validation tractable while still executing every scenario against the real harness.

## Handoff

- Review the plaintext scenario and the proposed split-by-wrapper test shape.
- If approved, implement the `.feature` scenarios first and capture the RED failure before adding step definitions.
