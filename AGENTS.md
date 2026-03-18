# Project Knowledge Base

Air for Tomorrow predicts PM2.5 on an H3 grid using ground sensors (OpenAQ, AirGradient), fire detections (NASA FIRMS), AOD (Himawari), and ERA5 meteorology.

## Purpose

- Produce daily PM2.5 estimates for Thailand and Laos, especially where sensor coverage is sparse.
- Main outputs:
  - `data/processed/` source parquet files
  - `data/silver/` feature tables
  - `data/predictions/data/` prediction parquet files

## Quick Map

- `scripts/`: only supported user-facing entrypoints
- `src/`: collectors, processors, silver assembly, prediction
- `features/`: Behave workflow and contract coverage
- `config/config.yaml`: central config
- Key entrypoints: `src/run_complete_pipeline.py`, `src/make_silver.py`, `src/predict_air_quality.py`

## Core Rules

- Use wrapper scripts in `scripts/`; do not run `src/` modules directly.
- Use `ConfigLoader` (Python) and `scripts/utils/config_reader.sh` (Bash) for config access.
- Prefer explicit errors for invalid mode/flag combinations.
- Ensure checks validate fresh artifacts from the current run.
- Push to `origin` only, never `upstream`.

## Workflow (lightweight by default)

- Small/local changes: no required `plans/*.md`; record commands and verification in commit/PR notes.
- Workflow/CLI/contract changes: add a decision note in `decisions/`; add a plan only when work is multi-step, cross-layer, or likely to span sessions.
- High-risk or cross-source changes: decision note + plan required.
- Docs-only changes with no behavior change can skip Behave, plans, and decisions.

## Worktrees And Branches

- For large breaking changes or cross-layer rebuilds, keep `main` runnable and deployable.
- Do implementation in isolated git worktrees on `codex/...` branches rather than directly on `main`.
- Prefer one bounded concern per worktree when practical.
- Keep design/doc iteration separate from implementation branches when possible.
- If you are starting a new implementation thread or subagent task, use the `using-git-worktrees` skill before writing code.
- Do not point two coding agents at the same editable worktree at the same time.
- Read-only review/exploration may inspect another implementation worktree, but only the owning coding agent should edit there.
- If a task needs to continue work from an existing implementation branch, either:
  - work in that branch as the sole coding agent, or
  - create a fresh worktree from the latest clean commit on that branch for your own bounded task.
- Keep each coding agent responsible for a clearly defined write set and report branch/worktree path in status updates.

## Test-First Rules

- Workflow/CLI/contract behavior: write or update Behave first and capture RED before implementation.
- Narrow Python logic with stable seams: start with `./scripts/run_tests.sh`; add Behave only if user-visible workflow behavior changed.
- Implement minimal GREEN change, then rerun targeted and regression coverage.

## Scope And Contract Discipline

- Stay inside the declared task scope and write set. Do not widen a branch from “contract coverage” into “production compatibility fix” unless that scope change is made explicit.
- If a task uncovers an unrelated production bug or dependency mismatch, either:
  - stop and report it as a blocker, or
  - split it into a clearly declared follow-on fix with its own RED/GREEN cycle.
- Do not patch around a dependency/API mismatch when the real requirement is to align the dependency contract itself.
- If you change code that depends on a specific library/API contract, update the dependency declaration in the same branch and add a RED test for the intended contract.
- Test the intended behavior, not a fallback workaround that only matches the current environment.
- Review must check not just that tests are green, but that:
  - the code matches the locked design
  - the dependency/version contract is aligned
  - the new tests cover the intended behavior

## Verification Evidence

- No coding task is complete without explicit GREEN evidence from the relevant test or verification commands.
- Do not report `DONE`, `fixed`, `passing`, or equivalent unless you have actually run the verification commands and seen them pass.
- Status reports must include the exact verification commands that were run and a short result summary such as `9 passed` or `1 feature passed`.
- Narrative-only claims like "should pass", "looks good", or "implemented but not verified" do not count as completion.
- If verification is blocked by an unrelated failure, report `BLOCKED` and name the blocking command and failure clearly.
- If a worker has RED only and no GREEN, treat the task as unfinished.
- When another agent's work is important to current decisions, prefer rerunning the relevant verification yourself instead of trusting an unverified summary.

## Test Commands

- Behave default (Tier A): `./scripts/run_behave_tests_compact.sh --tier a`
- Behave Tier B (live, non-slow): `./scripts/run_behave_tests_compact.sh --tier b`
- Behave Tier C (slow): `./scripts/run_behave_tests_compact.sh --tier c`
- Behave all tiers (A then B then C): `./scripts/run_behave_tests_compact.sh --tier all`
- Behave raw output/debug: `./scripts/run_behave_tests.sh` only when full raw output is explicitly needed.
- pytest: `./scripts/run_tests.sh` (do not run pytest directly on host)
- smoke: `./scripts/smoke_test.sh`
- Tier runs must not rely on ad-hoc tag forwarding.

## Long-Run Commands (10+ min expected)

- Start once and record log path.
- Prefer `./scripts/run_behave_tests_compact.sh --tier c --long-run` for slow Behave runs.
- Do not poll/tail/status-update more often than every 5 to 10 minutes unless run state materially changes.

## Minimal Plan Template (only when needed)

```md
# <Short Title>

- Status: Planned | In Progress | Blocked | Complete
- Owner: <agent or person>
- Last Updated: YYYY-MM-DD

## Goal
## Red
## Green
## Verification
## Notes
```

## Optional Deep References

- `docs/REPO_MAP.md`
- `docs/ARCHITECTURE.md`
- `docs/DATAFLOW.md`
- `docs/SOURCE_CONTRACTS.md`
- `docs/RELIABILITY_AND_OPERATIONS.md`
