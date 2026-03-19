# Parquet Phase 1 Runtime Brief

- Status: Locked for phase 1 implementation
- Date: 2026-03-19
- Scope: Define the smallest acceptable implementation for the first phase of the parquet pipeline rebuild.

## Goal

Build the runtime foundation only.

This phase should create the minimal shell, CLI, layout, manifest, and SQLite runtime needed for later bronze, silver, gold, and prediction work. It should not implement source-specific collection or materialization logic beyond the minimum needed to exercise the runtime contract.

## Required Reading

A phase-1 implementation agent should read only:

1. [AGENTS.md](/Users/anthonymockler/Documents/unicef/airfortomorrow/AGENTS.md)
2. [2026-03-18-parquet-lake-architecture-design.md](/Users/anthonymockler/Documents/unicef/airfortomorrow/docs/superpowers/specs/2026-03-18-parquet-lake-architecture-design.md)
3. [2026-03-19-parquet-phase-1-runtime-brief.md](/Users/anthonymockler/Documents/unicef/airfortomorrow/docs/superpowers/specs/2026-03-19-parquet-phase-1-runtime-brief.md)
4. [2026-03-18-spatial-parquet-pipeline-rebuild.md](/Users/anthonymockler/Documents/unicef/airfortomorrow/docs/superpowers/plans/2026-03-18-spatial-parquet-pipeline-rebuild.md)

Do not require the air-quality silver spec, bronze source-policy reference, or other later-phase reference notes for phase 1.

## In Scope

- `scripts/aq_pipeline.sh`
- a small CLI under `src/parquet_pipeline/`
- config loading
- partition path helpers
- partition manifest read/write
- SQLite runtime state in `data/system/jobs.sqlite`
- explicit job-list creation for date-based commands
- enough contract coverage to prove:
  - wrapper invocation works
  - commands parse correctly
  - manifests are written in the locked format
  - SQLite tracks runs and jobs
  - rerun skip-by-default behavior works where phase-1 commands publish output

## Out Of Scope

- real OpenAQ or AirGradient collection
- silver materialization
- gold grid generation
- prediction logic
- source-specific bronze fetch-window logic
- classification logic
- any unsupported mode surface that would imply a later phase already exists

If a feature depends on bronze, silver, gold, or prediction semantics beyond generic runtime plumbing, it belongs to a later phase.

## Hard Rules

- unsupported commands, sources, or modes must fail explicitly
- wrapper must work when invoked from outside the repo root
- reruns must skip existing outputs by default unless `--force` is implemented and explicitly used
- manifests must record only actual existing upstream inputs
- do not advertise source support that phase 1 does not really implement

## Deliverable

At the end of phase 1, a future agent should be able to start phase 2 without redesigning the runtime foundation.
