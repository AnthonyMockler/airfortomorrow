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
- Keep scenarios atomic so failures isolate to one responsibility.
- Reuse shared command-running helpers from `features/environment.py` and the existing step libraries.

## Long-Running Runs

- For commands expected to run more than 10 minutes, start the command once and wait for completion before checking again.
- Prefer compact output so the result stays readable.
- Do not spam interim polling unless the run fails, materially changes state, or the user asked for frequent updates.

## Evidence Expectations

- record the exact command
- record the pass or fail summary
- capture the raw-log path when relevant
- prove the artifacts being checked were produced or updated by the current run
