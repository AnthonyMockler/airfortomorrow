# Decision: OpenAQ Historical Speedup Phase 1 and 2

## Date
2026-03-09

## Decision
Implement OpenAQ historical speedup in two linked steps:

1. Phase 1: replace hand-rolled retry waits with botocore-native retry/backoff and improve S3 transfer throughput with connection-pool tuning plus per-location object download concurrency.
2. Phase 2: add optional date-window filtering to historical OpenAQ so bounded runs avoid full-year object materialization when start/end dates are provided.

## Why

- Measured profiling shows S3 object-fetch latency dominates historical OpenAQ runtime.
- Existing code uses manual retry/sleep loops despite botocore having built-in retry strategies.
- Historical wrapper currently works at year granularity, causing avoidable downloads for bounded date windows.
- Full-year and multi-month runs remain common, so date filtering should be optional and non-disruptive.

## Change Scope

- Update OpenAQ historical wrapper and downloader to accept optional date bounds.
- Configure S3 client retries/connections and remove manual sleep-based retry loops.
- Improve object download orchestration and filter object keys to the requested date interval.
- Pass date bounds through historical complete-pipeline and integrated air-quality paths.
- Update and run existing OpenAQ historical Behave contract as regression coverage.

## Non-Goals

- No schema or naming changes to historical raw parquet outputs.
- No changes to OpenAQ realtime collector paths.
- No location-discovery caching work in this slice unless required by regressions.
