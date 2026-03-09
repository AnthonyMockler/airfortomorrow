# Repository Docs

This directory holds durable repository knowledge that used to be concentrated in the root `AGENTS.md`.

Use `AGENTS.md` for the short operating map. Use the docs here when you need detail on one part of the system.

## Start Here

- Need the top-level shape of the repo: `REPO_MAP.md`
- Need architecture and configuration rules: `ARCHITECTURE.md`
- Need the pipeline flow and artifact layout: `DATAFLOW.md`
- Need workflow and git rules: `WORKFLOW_RULES.md`
- Need test execution guidance: `TEST_HARNESS.md`
- Need source-specific constraints: `SOURCE_CONTRACTS.md`
- Need runtime troubleshooting: `RELIABILITY_AND_OPERATIONS.md`
- Need rollout context for the harness work itself: `HARNESS_ADOPTION.md`

## Directory-Specific Notes

- `scripts/AGENTS.md`: Bash wrapper conventions
- `src/AGENTS.md`: Python implementation notes
- `tests/AGENTS.md`: Behave authoring and runtime testing guidance

## How To Use This Docs Set

- Read the smallest file that answers the task.
- Prefer links over duplicating rules across multiple docs.
- Keep durable rules here, not in ad hoc chat context or review-only notes.
- If executable behavior changes, update the relevant docs in the same change.
