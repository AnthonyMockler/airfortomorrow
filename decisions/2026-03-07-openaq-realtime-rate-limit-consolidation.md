# Decision: OpenAQ Realtime Rate-Limit Consolidation

## Date
2026-03-07

## Decision
Consolidate OpenAQ realtime throttling and retry behavior into one policy layer, and remove duplicate fixed delays that currently exist in multiple places.

## Why
- Realtime OpenAQ collection currently includes multiple fixed sleeps and retry waits in `src/data_processors/openaq_realtime_client.py`, even though the SDK client and collector layer already include rate-limit handling.
- Config values and runtime behavior are misaligned. For example, `config/config.yaml` sets higher OpenAQ concurrency while realtime client code hardcodes low worker count.
- Fixed waits make runtime scale linearly with sensor count and can dominate wall time even when the API is healthy.
- Current timeout signaling is inconsistent. `scripts/collect_openaq_realtime.sh` accepts a timeout flag but does not enforce it directly.

## Change Scope
- Define one clear owner for OpenAQ realtime rate-limiting and retry policy.
- Move throttling, retry, and timeout parameters to configuration-driven behavior.
- Remove duplicate fixed sleeps in the realtime OpenAQ client path.
- Add operational logging so rate-limit hits, retries, and timeout behavior are visible.
- Validate behavior with Behave workflow scenarios and focused regression checks before/after implementation.

## Non-Goals
- No model training, feature engineering, or prediction logic changes.
- No refactor of non-OpenAQ pipelines.
- No country coverage expansion as part of this change.
