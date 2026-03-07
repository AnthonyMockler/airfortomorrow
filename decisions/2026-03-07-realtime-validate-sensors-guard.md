# Decision: Realtime Validation Flag Guard

## Date
2026-03-07

## Decision
`--validate-sensors` is invalid in realtime mode and must fail fast with a clear error.

## Why
- Realtime prediction currently accepts validation flags that are intended for historical evaluation logic.
- This creates contradictory behavior and can trigger downstream runtime errors.
- Users should get immediate feedback instead of partial execution and misleading success output.

## Change Scope
- Add argument validation guard in prediction entrypoint so realtime + `--validate-sensors` exits immediately with explicit message.
- Ensure wrapper behavior does not implicitly pass invalid realtime validation flags.
- Add Behave contract tests using red/green TDD.

## Non-Goals
- No model logic changes.
- No sensor validation algorithm changes.
