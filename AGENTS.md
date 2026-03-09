# Project Knowledge Base

Air for Tomorrow is an end-to-end air quality prediction pipeline. It combines ground sensors (OpenAQ, AirGradient), fire detections (NASA FIRMS), AOD (Himawari), and meteorology (ERA5) to predict PM2.5 on an H3 grid with XGBoost.

## Purpose and Outputs

- Operational goal: produce daily PM2.5 estimates for Thailand and Laos, especially where ground sensors are sparse.
- System shape: collect and process source data, harmonize everything onto H3, build a silver feature table, then run XGBoost inference.
- Outputs that matter:
  - processed source parquet files under `data/processed/`
  - silver feature datasets under `data/silver/`
  - prediction parquet files under `data/predictions/data/`
  - optional maps and validation artifacts under `data/predictions/`

## Start Here

- Use the shell wrappers in `scripts/` for execution. Start at `./scripts/run_complete_pipeline.sh`.
- Load durable repo guidance from `docs/README.md` and open the focused doc for the task at hand.
- Use the directory-specific notes when working in one layer:
  - `scripts/AGENTS.md`
  - `src/AGENTS.md`
  - `tests/AGENTS.md`

## Quick Map

- `scripts/`: Bash orchestration and the only blessed user-facing entrypoints.
- `src/`: Python implementation for collectors, processors, silver-data assembly, and prediction.
- `features/`: Behave workflow and contract coverage.
- `config/config.yaml`: central configuration source.
- `data/`: raw, processed, silver, and prediction artifacts.
- `plans/`: active work records and verification evidence.
- `decisions/`: short decision notes for scoped workflow or behavior changes.
- key code entrypoints: `src/run_complete_pipeline.py`, `src/make_silver.py`, `src/predict_air_quality.py`

## Mandatory Rules

- Use wrapper scripts in `scripts/` rather than calling `src/` modules directly.
- Use `ConfigLoader` in Python and `scripts/utils/config_reader.sh` in Bash for configuration access.
- For executable workflow changes, create or claim a plan in `plans/` and create a decision note in `decisions/`.
- For workflow, CLI, or contract changes, write or update Behave coverage first and capture the expected RED failure before implementation.
- For narrower Python logic changes, use `./scripts/run_tests.sh` when a focused pytest path is the better fit.
- Documentation-only changes can skip Behave only when they do not change executable behavior.
- Prefer `./scripts/run_behave_tests_compact.sh` for routine agent-driven Behave runs.
- Use `./scripts/run_behave_tests.sh` only when full raw output is explicitly needed or when debugging the compact wrapper.
- Use `./scripts/run_tests.sh` for pytest. Do not run pytest directly on the host.
- For performance, soak, load, `@slow`, or other runs expected to exceed 10 minutes, start the command once, record the log path, and do not poll, tail, or send status updates more often than every 5 to 10 minutes unless the run exits, fails, materially changes state, or the user asked for tighter updates.
- For long-running Behave work, prefer `./scripts/run_behave_tests_compact.sh --long-run ...`. The compact shim also auto-enables the same delayed-check guidance when forwarded Behave args include `@slow`.
- Do not let tests pass on stale artifacts from older runs.
- Invalid mode-specific flags or options must fail explicitly.
- Push to `origin` only. Never push to `upstream`.

## Common Commands

```bash
./scripts/run_complete_pipeline.sh --mode realtime --countries THA LAO
./scripts/run_behave_tests_compact.sh --tags=@smoke
./scripts/run_tests.sh -- -q
./scripts/smoke_test.sh
```

## Docs Index

- `docs/README.md`: task-oriented guide to the docs set
- `docs/REPO_MAP.md`: top-level map, entrypoints, and directory ownership
- `docs/ARCHITECTURE.md`: wrapper, Python, configuration, and H3 architecture
- `docs/DATAFLOW.md`: collectors -> processors -> silver -> prediction flow
- `docs/WORKFLOW_RULES.md`: plans, decisions, TDD workflow, and git rules
- `docs/TEST_HARNESS.md`: Behave, pytest, tags, long-running runs, and evidence capture
- `docs/SOURCE_CONTRACTS.md`: source-specific constraints and wrapper guidance
- `docs/RELIABILITY_AND_OPERATIONS.md`: logs, artifact freshness, common failures, and troubleshooting
- `docs/HARNESS_ADOPTION.md`: why the harness rollout exists and which phases are planned next

## Fast Path By Task

- Need to understand what the repo actually does:
  - read `README.md`
  - read `docs/DATAFLOW.md`
  - read `docs/ARCHITECTURE.md`
- New behavior or bug fix:
  - read `docs/WORKFLOW_RULES.md`
  - read `docs/TEST_HARNESS.md`
- Collector or processor work:
  - read `docs/SOURCE_CONTRACTS.md`
  - read `src/AGENTS.md`
- Wrapper or CLI work:
  - read `docs/REPO_MAP.md`
  - read `scripts/AGENTS.md`
- Test or contract work:
  - read `docs/TEST_HARNESS.md`
  - read `tests/AGENTS.md`
