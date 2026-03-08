# Decision: ERA5 Realtime Contract + Small Real Benchmark Coverage

## Date
2026-03-07

## Decision
Add focused Behave coverage for an ERA5-only realtime workflow that validates:
- command-line contract surface for ERA5 entrypoints, and
- production of fresh, non-empty, schema-valid ERA5 realtime parquet output on a small but real live run profile.

## Why
- User testing notes indicate ERA5 is the next slowest completed pipeline after OpenAQ in the observed run (`ERA5 ~680s` in `USER_TESTING_QUICKSTART_NOTES.md`).
- Existing BDD coverage validates broader workflow behavior but does not lock down ERA5-only realtime output contract in an isolated scenario.
- We need a repeatable baseline scenario to evaluate future ERA5 performance changes without running the full end-to-end pipeline each iteration.

## Change Scope
- Add an ERA5-specific contract feature file under `features/contracts/`.
- Add ERA5-specific step definitions to validate:
  - updated ERA5 realtime parquet files were produced by the current command,
  - expected core columns exist and key columns are non-null/numeric,
  - output includes multiple H3 cells (useful downstream input).
- Run ERA5-focused Behave scenarios through the Docker harness and capture evidence.
- Review current ERA5 collector/processor flow and produce a concrete optimization plan (no production refactor in this task).

## Non-Goals
- No implementation changes to ERA5 collector/processor logic in this task.
- No expansion to non-ERA5 test scope.
- No tuning of model, silver, or prediction stages.
