# Test Improvement Proposal (2026-03-07)

## Baseline Findings
- With valid credentials, the focused `@live` quickstart scenario times out at 900s because OpenAQ collection is long-running.
- Timeout currently bubbles as a harness exception (`subprocess.TimeoutExpired`) rather than a normal command result, which weakens failure diagnostics.
- Slow quickstart scenario correctly catches hidden runtime errors (`ERROR` + traceback) in the referenced complete-pipeline log.

## Proposed Improvements
1. Make command timeouts first-class test results.
- Catch `subprocess.TimeoutExpired` in Behave environment runner.
- Store timeout state in `ShellResult` (`timed_out`, timeout seconds).
- Return deterministic non-zero exit code (`124`) with explicit timeout message in output.
- Benefit: scenarios fail with clean assertion messages, not step tracebacks.

2. Bound the focused `@live` auth/integrity scenario runtime.
- Use `--test-mode --test-openaq-limit 3` in that scenario command.
- Keep OpenAQ + Himawari active so auth/log checks remain meaningful.
- Benefit: preserve intent while preventing 15+ minute collector overruns and timeout-driven false negatives.

## Expected Outcome
- Focused `@live` scenario no longer fails from harness exception shape.
- Timeouts (if they still occur) appear as explicit command-failure evidence.
- Full-suite runtime and stability improve while still testing real pipeline behavior.

## Validation Plan
- Rerun full suite with all tags: `./scripts/run_behave_tests.sh -- --tags='~@__never__'`
- Confirm focused `@live` scenario behavior changes from timeout traceback to either:
  - clean pass (preferred), or
  - clean assertion failure with timeout message.
- Confirm slow scenario still validates fresh artifacts and catches referenced-log errors if present.

## Implementation Status
- Implemented both proposed improvements:
  - timeout-aware shell execution in Behave environment;
  - bounded focused `@live` command with `--test-mode --test-openaq-limit 3`.

## Post-Implementation Validation
- Full rerun command: `./scripts/run_behave_tests.sh -- --tags='~@__never__'`
- Full rerun log: `logs/behave_full_env_after_20260307_013035.log`
- Outcome:
  - `31 scenarios passed, 1 failed` (improved from `30 passed, 2 failed`)
  - focused `@live` timeout issue resolved (scenario now passes)
  - remaining failure is the slow scenario log-integrity check on real hidden prediction error

## Additional Next-Step Hardening
1. Add explicit row-count/schema assertions for silver and prediction parquet outputs.
2. Add optional per-scenario timeout overrides via env vars (so CI can tune without editing feature files).
3. Keep slow referenced-log integrity gate strict until pipeline no longer reports success after `ERROR`/traceback.
