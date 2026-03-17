# Decision

Adopt strict Tier A/B/C Behave execution in `scripts/run_behave_tests_compact.sh` and require explicit `@tier_a`, `@tier_b`, or `@tier_c` tags on every Behave scenario.

# Why

Ad-hoc tag filtering made it too easy to run partial suites that looked green while silently skipping scenarios. Tiered execution reduces ambiguity, prevents accidental coverage gaps, and ensures failures are surfaced immediately.

# Change Scope

- Convert the compact Behave runner to accept fixed inputs (`--tier`, optional fixed `--scope`) instead of arbitrary Behave passthrough arguments.
- Discover scenario selectors directly from feature files and run exact selectors through Docker.
- Enforce strict outcome checks per tier run:
  - zero skipped scenarios
  - observed scenario count must equal selected scenario count
  - non-zero Behave exit codes fail immediately
- Add explicit tier tags across all feature scenarios and validate tier consistency with `@live` / `@slow` semantics.
- Update smoke runner, AGENTS guidance, and Behave contracts to use the tiered interface.

# Non-Goals

- Do not remove `scripts/run_behave_tests.sh`; keep it for full raw output debugging.
- Do not rewrite existing scenario assertions or data contracts beyond tier classification and runner behavior.
