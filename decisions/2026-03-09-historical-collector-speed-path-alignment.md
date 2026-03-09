# Decision: Historical Collector Speed Path Alignment

## Date
2026-03-09

## Decision
Prioritize historical collector speed work by first aligning historical execution paths with the realtime optimizations that already landed, but only where the upstream/source semantics actually match.

The first optimization pass should proceed in this order:
1. OpenAQ historical / Air Quality historical path consolidation
2. Himawari historical download-path alignment
3. ERA5 historical orchestration cleanup

For this pass:
- OpenAQ historical should be treated as a separate archive path that needs consolidation and earlier filtering, not as a candidate to be forced through the realtime API client.
- Himawari historical should reuse the realtime-style download concurrency pattern where possible, because the shared processing optimizations are already in place.
- ERA5 historical should stay in the shared collector, but its historical-only pacing and wrapper behavior should be optimized.

## Why
- The bounded historical Behave baseline shows the current wall-time order is Air Quality historical `33m26.354s`, Himawari historical `17m2.378s`, ERA5 historical `6m13.479s`, and FIRMS historical `1m20.449s`.
- Prior realtime performance work already landed for OpenAQ, ERA5, and Himawari, but the historical paths do not all use those improvements consistently.
- OpenAQ historical is the clearest divergence: the optimized realtime client lives in `src/data_processors/openaq_realtime_client.py`, while the historical wrapper and integrated air-quality pipeline route through S3-archive codepaths instead.
- Himawari historical already benefits from the shared H3/IDW work, but it still uses a sequential download loop while realtime gained threaded day-level FTP downloads.
- ERA5 historical and realtime already share the same collector-level retry/backoff machinery, but historical still carries its own sequential per-date CDS loop and fixed inter-date sleep.

## Change Scope
- Audit and document the historical-vs-realtime path split for OpenAQ, Himawari, and ERA5.
- Consolidate duplicate OpenAQ historical entrypoints around one archive-oriented flow before tuning throughput.
- Extend or port Himawari realtime download-worker behavior to the historical download path and wire the flag through the historical integrated path.
- Remove historical-only ERA5 waits and wrapper behavior that block reuse of existing shared improvements.
- Keep the current historical Behave contract as the correctness gate and use the recorded bounded timings as the baseline for comparison.

## Non-Goals
- No FIRMS optimization in the first pass.
- No strict timing threshold assertions in Behave while runs still depend on networked upstream services.
- No changes to model training, silver-data schema, or prediction behavior.
- No forced unification of fundamentally different providers, such as replacing the OpenAQ historical archive path with the realtime API client.
