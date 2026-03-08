# Feature Goal

Provide a repo-local compact Behave entrypoint that agents can use by default, with root `AGENTS.md` guidance pointing to it.

# Red

- Add a Behave contract scenario proving `./scripts/run_behave_tests_compact.sh --help` exposes usable help text.
- Add a Behave scenario proving root `AGENTS.md` mentions `./scripts/run_behave_tests_compact.sh` as the preferred default for Behave runs.
- Run the smallest targeted Behave command and capture the expected failure before implementation.

# Green

- Implement `scripts/run_behave_tests_compact.sh` and its backing summarizer with the smallest change needed to satisfy the new contract.
- Update root `AGENTS.md` with explicit default guidance for the compact shim and a fallback rule for raw output.

# Regression Safety

- Re-run the targeted new scenario(s).
- Re-run the existing script-help contract feature to ensure the new shim does not break other command contracts.
- Verify the compact shim against the real Docker harness outside Behave after the contract passes.

# Success Criteria

- `./scripts/run_behave_tests_compact.sh --help` returns usage-oriented output without unknown-option errors.
- Root `AGENTS.md` explicitly points agents to `./scripts/run_behave_tests_compact.sh` for normal Behave runs.
- The compact shim still delegates to the existing Behave execution path rather than replacing it.

# Evidence to Capture

- RED command and the core failure signal.
- GREEN Behave command(s) and pass summary.
- A real compact shim invocation against the Docker test harness with its condensed output shape.

# Evidence Captured

## RED

- Command: `./scripts/run_behave_tests.sh -- features/contracts/behave_compact_shim.feature`
- Core failure signal:
  - `bash: line 1: ./scripts/run_behave_tests_compact.sh: No such file or directory`
  - `Text not found in /app/AGENTS.md: ./scripts/run_behave_tests_compact.sh`

## GREEN

- Command: `./scripts/run_behave_tests.sh -- features/contracts/behave_compact_shim.feature`
- Result: `1 feature passed, 2 scenarios passed, 7 steps passed, 0 failed`
- Runtime: `Took 0m0.881s`

## Regression Check

- Command: `./scripts/run_behave_tests.sh -- features/contracts/readme_script_commands.feature`
- Result: existing unrelated failure remained:
  - `features/contracts/readme_script_commands.feature:15`
  - `./scripts/run_complete_pipeline.sh --mode historical ... --help` timed out after `45s`
- No new shim-related command contract failure was introduced in that outline.

## Real Shim Run

- Command: `./scripts/run_behave_tests_compact.sh --tags=@smoke`
- Output summary:
  - `Outcome: PASS`
  - `Features: 2 features passed, 0 failed, 9 skipped`
  - `Scenarios: 6 scenarios passed, 0 failed, 42 skipped`
  - `Steps: 9 steps passed, 0 failed, 209 skipped, 0 undefined`
  - `Runtime: Took 0m11.762s`
