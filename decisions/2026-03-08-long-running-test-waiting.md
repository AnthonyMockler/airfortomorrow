# Decision

Add explicit long-running test waiting guidance to the root `AGENTS.md` so agents start long Behave or pipeline runs once, wait for completion, and avoid frequent polling or interim narration by default.

# Why

Long-running test and pipeline commands can run for tens of minutes to over an hour. Frequent polling and repeated commentary consume tokens without producing new diagnostic value. A repo-local instruction gives agents a clear default behavior for these runs.

# Change Scope

- Update root `AGENTS.md` with a long-running test command policy.
- Require agents to prefer the compact Behave shim for long runs.
- Set a default polling interval and restrict interim updates and log tailing unless the user explicitly asks.
- Add Behave contract coverage for the new instruction text.

# Non-Goals

- Do not change the execution behavior of the compact shim or raw Behave harness.
- Do not add scheduling or background job machinery.
- Do not rewrite nested `AGENTS.md` files in this change.
