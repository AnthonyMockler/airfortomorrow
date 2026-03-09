# Project Knowledge Base

Air for Tomorrow predicts PM2.5 on an H3 grid using ground sensors (OpenAQ, AirGradient), fire detections (NASA FIRMS), AOD (Himawari), and ERA5 meteorology.

## Purpose

- Produce daily PM2.5 estimates for Thailand and Laos, especially where sensor coverage is sparse.
- Main outputs:
  - `data/processed/` source parquet files
  - `data/silver/` feature tables
  - `data/predictions/data/` prediction parquet files

## Quick Map

- `scripts/`: only supported user-facing entrypoints
- `src/`: collectors, processors, silver assembly, prediction
- `features/`: Behave workflow and contract coverage
- `config/config.yaml`: central config
- Key entrypoints: `src/run_complete_pipeline.py`, `src/make_silver.py`, `src/predict_air_quality.py`

## Core Rules

- Use wrapper scripts in `scripts/`; do not run `src/` modules directly.
- Use `ConfigLoader` (Python) and `scripts/utils/config_reader.sh` (Bash) for config access.
- Prefer explicit errors for invalid mode/flag combinations.
- Ensure checks validate fresh artifacts from the current run.
- Push to `origin` only, never `upstream`.

## Workflow (lightweight by default)

- Small/local changes: no required `plans/*.md`; record commands and verification in commit/PR notes.
- Workflow/CLI/contract changes: add a decision note in `decisions/`; add a plan only when work is multi-step, cross-layer, or likely to span sessions.
- High-risk or cross-source changes: decision note + plan required.
- Docs-only changes with no behavior change can skip Behave, plans, and decisions.

## Test-First Rules

- Workflow/CLI/contract behavior: write or update Behave first and capture RED before implementation.
- Narrow Python logic with stable seams: start with `./scripts/run_tests.sh`; add Behave only if user-visible workflow behavior changed.
- Implement minimal GREEN change, then rerun targeted and regression coverage.

## Test Commands

- Behave default: `./scripts/run_behave_tests_compact.sh`
- Behave raw output/debug: `./scripts/run_behave_tests.sh`
- pytest: `./scripts/run_tests.sh` (do not run pytest directly on host)
- smoke: `./scripts/smoke_test.sh`
- Default Behave should exclude `@slow` and `@live` unless explicitly needed.

## Long-Run Commands (10+ min expected)

- Start once and record log path.
- Prefer `./scripts/run_behave_tests_compact.sh --long-run ...` for slow Behave runs.
- Do not poll/tail/status-update more often than every 5 to 10 minutes unless run state materially changes.

## Minimal Plan Template (only when needed)

```md
# <Short Title>

- Status: Planned | In Progress | Blocked | Complete
- Owner: <agent or person>
- Last Updated: YYYY-MM-DD

## Goal
## Red
## Green
## Verification
## Notes
```

## Optional Deep References

- `docs/REPO_MAP.md`
- `docs/ARCHITECTURE.md`
- `docs/DATAFLOW.md`
- `docs/SOURCE_CONTRACTS.md`
- `docs/RELIABILITY_AND_OPERATIONS.md`
