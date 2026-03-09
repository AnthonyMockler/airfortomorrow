# Project Knowledge Base

Air for Tomorrow is an end-to-end air quality prediction pipeline. It combines ground sensors (OpenAQ, AirGradient), fire detections (NASA FIRMS), AOD (Himawari), and meteorology (ERA5) to predict PM2.5 on an H3 grid with XGBoost.

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

## Mandatory Rules

- Use wrapper scripts in `scripts/` rather than calling `src/` modules directly.
- Use `ConfigLoader` in Python and `scripts/utils/config_reader.sh` in Bash for configuration access.
- For executable workflow changes, create or claim a plan in `plans/` and create a decision note in `decisions/`.
- For workflow behavior changes, write or update Behave coverage first and capture the expected RED failure before implementation.
- Documentation-only changes can skip Behave only when they do not change executable behavior.
- Prefer `./scripts/run_behave_tests_compact.sh` for routine agent-driven Behave runs.
- Use `./scripts/run_behave_tests.sh` only when full raw output is explicitly needed or when debugging the compact wrapper.
- Use `./scripts/run_tests.sh` for pytest. Do not run pytest directly on the host.
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
