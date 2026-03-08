# Plan: OpenAQ SDK Rate-Limit Alignment (Iteration 1)

## Status
Closed on 2026-03-08 by maintainer decision. Remaining refinements are deferred.

## Context Review
- Existing plan `2026-03-07-openaq-realtime-rate-limit-consolidation-tdd-plan.md` already identifies duplicate sleeps/retries and proposes consolidation.
- Existing plan `2026-03-07-openaq-live-10pct-benchmark-scenario-tdd-plan.md` gives us a realistic live benchmark gate.
- Existing OpenAQ contract coverage is in place (`@openaq` scenarios).
- Current benchmark evidence: baseline locations `738`, sample limit `74` (1/10), reported duration `142.98s`, successful sensors `61`.

## External Source Notes
- OpenAQ SDK docs state response headers expose rate-limit values (`x_ratelimit_limit`, `x_ratelimit_remaining`, `x_ratelimit_reset`) and the SDK tracks them internally.
- OpenAQ API docs state rate limits are scoped to API key and provide reset semantics through headers.
- SDK exceptions separate client-side `RateLimitError` from server-side `HTTPRateLimitError` (429).
- SDK inspection in container (`openaq==0.4.0`) confirms:
  - rate-limit state is stored on client instance fields (`_rate_limit_remaining`, `_rate_limit_reset_datetime`).
  - sync client checks this state before request and updates it after request.
  - no explicit thread synchronization is present around that mutable state.

## Feature Goal
Refactor OpenAQ realtime collection to rely on SDK-native rate-limit awareness and reset timing, removing ad hoc throttling so requests are respectful but as fast as allowed.

## Design Principles
- Single source of truth for request pacing in realtime OpenAQ path.
- No fixed sleeps unless derived from reset information or explicit backoff policy.
- Respect API-key-scoped limits globally, even when parallel processing is enabled.
- Keep output schema and CLI surface unchanged.

## Architecture Decision (This Iteration)
- Keep worker concurrency for orchestration only.
- Introduce one shared, thread-safe API gateway object in realtime collector path:
  - owns one `OpenAQ` client instance for measurements (`from openaq import OpenAQ`).
  - serializes actual API calls through a lock (single API call in flight).
  - reads SDK-managed rate state after each request and enforces reset-aware wait.
  - catches `RateLimitError` / `HTTPRateLimitError` and reschedules next allowed request time.
- Rationale:
  - per-request client construction loses SDK rate-limit continuity.
  - per-thread clients do not reflect key-scoped global budget.
  - lock-based gateway removes race risk in SDK client mutable rate-limit state.
  - `get_single_sensor_data` should remain a thin contract-preserving transform layer (fetch + normalize + schema) with no local sleep/retry policy.

## Red
1. Add/adjust Behave scenarios before implementation:
- Keep existing `@openaq @live @benchmark` scenario as primary runtime gate.
- Add one focused contract scenario that ensures rate-limit retry behavior is visible in logs and non-fatal in normal operation.
2. Add focused Python tests for SDK error handling wrapper:
- `RateLimitError` handling path.
- `HTTPRateLimitError` handling path.
- reset-based wait calculation path.
3. Run smallest targeted Docker Behave command and targeted Python tests to confirm failing baseline before refactor.
4. Capture fresh pre-change benchmark duration from `@openaq @benchmark` run for direct before/after comparison.

## Green
1. Realtime request path cleanup in `src/data_processors/openaq_realtime_client.py`:
- Remove proactive per-request sleep and per-batch sleep.
- Remove generic fixed 60-second wait paths.
- Stop creating a new OpenAQ client for every sensor request.
2. SDK-aligned pacing model:
- Use shared coordinator (gateway) so all worker calls respect one API-key budget.
- Use SDK-managed rate state as primary signal (`remaining` + reset window from client state).
- On `RateLimitError` or `HTTPRateLimitError`, set `next_allowed_time` from reset semantics plus small jitter and retry.
3. Concurrency model:
- Keep worker pool for task orchestration, but gate actual API calls through one rate-aware control point.
- Make concurrency configurable and start conservative for first pass.
4. Timeout and retry semantics:
- Keep retries targeted to retryable failures only.
- Ensure timeout ownership is explicit (script vs orchestrator) and consistent.
5. Observability:
- Add structured summary at end of run:
  - requests attempted
  - retries
  - rate-limit exceptions
  - total wait-for-reset time
  - wall-clock duration

## Regression Safety
1. Re-run:
- `./scripts/run_behave_tests.sh -- --tags=@openaq --tags=~@live`
- `./scripts/run_behave_tests.sh -- --tags='~@__never__' --tags=@openaq --tags=@benchmark`
2. Validate output parity:
- required parquet columns unchanged
- non-empty output in live benchmark scenario
- no new auth/credential failures in logs
3. Guard against hidden behavior change:
- verify same output filename contract and CLI flags.

## Success Criteria
- Live benchmark scenario remains green and faster than current baseline.
- Expected first-pass target: at least 20 percent reduction from fresh pre-change benchmark on the same `@benchmark` scenario.
- No increase in hard failures from rate limiting.
- No regression in OpenAQ CLI contract scenarios.
- Output data remains schema-compatible for downstream processors.

## Evidence to Capture
- Before/after benchmark durations using the same `@benchmark` scenario.
- Before/after rate-limit wait and retry counters from logs.
- Behave pass/fail summaries for OpenAQ tag set.
- A short decision note update if architecture choice changes (for example shared client vs coordinator wrapper).

## Open Questions For Next Iteration
- Should we keep any explicit client-side limiter as a safety cap below hard API limits, or rely entirely on SDK exceptions + reset handling?
- Do we need separate policies for location discovery calls vs measurement calls?

## Self Review (Post-Conversation)
- Strengths:
  - aligns directly with your preferred approach: parallel orchestration + single shared rate-aware API path.
  - explicitly addresses why manual sleeps were originally added (parallel workers with fragmented rate-limit state).
  - uses existing live benchmark and contract tests for both correctness and speed validation.
- Risks:
  - serializing API calls could underutilize available rate budget if wait calculation is too conservative.
  - SDK private state usage is version-sensitive.
- Mitigations:
  - keep pacing logic isolated in gateway wrapper for easy tuning.
  - log pacing decisions (`remaining`, `reset`, wait applied) for calibration.
  - lock correctness and retry semantics validated by targeted tests plus benchmark comparison.
  - keep worker threads for orchestration so call sites and batch processing behavior remain stable while request pacing semantics move to one shared control path.
