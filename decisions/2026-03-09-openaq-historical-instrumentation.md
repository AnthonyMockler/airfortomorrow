# Decision: OpenAQ Historical Instrumentation

## Date
2026-03-09

## Decision
Instrument the maintained OpenAQ historical downloader in place, using lightweight `perf_counter`-based timings and a structured JSON sidecar report, before making any throughput changes.

For this slice:
- add run-level timings around collector initialization, location discovery, and bounded download execution
- add per location-year timings for skip-path checks, S3 listing, object transfer and decompression, dataframe parse/concat, parquet write, and retry waits
- keep the wrapper CLI unchanged and write timing artifacts under the chosen output directory
- preserve the existing bounded Behave contract as the regression gate

## Why
- The maintained historical path is the shell wrapper plus `src/data_processors/s3_historical_data.py`, not the alternate collector implementation.
- The current bottleneck could be in several materially different places: OpenAQ location discovery, S3 object listing, archive transfer, gzip/CSV materialization, parquet writes, or warm-run skip overhead.
- Instrumenting first gives evidence for the first speedup pass and reduces the risk of optimizing the wrong stage.
- A JSON sidecar keeps the output inspectable without changing downstream parquet artifacts.

## Change Scope

- Modify `src/data_processors/s3_historical_data.py` to collect and summarize timing data for the maintained historical download path.
- Modify `src/data_collectors/openaq_collector.py` to expose timing breakdown for `_get_sensors_country()`.
- Correct the historical script's country override plumbing so the bounded timing run reflects the requested country selection.
- Validate with the existing bounded historical OpenAQ contract and bounded live sample runs.

## Non-Goals

- No throughput optimization in this slice beyond the minimum fix needed for accurate bounded-country profiling.
- No new historical wrapper flags.
- No changes to raw parquet schema or file naming.
- No attempt to merge the historical S3 path into the realtime OpenAQ API client.
