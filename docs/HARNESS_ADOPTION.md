# Harness Adoption History

## Summary

The repository trialed a split-doc harness model in early March 2026 by moving substantial operating guidance out of `AGENTS.md` into many focused files under `docs/`.

After usage feedback, the team observed higher context loss and more execution mistakes from agents. The operating model was therefore re-consolidated so `AGENTS.md` is again the primary guidance surface.

## Current State

- `AGENTS.md` is the canonical day-to-day operating guide.
- `docs/` remains as optional deep reference material.
- Workflow and test rules are kept concise and aligned to avoid conflicting guidance across files.

## What Stayed

The rollback kept useful instruction improvements introduced during the harness trial:

- clearer Behave vs pytest selection rules
- explicit long-run command handling expectations
- artifact freshness and fail-fast CLI validation emphasis
