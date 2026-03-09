# Reliability and Operations

## Operational Prerequisites

- Git LFS is required for tracked model and bootstrap data artifacts.
- Docker is the expected execution environment for tests and routine local runs.
- Credentials in `.env` are required for at least Himawari, OpenAQ, and ERA5/CDS-backed workflows.
- Historical FIRMS workflows depend on the tracked archive under `data/raw/firms/historical/`.

## Logs and Evidence

- Wrapper commands should print or reference the log file for the current run.
- When debugging behavior, capture the log path in the plan alongside the command result.
- Use the compact Behave shim for routine feedback and the raw harness only when detailed output is necessary.

## Current Reliability Risks

- wrapper scripts can appear to succeed even when child processes logged substantive failures
- stale files in `data/` can make weak artifact assertions pass
- external credentials and rate limits can break `@live` scenarios independently of code quality
- long-running historical slices can be too expensive for routine iteration if they are not tightly bounded
- larger historical OpenAQ runs and Himawari collection paths can dominate runtime even when the requested date slice looks small
- missing LFS bootstrap inputs can break historical workflows before code-level logic even runs

## Current Mitigations

- separate focused quick failure checks from slower comprehensive runs
- clean mutable output paths while preserving tracked bootstrap inputs
- fail scenarios on hidden auth or credential signatures in current-run logs
- keep historical and live slices intentionally small when used for contract coverage

## Troubleshooting Checklist

- confirm Docker, LFS, and required credentials are present before debugging code
- confirm the wrapper command, mode, dates, and countries match the intended slice
- inspect the current-run log file before assuming a top-level success message is trustworthy
- verify the artifact was created or updated by the current command
- check for credentials, timeout, or upstream availability failures before assuming a code regression

## Planned Improvement

Structured run manifests are planned in a later phase. Until then, logs plus fresh-artifact assertions remain the main runtime evidence surface.
