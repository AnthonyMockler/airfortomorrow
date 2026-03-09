# Plan: Harness Engineering Workflow Adoption

- Status: In Progress
- Owner: Codex
- Active Agent: Codex (GPT-5)
- Started: 2026-03-09
- Last Updated: 2026-03-09
- Scope Note: Convert the repo's existing plan-driven and Behave-based workflow into a more explicit harness-engineering system with short repo maps, durable in-repo knowledge, mechanical enforcement, agent-readable validation artifacts, and scheduled cleanup. The currently approved implementation slice is limited to Phase 0 and Phase 1.

## Feature Goal

Adopt the useful parts of the harness-engineering workflow described in the OpenAI article in a way that fits this repository's current structure, external-data constraints, and Behave-first testing model.

The target state is a repository where:

- the key operating model is easy for an agent or human to load quickly
- durable project knowledge lives in versioned files instead of chat context
- important architectural and workflow rules are enforced by scripts and CI rather than left as prose only
- wrapper runs emit machine-readable evidence that is cheaper to inspect than free-form logs
- CI is split into fast blocking checks and slower scheduled verification
- the workflow can later be copied into other UNICEF and non-UNICEF repos with minimal changes

## Scope Guardrails

- The current approved slice is docs-and-governance only. Do not modify executable behavior in Phase 0 or Phase 1.
- Preserve the current shell-wrapper-first workflow; do not redesign the repo around direct `src/` invocation.
- Preserve Behave as the default acceptance-harness style for workflow and contract coverage.
- Do not weaken current safeguards around fresh artifacts, Docker-backed test execution, or live-source separation.
- Keep the first implementation pass focused on repository ergonomics, validation surfaces, and CI structure rather than broad pipeline refactors.
- Avoid introducing heavy platform dependencies when a shell or Python repo-local check is sufficient.
- Keep external-service usage bounded. Scheduled live checks should be intentional and sparse.

## Current State Snapshot

The repository already has several strong harness-like elements:

- a high-signal root knowledge file in [`AGENTS.md`](/Users/anthonymockler/Documents/unicef/airfortomorrow/AGENTS.md)
- documented plan and decision workflows in `plans/` and `decisions/`
- a strong shell-wrapper convention rooted in [`scripts/run_complete_pipeline.sh`](/Users/anthonymockler/Documents/unicef/airfortomorrow/scripts/run_complete_pipeline.sh)
- Behave-based workflow and contract coverage in `features/`
- an agent-friendly Behave output shim in [`scripts/run_behave_tests_compact.py`](/Users/anthonymockler/Documents/unicef/airfortomorrow/scripts/run_behave_tests_compact.py)
- a GitHub Actions entrypoint in [`.github/workflows/tests.yml`](/Users/anthonymockler/Documents/unicef/airfortomorrow/.github/workflows/tests.yml)

The main gaps relative to the desired workflow are:

- `AGENTS.md` currently mixes repo map, durable policy, and detailed procedural guidance into one long file
- many rules are written down but not mechanically enforced
- wrapper runs mostly expose free-form log files rather than compact structured manifests
- CI currently has one main Behave job and does not yet separate fast repository guardrails from slower workflow checks
- there is no explicit recurring cleanup loop for docs drift, stale plans, or harness hygiene
- there is no reusable "starter kit" for applying the same workflow to other repos

## Implementation Strategy

Implement in ordered phases so each layer creates leverage for the next one.

### Phase 0: Baseline, Approval, and Decision Capture

Goal: lock the scope before touching enforcement or docs structure.

Deliverables:

- Review and approve this plan.
- Create a decision note in `decisions/` once the approach is approved.
- Define the first-pass "golden principles" that the repo will enforce mechanically.
- Record which rules are blocking versus advisory.

Proposed first-pass golden principles:

- Use shell wrappers in `scripts/` for user-facing execution paths.
- Use `ConfigLoader` in Python and `scripts/utils/config_reader.sh` in Bash for config access.
- For executable workflow changes, require a plan and decision note.
- For workflow behavior, require Behave coverage or an explicit documented exemption.
- Ensure tests and contract checks validate artifacts from the current run, not stale files.
- Fail explicitly on invalid mode/flag combinations instead of silently accepting them.

Recommended first-pass enforcement split:

- Blocking from the first implementation pass:
  - executable workflow changes require a plan and decision note
  - workflow behavior changes require Behave coverage or an explicit documented exemption
  - user-facing execution paths must go through wrapper scripts in `scripts/`
  - tests must prove current-run artifact freshness rather than passing on stale files
  - invalid mode/flag combinations must fail explicitly
- Advisory in the first implementation pass:
  - wrapper scripts should use shared helpers consistently where practical
  - root docs and deeper docs should remain synchronized as the docs tree evolves
  - stale `In Progress` plans should be reported before they become hard CI failures
  - manifest support should be rolled out progressively rather than required everywhere on day one

Validation:

- Agreement on scope, enforcement list, and rollout order.

Exit criteria:

- Decision note drafted and accepted.
- Golden principles list frozen for first implementation pass.

### Phase 1: Reorganize Repository Knowledge Surfaces

Goal: make the repo easier for an agent to load quickly without losing important detail.

Deliverables:

- Trim root [`AGENTS.md`](/Users/anthonymockler/Documents/unicef/airfortomorrow/AGENTS.md) into a shorter map and policy index.
- Create a small `docs/` structure for durable knowledge that does not belong in `AGENTS.md`.
- Add a single landing document that links the knowledge surfaces together.

Proposed docs structure:

- `docs/README.md`
- `docs/REPO_MAP.md`
- `docs/ARCHITECTURE.md`
- `docs/DATAFLOW.md`
- `docs/WORKFLOW_RULES.md`
- `docs/TEST_HARNESS.md`
- `docs/SOURCE_CONTRACTS.md`
- `docs/RELIABILITY_AND_OPERATIONS.md`
- `docs/HARNESS_ADOPTION.md`

Recommended content split:

- `AGENTS.md`: short repo map, mandatory operating rules, entrypoint commands, links to deeper docs
- `REPO_MAP.md`: directories, primary entrypoints, how the shell and Python layers connect
- `DATAFLOW.md`: collectors -> processors -> silver -> prediction, plus key artifact directories
- `WORKFLOW_RULES.md`: plan/decision requirements, test-first rules, commit sequencing, anti-patterns
- `TEST_HARNESS.md`: Behave tags, Docker harness usage, when to use compact output, live/slow policy
- `SOURCE_CONTRACTS.md`: data-source expectations and historical/realtime constraints per collector
- `RELIABILITY_AND_OPERATIONS.md`: logs, manifests, common failures, troubleshooting

Implementation notes:

- Keep `AGENTS.md` intentionally short enough to be scanned in one pass.
- Prefer links to deep docs over repeating the same instructions in multiple places.
- Move durable repo knowledge out of ad hoc review logs and into the docs tree where appropriate.

Validation:

- Root `AGENTS.md` still gives enough information for a new agent to act safely.
- Key repo questions can be answered by opening one or two targeted docs instead of scanning one long file.

Exit criteria:

- New docs tree exists.
- `AGENTS.md` is shorter and points cleanly to deeper docs.
- Redundant or stale guidance is removed or consolidated.

### Phase 2: Add Mechanical Repository Guardrails

Goal: turn the most important prose rules into executable checks.

Deliverables:

- Add a repo-guardrail script, likely `scripts/check_repo_guardrails.py` or `scripts/check_repo_guardrails.sh`.
- Add focused checks that are cheap enough to run in CI and locally.
- Add contract coverage where a textual lint is too weak.

Initial checks to implement:

- verify `plans/` and `decisions/` coverage for executable changes
- verify plan headers contain status, owner, started, last updated, and scope fields
- verify new or changed wrapper scripts are referenced from repo docs where expected
- verify documented commands in `README.md` and `DOCUMENTATION.md` still respond correctly to `--help`
- verify anti-pattern rules that are amenable to grep-based detection:
  - direct user-facing docs should not instruct calling `src/` modules directly
  - shell scripts should source or use shared config helpers where applicable
- verify stale `In Progress` plans older than an agreed threshold are flagged

Likely follow-up checks after the first pass:

- detect new wrapper scripts missing corresponding contract or quickstart coverage
- detect features added without a matching step file update when required
- detect docs command examples that have drifted from wrapper syntax

Implementation notes:

- Keep the first version simple and deterministic.
- Distinguish clearly between hard failures and informational warnings.
- Prefer explicit allowlists over fragile heuristics where possible.

Validation:

- Introduce one or two intentionally failing fixtures or controlled cases to prove the guardrails fail for the right reason.
- Document all checks and how to run them locally.

Exit criteria:

- Guardrail script runs locally and in CI.
- Failures are precise enough that contributors can fix them quickly.

### Phase 3: Extend the Acceptance Harness Around Repository Hygiene

Goal: use Behave and contract tests for repository-level workflow guarantees, not just pipeline runtime behavior.

Deliverables:

- Add or extend contract features to validate the new docs-and-guardrails workflow.
- Keep these checks atomic and cheap.

Candidate Behave coverage:

- root docs continue to reference the blessed wrapper commands
- root docs point to the new durable knowledge files
- compact test harness help and defaults remain documented
- any new run-manifest files are created and contain the required schema
- documentation-only exemptions remain explicit and narrow

Implementation notes:

- Use Behave where user-visible workflow behavior matters.
- Use the repo guardrail script where structural checks are cheaper than BDD steps.
- Avoid duplicating the same invariant in too many places.

Validation:

- Run the smallest targeted Behave slices first.
- Keep repository-hygiene scenarios separate from long-running live collector scenarios.

Exit criteria:

- Repo-workflow behavior is validated by a combination of guardrail script and small Behave contracts.

### Phase 4: Add Structured Run Manifests for Wrapper Commands

Goal: make pipeline runs easier for agents and CI to inspect than raw logs alone.

Deliverables:

- Define a small manifest schema written by wrapper scripts.
- Add manifest emission to the main wrapper(s) first, then expand to source-specific wrappers.
- Add manifest-aware test assertions.

Recommended first-pass manifest fields:

- command
- wrapper name
- mode
- countries
- start date
- end date
- start timestamp
- end timestamp
- duration seconds
- exit code
- referenced log path
- artifacts created or updated
- artifact counts
- key warnings or error summary

Recommended storage pattern:

- write alongside existing logs or under a dedicated `logs/manifests/` directory
- use deterministic filenames tied to the wrapper and run timestamp

Why this matters:

- agents can inspect a manifest without parsing many log formats
- CI can assert artifact freshness and basic outcomes with less brittle string matching
- future dashboards or scheduled reports can summarize runs mechanically

Validation:

- Behave or shell-level contract checks confirm manifest creation and required fields
- manifests point only to artifacts from the current run

Exit criteria:

- main wrapper emits manifest
- at least one source-specific wrapper emits manifest
- tests assert manifest presence and schema

### Phase 5: Restructure CI Into Fast Gates and Scheduled Deep Checks

Goal: make merges fast without losing confidence on slower or live-dependent coverage.

Deliverables:

- Expand [`.github/workflows/tests.yml`](/Users/anthonymockler/Documents/unicef/airfortomorrow/.github/workflows/tests.yml) or split it into multiple workflows.
- Define which checks block pull requests and which run on a schedule.
- Update the PR template to require the right evidence for each change type.

Recommended CI split:

- PR blocking:
  - repo guardrail script
  - fast Behave contracts and smoke scenarios that exclude `@slow` and `@live`
  - targeted pytest via `./scripts/run_tests.sh` when relevant
- Scheduled or manually triggered:
  - `@slow` workflow slices
  - carefully selected `@live` scenarios
  - docs drift checks
  - stale-plan and stale-decision hygiene report

Recommended workflow set:

- `repo-guardrails.yml`
- `behave-fast.yml`
- `behave-slow-nightly.yml`
- `live-contracts-scheduled.yml`
- optional `docs-hygiene.yml`

Implementation notes:

- Keep scheduled live checks bounded and explicit about credentials and external dependencies.
- Preserve the current default tag behavior in [`behave.ini`](/Users/anthonymockler/Documents/unicef/airfortomorrow/behave.ini).
- Publish raw-log paths and manifest paths in job summaries where useful.

Validation:

- One example PR should trigger only the fast path.
- One scheduled run should exercise the slow/live path and produce a clear summary.

Exit criteria:

- PRs get fast, relevant blocking feedback.
- slower confidence checks move off the critical merge path without disappearing.

### Phase 6: Add a Recurring Cleanup and Maintenance Loop

Goal: keep the harness from decaying after the first implementation pass.

Deliverables:

- Define a recurring maintenance checklist for plans, decisions, docs drift, and stale checks.
- Implement either a scheduled GitHub Action, a lightweight automation, or both.

Candidate cleanup tasks:

- flag stale `In Progress` plans
- flag orphaned decisions or plans with no related implementation
- flag docs that mention deleted wrappers or old commands
- flag wrapper scripts lacking manifest support after the migration window
- flag contract scenarios that duplicate stronger coverage elsewhere

Implementation notes:

- Start with reporting, not auto-fixing.
- Make every cleanup finding easy to route into a small follow-up PR.

Validation:

- scheduled report produces actionable, low-noise output

Exit criteria:

- there is a repeatable cleanup loop rather than a one-time docs sweep

### Phase 7: Generalize the Pattern for Other Projects

Goal: make this work portable beyond Air for Tomorrow.

Deliverables:

- Create a small reusable playbook from the final Air for Tomorrow implementation.
- Separate repo-specific rules from reusable harness patterns.

Reusable outputs to produce after the local rollout:

- a minimal `AGENTS.md` template
- a reusable plan template for harness adoption
- a guardrail-check checklist that can be adapted per repo
- a manifest-schema template for wrapper-oriented projects
- a CI layering pattern: fast block, slow scheduled, live scheduled

Generalization notes:

- data pipelines need stronger artifact-freshness and live-source boundaries than many app repos
- web apps may replace artifact manifests with browser traces and app metrics
- API repos may replace pipeline artifact checks with schema, trace, and contract outputs

Validation:

- another repo should be able to copy the template set and customize only a short list of repo-specific invariants

Exit criteria:

- reusable documentation exists that is not tightly coupled to Air for Tomorrow internals

## Work Breakdown

Recommended order of execution once this plan is approved:

1. Approve scope and create the decision note.
2. Draft the new docs structure and shorten `AGENTS.md`.
3. Implement the repo guardrail script with a very small initial rule set.
4. Add CI for repo guardrails before broadening the rule set.
5. Add repository-hygiene contract coverage.
6. Add run manifests to the main wrapper and one source-specific wrapper.
7. Extend CI into fast and scheduled lanes.
8. Add cleanup reporting.
9. Extract the reusable playbook for other repos.

## Red

Target RED states for implementation:

- repo guardrail script fails when required plan or decision metadata is missing
- docs contract checks fail when wrapper documentation drifts
- manifest contract checks fail before wrappers emit structured manifests
- CI demonstrates that fast repository checks are isolated from slow/live scenarios

## Green

Target GREEN states for implementation:

- repository guardrails pass on a clean branch with compliant docs and plan metadata
- fast Behave and contract checks pass in PR CI
- main wrapper runs emit both free-form logs and structured manifests
- scheduled workflows cover slow/live verification without blocking normal merges
- the new docs layout makes the operating model faster to load than the current monolithic `AGENTS.md`

## Regression Safety

- preserve existing wrapper entrypoints and command semantics during the first pass
- do not remove current Behave coverage while adding new harness checks
- keep live checks opt-in or scheduled rather than accidentally making PR CI depend on external services
- add new checks in narrow increments so false positives can be corrected before expanding enforcement
- document every new hard-failure rule before enabling it in blocking CI

## Success Criteria

- Root repository guidance is shorter, clearer, and linked to durable supporting docs.
- The repo has at least one executable guardrail check that enforces workflow rules now expressed only in prose.
- CI distinguishes between fast blocking checks and slower scheduled confidence checks.
- The main wrapper workflow emits machine-readable run evidence in addition to logs.
- Contributor-facing docs and PR templates reflect the new workflow.
- A reusable pattern is documented for applying the same approach to other projects.

## Evidence to Capture

- before/after size and structure of `AGENTS.md`
- docs tree and link map
- guardrail script command and failure/pass examples
- Behave contract commands and summaries for repository-hygiene scenarios
- sample run manifest and manifest-schema validation evidence
- CI workflow screenshots or summaries showing fast versus scheduled lanes
- cleanup-report output from at least one scheduled run

## Notes and Findings

- 2026-03-09:
  - User approved proceeding in phased implementation order rather than attempting the full harness rollout at once.
  - Phase 0 and Phase 1 were selected as the first implementation slice.
  - Separate commits are required for Phase 0 and Phase 1 so the repo can roll back either slice independently if the new workflow proves too noisy or too rigid.
  - Phase 1 introduced a `docs/` landing page plus focused durable knowledge files for repo map, architecture, data flow, workflow rules, test harness usage, source contracts, reliability, and harness adoption context.
  - Root `AGENTS.md` was reduced from 167 lines to 72 lines and now acts as a short operating map rather than the full instruction manual.

## Risks and Mitigations

- Risk: too many guardrails create contributor friction.
  - Mitigation: start with a short hard-failure list and keep the rest advisory.
- Risk: manifests drift between wrappers.
  - Mitigation: define one small schema and add fields only when justified.
- Risk: scheduled live checks become noisy due to upstream instability.
  - Mitigation: keep the live set narrow, bounded, and clearly separated from merge blockers.
- Risk: docs sprawl replaces one long file with many stale files.
  - Mitigation: keep the docs set small and add hygiene checks for drift.
- Risk: rule enforcement via grep becomes brittle.
  - Mitigation: prefer explicit file scopes, allowlists, and targeted contract tests.

## Open Questions

- How short should the root `AGENTS.md` be for this repo before it stops being useful?
- Which plan and decision requirements should be hard blockers in CI versus warnings?
- Should the first manifest implementation live in Bash, Python, or a shared helper invoked by wrappers?
- Should slow/live scheduled checks publish summaries as workflow artifacts, markdown job summaries, or both?
- Do we want one shared harness playbook for multiple repos, or should Air for Tomorrow remain the proving ground first?

## Handoff

- Review this plan and confirm the desired phase order.
- Decide whether to implement the docs reorganization and guardrail checks in the same PR or separate phases.
- After approval, create the decision note and begin with Phase 1 and Phase 2 in the smallest viable slice.
