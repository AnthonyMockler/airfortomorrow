# Decision

Add a repository-local compact Behave shim at `scripts/run_behave_tests_compact.sh` backed by a self-contained repo implementation, and update root `AGENTS.md` to prefer that shim for routine Behave runs.

# Why

The existing Docker Behave harness is the correct execution path, but its raw output is too verbose for agent-driven iteration. A repo-local shim gives agents a stable, discoverable command in the workspace itself instead of relying on a user-home skill path that is not available inside Docker or to every agent context.

# Change Scope

- Add a compact Behave wrapper under `scripts/` that preserves the existing Docker harness and emits concise summaries.
- Add a shell shim entrypoint that agents can invoke with one command.
- Update root `AGENTS.md` so agents prefer the compact shim by default and fall back to the raw harness only when full output is explicitly needed.
- Add Behave coverage for the shim help contract and the root agent guidance.

# Non-Goals

- Do not change the behavior or defaults of `scripts/run_behave_tests.sh`.
- Do not rewrite the repository logging strategy or Behave test structure.
- Do not add README-facing public documentation for the compact shim in this change.
