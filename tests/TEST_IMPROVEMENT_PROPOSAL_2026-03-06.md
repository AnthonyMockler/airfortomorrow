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

## Implementation Status (2026-03-07)
- Implemented:
  - command-scoped `data/` freshness snapshot in Behave environment;
  - fresh-artifact step (`updated by the current command`);
  - referenced-log error marker assertion;
  - slow scenario reordered so artifact checks execute before log-integrity gate.
- Verified by rerun:
  - full all-tags run (`--tags='~@__never__'`) executed all 32 scenarios;
  - fresh-artifact steps passed in slow scenario;
  - slow scenario correctly failed on hidden `ERROR`/traceback markers in the referenced pipeline log.

## Next Improvement Candidates
1. Add content-level artifact assertions.
- Validate parquet row-count > 0 and required columns for silver/prediction outputs.
- Validate map PNG is newly written and non-trivial (size threshold + decode check).

2. Split live credential expectations into explicit modes.
- Keep current strict live scenario for credentialed environments.
- Add a separate negative-credentials scenario (or tag) that expects auth failure markers, so intent is explicit.

3. Tighten log-integrity semantics.
- Keep fail-on-traceback.
- Optionally scope `ERROR` markers to known critical components to reduce false positives while preserving strictness.
