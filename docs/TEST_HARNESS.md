# Test Harness

## Default Commands

- `./scripts/run_behave_tests_compact.sh`: preferred Behave path for routine agent-driven work
- `./scripts/run_behave_tests.sh`: raw Docker-backed Behave harness
- `./scripts/run_tests.sh`: pytest wrapper
- `./scripts/smoke_test.sh`: smoke path that can build and validate the Docker image

## Behave Defaults

- Behave configuration lives in `behave.ini`.
- Default tags exclude `@slow` and `@live`.
- Use explicit tag selection when you need slower or network-dependent coverage.

## Common Tags

- `@smoke`: fast environment and harness checks
- `@contract`: CLI and documentation contract checks
- `@quickstart`: README workflow coverage
- `@slow`: long-running scenarios
- `@live`: scenarios that depend on external services or credentials

## Execution Rules

- Prefer the compact Behave shim unless full raw output is explicitly needed.
- Do not run pytest directly on the host; use `./scripts/run_tests.sh`.
- Use Behave for wrapper, CLI, documentation-contract, and workflow behavior.
- Use pytest first for narrower Python logic when a stable function-level seam exists and no user-facing workflow contract changed.
- Keep scenarios atomic so failures isolate to one responsibility.
- Reuse shared command-running helpers from `features/environment.py` and the existing step libraries.

## Long-Running Runs

- For performance, soak, load, `@slow`, or other commands expected to run more than 10 minutes, start the command once and record the command, start time, and log path before moving on.
- For long-running Behave runs, use `./scripts/run_behave_tests_compact.sh --long-run ...` when you know the run will be slow. The compact shim also enables this guidance automatically when forwarded Behave args include `@slow`.
- Do not poll, tail, or send status updates more often than every 5 to 10 minutes unless the run exits, fails, materially changes state, or the user asked for tighter updates.
- Prefer one delayed check over repeated short-interval checks. Token-efficient waiting is the default for long-running test work.
- Prefer compact output so the result stays readable.
- When a wrapper supports detached execution or durable logs, use that path so the run can complete without repeated terminal interaction.

## Evidence Expectations

- record the exact command
- record the pass or fail summary
- capture the raw-log path when relevant
- prove the artifacts being checked were produced or updated by the current run
