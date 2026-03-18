# Subagent Scope And Contract Gates

- Date: 2026-03-18
- Status: Accepted

## Context

During the parquet-pipeline rebuild, a worker branch expanded CLI contract coverage but also introduced an unrelated production H3 compatibility patch. The branch was green, but the coverage was for the wrong behavior:

- the dependency contract was not updated
- the new production path was not protected by a RED test for the intended API
- the fix solved the current environment mismatch instead of aligning the implementation with the locked design

This is exactly the kind of drift that can slip through when subagents are allowed to widen scope while chasing a failing test.

## Decision

We will add explicit process gates for future phases:

1. Workers must stay inside the declared write scope and behavioral scope.
2. If a task uncovers an unrelated production bug or dependency mismatch, the worker must treat it as:
   - a blocker to surface, or
   - a separately declared fix with its own RED/GREEN cycle and explicit scope expansion.
3. If a change touches a dependency/API contract, the same branch must update the dependency declaration and add a RED test for the intended contract, not just a workaround for the current environment.
4. Green tests are not sufficient by themselves. Review must check that:
   - the code matches the locked design
   - the dependency contract is aligned
   - the new tests cover the intended behavior, not a fallback or accidental workaround

## Implications

- “Coverage exists” is no longer enough; it must be coverage for the right requirement.
- Environment-specific compatibility hacks should not be merged when the real requirement is to pin and use the intended dependency/API.
- Unexpected runtime failures found during contract work should usually split into a new bounded fix branch unless the scope expansion is made explicit and tested correctly.
