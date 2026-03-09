# Compact Shim Long-Run Mode

- Status: Complete
- Owner: Codex (GPT-5)
- Started: 2026-03-09
- Last Updated: 2026-03-09
- Scope Note: Add compact-shim support for long-running test cadence guidance so agents get a log path and explicit delayed check timing before `@slow` or `--long-run` runs.

## Feature Goal

Add repo-level tooling pressure for long-running Behave runs by teaching the compact shim to announce durable log output and a recommended delayed re-check time before the run starts.

## Scope Guardrails

- Keep the existing Docker-backed Behave harness as the execution engine.
- Prefer the compact shim as the single enforcement point for agent-driven Behave runs.
- Support explicit opt-in via a CLI flag and automatic opt-in for common slow-tag runs.
- Do not add background-job scheduling or change the raw harness defaults in this task.

## Red

- Extend compact-shim Behave contract coverage for long-run help text and runtime guidance output.
- Run the smallest targeted contract slice and capture the expected RED failure before implementation.

## Green

- Add `--long-run` support to `scripts/run_behave_tests_compact.py`.
- Print the raw-log path and explicit next-check guidance before starting the underlying run when long-run mode is active.
- Auto-enable the same guidance when Behave args include `@slow`.

## Regression Safety

- Re-run the compact-shim contract feature after the implementation change.
- Keep existing compact summary output and raw-log reporting intact for non-long-run invocations.

## Success Criteria

- `./scripts/run_behave_tests_compact.sh --help` documents a long-run mode.
- `./scripts/run_behave_tests_compact.sh --long-run -- --tags=@smoke` prints a raw-log path and a delayed next-check timestamp before the run completes.
- `@slow` runs through the compact shim get the same guidance without requiring agents to remember the flag.

## Evidence to Capture

- RED command and failure signal.
- GREEN command and pass summary.
- Any implementation tradeoff around explicit flag versus automatic `@slow` detection.

## Evidence Captured

### RED

- Command: `./scripts/run_behave_tests.sh -- features/contracts/behave_compact_shim.feature`
- Core failure signals:
  - `--help` output for `./scripts/run_behave_tests_compact.sh` did not contain `--long-run`.
  - `./scripts/run_behave_tests_compact.sh --long-run -- --tags=@smoke` failed with:
    - `__main__.py: error: unrecognized arguments: --long-run`

### GREEN

- Targeted contract:
  - Command: `./scripts/run_behave_tests.sh -- features/contracts/behave_compact_shim.feature`
  - Result: `1 feature passed, 3 scenarios passed, 13 steps passed`
  - Runtime: `Took 0m5.929s`
- Manual non-long-run regression check:
  - Command: `./scripts/run_behave_tests_compact.sh --tags=@smoke`
  - Result:
    - `Outcome: PASS`
    - `Features: 2 features passed, 0 failed, 13 skipped`
    - `Scenarios: 6 scenarios passed, 0 failed, 54 skipped`
    - `Steps: 9 steps passed, 0 failed, 338 skipped, 0 undefined`
    - `Runtime: Took 0m3.998s`
- Manual auto-detect verification:
  - Command: `./scripts/run_behave_tests_compact.sh --dry-run --tags=@slow`
  - Result:
    - `Long-run mode: enabled (detected @slow in forwarded Behave args)`
    - `Next check after: ...`
    - `Outcome: PASS`

## Notes and Findings

- The compact shim now enforces the long-run reminder at the point of execution instead of relying on docs alone.
- Supporting an optional forwarded `--` separator in the shim avoids a fragile CLI edge case and keeps invocation habits tolerant.
- Automatic `@slow` detection covers the most obvious long-running Behave path without making every run noisy.
