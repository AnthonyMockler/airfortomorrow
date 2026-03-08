# Decision: OpenAQ Live 10%-Sample Benchmark Scenario

## Date
2026-03-07

## Decision
Add a dedicated live Behave scenario for OpenAQ realtime collection that runs against a dynamic sample sized at one tenth of the current live OpenAQ location list.

## Why
- We need a realistic optimization target that uses live data and enough workload to expose meaningful runtime differences.
- Full OpenAQ realtime runs are too long and expensive for iterative optimization loops.
- Very small test-mode caps (for example single-digit location limits) are too synthetic to represent production behavior.

## Change Scope
- Add a new OpenAQ live benchmark scenario in Behave.
- Compute sample size dynamically from current live location count (`ceil(total_locations / 10)` with a minimum floor).
- Validate command contract, data contract, and reported runtime signal in that sampled run.
- Run the new OpenAQ-focused scenario via Docker Behave harness.

## Non-Goals
- No production collector/processor behavior changes.
- No retry/rate-limit policy changes.
- No non-OpenAQ benchmark scenario additions.
