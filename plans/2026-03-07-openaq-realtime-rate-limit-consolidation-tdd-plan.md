# Plan: OpenAQ Realtime Rate-Limit Consolidation (Design + TDD Plan)

## Status
Closed on 2026-03-08 by maintainer decision. Remaining refinements are deferred.

## Feature Goal
Reduce realtime OpenAQ collection wall time by removing duplicated throttling logic while preserving API safety and data completeness.

## Current Runtime Findings
- Realtime flow is `scripts/run_complete_pipeline.sh` -> `src/run_complete_pipeline.py` -> `scripts/collect_openaq_realtime.sh` -> `src/data_processors/openaq_realtime_client.py`.
- `src/data_processors/openaq_realtime_client.py` currently applies:
- `MAX_WORKERS = 2` and `BATCH_SIZE = 10` hardcoded.
- `time.sleep(2.0)` before every sensor request.
- `time.sleep(5.0)` between every batch.
- `time.sleep(60)` on explicit 429 handling.
- `time.sleep(60)` on generic exception retry path.
- User report observed OpenAQ as the final long-running collector while other pipelines had already completed.
- The wrapper exposes `--timeout` but does not directly enforce it in the collector script.

## Design Direction
- Keep one source of truth for rate limiting and retry behavior in the realtime path.
- Use configuration-backed limits for concurrency, retries, and request timeout.
- Prefer adaptive waiting from server signals (for example, `Retry-After`) over fixed sleeps.
- Remove proactive fixed sleeps that are not tied to real API feedback.

## Red
1. Add Behave coverage for bounded realtime OpenAQ behavior:
- Scenario for `scripts/collect_openaq_realtime.sh --test-mode --limit N` that validates command success and log output structure.
- Scenario that verifies timeout behavior is explicit and deterministic when OpenAQ collection exceeds configured timeout.
2. Add focused Python tests for retry policy helper:
- Retries on 429 and selected transient failures.
- Does not retry on non-retryable 4xx.
- Honors `Retry-After` when present.
3. Run smallest targeted test commands and capture failing evidence before implementation.

## Green
1. Consolidate policy in one layer in `src/data_processors/openaq_realtime_client.py`:
- Remove fixed per-request delay.
- Remove fixed per-batch delay.
- Replace fixed 60-second waits with policy-driven backoff and jitter.
2. Make realtime client settings config-driven:
- Wire `max_workers`, `batch_size`, retry parameters, and timeout from `config/config.yaml` through `ConfigLoader` or explicit config read path.
3. Improve client lifecycle:
- Reuse OpenAQ client per worker thread instead of creating a new client for each sensor request.
4. Clarify timeout ownership:
- Either enforce `--timeout` in `scripts/collect_openaq_realtime.sh` or remove that flag from script help and rely solely on pipeline timeout.
5. Add runtime summary logging:
- Total requests, retries, 429 count, timeout count, and total collection duration.

## Proposed Config Contract
Add OpenAQ realtime policy keys under `data_collection.openaq`:
- `max_workers`
- `batch_size`
- `request_timeout_seconds`
- `retry.max_attempts`
- `retry.base_delay_seconds`
- `retry.max_delay_seconds`
- `retry.jitter_seconds`
- `retry.retryable_status_codes`
- `retry.respect_retry_after`

## Regression Safety
1. Re-run targeted Behave scenarios for quickstart wrappers and OpenAQ realtime path.
2. Validate output parity on bounded test runs:
- Non-empty parquet produced.
- Comparable sensor coverage versus baseline for same time window and location cap.
3. Re-run relevant quickstart regression scenarios that assert artifact creation and log integrity.

## Success Criteria
- Realtime OpenAQ collection duration improves materially in like-for-like runs (target: at least 35 percent faster on the same bounded test profile).
- Retry and rate-limit behavior remains stable with no increase in hard collector failures.
- Timeout semantics are unambiguous and reflected correctly in logs and exit codes.
- Output data remains schema-compatible and coverage remains within expected variance.

## Evidence to Capture
- Commands used for red and green runs.
- Before/after duration snapshots for identical bounded OpenAQ runs.
- Log excerpts showing retry behavior and summary counters.
- Behave results for updated scenarios.
- Final diff scoped to OpenAQ realtime collector path and related config/docs.

## Implementation Order
1. Tests and scenario updates (red).
2. Policy consolidation and config wiring (green).
3. Timeout semantics cleanup and logging improvements.
4. Regression pass and evidence capture.
