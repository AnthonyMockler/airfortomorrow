# Decision

Adopt a phased harness-engineering rollout in Air for Tomorrow, starting with two low-risk repository-facing steps:

- Phase 0: freeze the first-pass operating principles and which ones are blocking versus advisory
- Phase 1: shorten root `AGENTS.md` and move durable repository knowledge into a focused `docs/` structure

The first implementation pass will preserve the current shell-wrapper-first and Behave-first workflow. It will improve how the repo communicates and enforces that workflow before changing CI shape, runtime artifacts, or pipeline behavior.

# Why

The repository already has many of the right ingredients for agent-friendly development: shell wrappers, plan-driven work tracking, decision notes, and Behave workflow coverage. The problem is that these are still spread across a long root `AGENTS.md`, scattered review logs, and convention-heavy guidance that is not yet encoded into durable knowledge surfaces or mechanical checks.

A phased rollout is the safest way to improve this. Phase 0 establishes the rules that matter most. Phase 1 makes the repository faster for an agent or contributor to load without touching executable behavior. Later phases can then add enforcement, manifests, and CI layering on top of clearer repository knowledge.

This decision also limits risk by treating the first rollout slice as docs-and-governance work only. That gives the team a chance to refine the operating model before guardrails start failing builds.

# Change Scope

- Add a decision note that freezes the first-pass golden principles for harness adoption.
- Record which first-pass rules are blocking and which remain advisory.
- Update the active plan to reflect that Phase 0 and Phase 1 are the approved working slice.
- Reorganize root knowledge so `AGENTS.md` becomes a short map and policy index.
- Add a small `docs/` knowledge base for durable repository guidance:
  - repo map
  - architecture
  - data flow
  - workflow rules
  - test harness usage
  - source contracts
  - reliability and operations
  - harness adoption context
- Keep these steps in separate commits so either phase can be reverted independently.

First-pass blocking rules:

- executable workflow changes require a plan and a decision note
- workflow behavior changes require Behave coverage or an explicit documented exemption
- user-facing execution paths should go through wrapper scripts in `scripts/`
- tests and contracts must validate artifacts from the current run rather than stale files
- invalid mode or flag combinations must fail explicitly

First-pass advisory rules:

- wrapper scripts should converge on shared helpers where practical
- root docs and deeper docs should remain synchronized as the docs tree evolves
- stale `In Progress` plans should be surfaced and cleaned up regularly
- structured manifests should be added progressively rather than required everywhere immediately

# Non-Goals

- Do not change pipeline behavior, wrapper semantics, or data-processing logic in Phase 0 or Phase 1.
- Do not add CI-blocking guardrail scripts in this slice.
- Do not add structured run manifests in this slice.
- Do not redesign the test suite away from Behave or away from Docker-backed execution.
- Do not broaden scope into source-specific performance or architecture refactors.
