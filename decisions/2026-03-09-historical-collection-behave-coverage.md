# Decision: Historical Collection Behave Coverage

## Date
2026-03-09

## Decision
Add focused Behave coverage for the documented historical data-collection workflow before optimizing historical collector performance.

## Why
- Historical mode exercises different code paths than realtime for Air Quality, FIRMS, Himawari, and ERA5.
- Existing coverage already protects several realtime paths and some historical argument guards, but it does not yet validate fresh historical collection artifacts from the documented user workflow.
- Performance work on historical collectors needs a user-visible contract so refactors do not silently break output shape, artifact freshness, or documented commands.

## Change Scope
- Start from the README historical workflow and the linked detailed documentation.
- Define a plaintext BDD scenario for historical data collection first.
- In the next phase, translate that scenario into bounded Behave coverage for the historical collector wrappers and artifact contracts.
- Reuse existing generic CLI/filesystem Behave steps where possible and add only the collector-specific assertions that are missing.

## Non-Goals
- No production collector or pipeline changes in this planning pass.
- No Behave feature or step-definition implementation in this pass.
- No expansion into silver-dataset or prediction coverage yet.
- No broad full-range historical benchmark runs; initial coverage should stay bounded to a small date range.
