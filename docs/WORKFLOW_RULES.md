# Workflow Rules

## Plans and Decisions

- Track work in markdown plans under `plans/`.
- Before implementation, claim an existing plan or create a new one.
- Update the plan status immediately so other agents can see it is active.
- Add the active agent, start date, last updated date, and a short scope note near the top.
- Create a short decision note in `decisions/` for executable behavior or workflow changes.
- Use the plan as the running record for commands, failures, decisions, and verification evidence.

## Test-First Workflow

For workflow, CLI, and contract behavior changes:

1. Document the change in the plan and decision note.
2. Write or update the Behave scenario first.
3. Run the smallest targeted slice and capture the RED failure.
4. Implement the minimum change that turns the scenario green.
5. Re-run the targeted slice and relevant regression coverage.

For narrower implementation changes with a clear function or module seam, start with `./scripts/run_tests.sh` and add or update Behave only if the user-visible workflow contract changed.

Docs-only changes can skip Behave if they do not change executable behavior.

## Verification Rules

- Use Behave for workflow behavior rather than relying on ad hoc manual shell runs.
- Ensure tests validate fresh artifacts from the current run.
- Prefer explicit errors for invalid mode and flag combinations.
- Record the actual commands run and the core pass or fail signal in the plan.

## Git Rules

- `origin` should point to `AnthonyMockler/airfortomorrow`.
- `upstream` should point to `unicef/airfortomorrow`.
- Never push to `upstream`; push to `origin` only.
- Keep `main` clean for integration and cherry-pick helper-only commits when preparing upstream PR branches.
- Keep helper docs and workflow notes out of upstream-facing PR branches unless they belong there.

## Commit Phasing

When work changes executable behavior, prefer separate commits for:

- docs and decision scaffolding
- test changes
- implementation changes

For this harness rollout, Phase 0 and Phase 1 are intentionally separate commits so they can be reverted independently.

## Anti-Patterns

- running `src/` modules directly instead of using wrapper scripts
- treating shell-only validation as a substitute for Behave acceptance coverage
- letting stale files satisfy output assertions
- silently accepting invalid mode-specific arguments
