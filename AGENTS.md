# PROJECT KNOWLEDGE BASE

**Generated:** 2026-03-04

## Overview

Air for Tomorrow is an end-to-end air quality prediction pipeline. It combines ground sensors (OpenAQ, AirGradient), fire detections (NASA FIRMS), AOD (Himawari), and meteorology (ERA5) to predict PM2.5 on an H3 grid with XGBoost.

## Quick Map

- `scripts/`: Bash orchestration. Start at `run_complete_pipeline.sh`.
- `src/`: Python implementation. Key entrypoints include `run_complete_pipeline.py`, `make_silver.py`, and `predict_air_quality.py`.
- `config/config.yaml`: Central configuration. There is no `pyproject.toml`-style config for the app.
- `data/`: Raw, processed, silver, and prediction artifacts.

## Project Conventions

- Configuration is YAML-based and accessed via `ConfigLoader` in Python and `scripts/utils/config_reader.sh` in Bash.
- Main data flow: collectors -> processors -> silver dataset -> prediction model.
- Most collectors and processors support `realtime` and `historical` modes.
- Use the shell wrappers in `scripts/` instead of calling `src/` modules directly.

## Mandatory Workflow

Apply this workflow for feature work, bug fixes, regressions, and other executable behavior changes.

### 1) Document first

- Create a decision note in `decisions/` named `YYYY-MM-DD-<short-slug>.md`.
- Include: `Decision`, `Why`, `Change Scope`, `Non-Goals`.
- Create a plan in `plans/` named `YYYY-MM-DD-<short-slug>-tdd-plan.md`.
- Include: `Feature Goal`, `Red`, `Green`, `Regression Safety`, `Success Criteria`, `Evidence to Capture`.

### 2) Test first with Behave

- Write or update a `.feature` scenario in `features/` before implementation.
- Use clear, user-observable Gherkin behavior.
- Run the smallest targeted Behave command and capture the expected RED failure.
- Record the failing command and the core failure signal as evidence.

### 3) Implement minimally

- Make the smallest change that turns the new Behave scenario green.
- Prefer fail-fast argument validation and explicit errors for invalid combinations.
- Do not widen scope during the green phase.

### 4) Verify and harden

- Re-run the targeted scenario and related regression or contract coverage.
- For workflow behavior, use Behave verification rather than ad hoc shell-only checks.
- Make sure tests validate fresh artifacts from the current run, not stale files.

### 5) Commit in phases

- Docs commit: `decisions/` and `plans/`
- Test commit: feature files and step definitions
- Implementation commit: production changes

### Docs-only changes

- Documentation-only changes do not need Behave coverage if they do not change executable behavior.
- Use this exception for files like `AGENTS.md`, process notes, and other instruction-only updates.
- If a docs change also changes executable workflow or CLI behavior, use the full Behave RED/GREEN workflow above.

## Test Execution Rules

- Behave BDD is the default style for integration and workflow behavior tests.
- Prefer `./scripts/run_behave_tests_compact.sh` for routine agent-driven Behave runs.
- Use `./scripts/run_behave_tests.sh` directly only when full raw output is explicitly needed or when debugging the compact wrapper.
- Use `./scripts/run_tests.sh` for pytest. Do not run pytest directly on the host.
- Default Behave runs should exclude `@slow` and `@live`.

### Long-running test commands

- For Behave or pipeline runs expected to take more than 10 minutes, start the command once and wait for completion before checking again.
- Prefer `./scripts/run_behave_tests_compact.sh` for long Behave runs so the final output stays concise.
- Do not poll more often than once every 10-15 minutes for runs expected to take 30-90 minutes.
- Do not tail Docker logs or raw output during the run unless the user explicitly asks or the run appears stuck.
- Do not send interim progress updates unless output materially changes, the run fails, or the user explicitly asks for frequent updates.
- Prefer reporting the final compact summary and raw-log path after the command exits.

## Repo-specific Anti-patterns

- Do not execute `src/` modules directly without the wrapper-managed `PYTHONPATH`.
- Do not use `_load_config()` in `BaseCollector`; use `self.config_loader` instead.
- Do not treat manual shell runs as a substitute for Behave acceptance or regression tests.
- Do not let tests pass because of cached artifacts from older runs.
- Do not allow mode-invalid flags or options to pass silently.

## Common Commands

```bash
./scripts/run_complete_pipeline.sh --mode realtime --countries THA LAO
./scripts/run_behave_tests_compact.sh --tags=@smoke
./scripts/run_tests.sh -- -q
./scripts/smoke_test.sh
```

## Git and Branch Rules

- `origin` must point to `AnthonyMockler/airfortomorrow`.
- `upstream` must point to `unicef/airfortomorrow`.
- Never push to `upstream`; push to `origin` only.
- `main` is the clean integration branch that tracks `upstream/main`.
- Keep helper docs and workflow notes on `main`.
- Create feature or issue branches from clean `main`.
- When preparing an upstream PR, cherry-pick only the commits that belong in the PR branch.
- Keep helper-only commits out of upstream PR branches by selective cherry-pick, not by maintaining a separate helper branch.

Recommended safety setup:

```bash
git remote set-url origin git@github.com:AnthonyMockler/airfortomorrow.git
git remote add upstream git@github.com:unicef/airfortomorrow.git
git remote set-url --push upstream DISABLED
git config remote.pushDefault origin
```

## Issue and PR Workflow

- Follow `ISSUE_CREATION_GUIDELINES.md` for repo task or improvement issues.
- Standard issue structure: `Problem` -> `Desired outcome` -> `Constraints / notes` -> `Done when` -> `Verification`.
- Before taking an issue, confirm it is open, unassigned, and not already active.
- For issue work, start in a clean worktree and a dedicated branch named `codex/issue-<id>-<slug>`.
- Read the full issue, including constraints, done criteria, verification steps, and out-of-scope notes.
- Keep scope tied to the issue; do not add opportunistic refactors unless required.
- Validate every `Done when` item and run the listed verification before opening a PR.
- PRs should target `unicef/airfortomorrow:main`, include test evidence, and link the issue with `Closes #<id>` when appropriate.
- After opening the PR, post an issue update summarizing what changed, key decisions, tradeoffs, and the PR link.

## Commands for Issue Work

```bash
gh issue view <id> --repo AnthonyMockler/airfortomorrow
git fetch --all --prune
git worktree add ../airfortomorrow_issue<id> -b codex/issue-<id>-<slug> upstream/main
```
