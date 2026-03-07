# TESTS KNOWLEDGE BASE

**Generated:** 2026-03-06
**Updated:** 2026-03-06

## OVERVIEW
Repository tests use **Behave BDD** as the preferred style for workflow and contract coverage, executed inside Docker for dependency parity.

## STYLE RULES
- Write tests as Gherkin features under `features/` with clear Given/When/Then intent.
- Keep step definitions in `features/steps/` small and reusable.
- Prefer command-level contract checks and atomic workflow checks over monolithic end-to-end scenarios.
- Tag scenarios consistently:
  - `@smoke`: fast runtime/environment checks
  - `@contract`: CLI/help/argument behavior
  - `@quickstart`: README setup/workflow coverage
  - `@slow`: long-running scenarios
  - `@live`: scenarios that require external APIs/network conditions

## EXECUTION RULES
- Run BDD tests through Docker:
  - `./scripts/run_behave_tests.sh`
- Avoid host execution unless debugging locally with explicit opt-in.
- Default Behave execution should exclude `@slow` and `@live`.

## AUTHORING GUIDELINES
- Keep scenarios atomic so failures isolate to one workflow responsibility.
- Validate observable outcomes (exit code, output text, file artifacts).
- Reuse shared command-running helpers from `features/environment.py` instead of custom subprocess logic per step file.
- Use scenario outlines for repeated contract checks (for example, script help coverage).

## SESSION LEARNINGS (2026-03-06)
### What Went Wrong
- Live quickstart scenarios could pass on stale files left in `data/` from previous runs.
- Assertions that only checked `command should succeed` were too weak; wrapper scripts can return `0` even when child collectors logged auth failures.
- File-existence checks could be satisfied by baseline files that are intentionally committed to the repo.
- Step definitions that depend on `git` binaries are brittle inside Docker test images (not guaranteed installed).

### Anti-Patterns (Do Not Use)
- `Then the command should succeed` as the only success criterion for `@live` scenarios.
- `directory should contain files` checks in mutable `data/` paths without run isolation.
- Counting artifacts in directories that include tracked baseline fixtures.
- Using `git ls-files` inside Behave steps to decide what to delete/count.

### Correct Pattern
- Before live workflow runs, clean `data/` and preserve only known baseline tracked fixtures:
  - `data/training/silver_dataset.parquet`
  - `data/raw/firms/historical/*`
- For output assertions in mutable paths, require **untracked/new** artifacts, not generic existence.
- Capture logs created by the current command and fail scenario on auth/credential signatures (for example `HTTP 401`, `Invalid credentials`, `Login incorrect`, `NotAuthorized`).
- Keep a focused live scenario for quick failure detection (OpenAQ/Himawari auth checks) and a separate `@slow` full workflow scenario for comprehensive coverage.
