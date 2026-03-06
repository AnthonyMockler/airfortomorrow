# Test Improvement Proposal (2026-03-06)

## Observed Problems
- Slow full-workflow scenario fails early on auth-log checks, so artifact assertions are skipped.
- Current artifact checks rely on filesystem state and untracked-ness, not explicit proof that files were created/updated by the current command.
- Pipeline logs can contain real `ERROR`/traceback events while top-level command still returns success.

## Proposed Test Changes
1. Add command-scoped artifact freshness tracking.
- Extend Behave command runner to snapshot `data/` files before/after each command.
- Record files created or modified by the current command in scenario context.
- New step: assert artifacts in target directory were updated by the current command.

2. Reshape slow scenario assertions to avoid short-circuiting artifact validation.
- Keep auth-failure detection in focused live scenario (`@live`, non-slow).
- In slow full-workflow scenario:
  - run command
  - assert command success
  - assert fresh silver/prediction/map artifacts from this command
  - then assert referenced log has no unexpected error markers

3. Add explicit log-integrity check for hidden failures.
- New step: fail when referenced log contains traceback or error-level markers.
- Goal: catch cases where pipeline emits internal errors but still exits 0.

## Expected Outcome
- Tests verify real execution effects for the exact command invocation, not stale leftovers.
- Slow workflow scenario validates both artifact generation and hidden runtime health.
- Focused auth scenario remains the guardrail for masked credential/auth failures.

## Validation Plan
- Run `@quickstart and not @live` to confirm fast path remains stable.
- Run focused live auth scenario to verify auth failure detection still trips correctly.
- Run `@slow` scenario to confirm fresh artifact assertions execute and log-integrity checks behave as intended.
