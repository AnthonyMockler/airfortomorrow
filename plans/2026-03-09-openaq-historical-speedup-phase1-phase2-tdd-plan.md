# Plan: OpenAQ Historical Speedup Phase 1 and 2

- Status: Completed
- Owner: Codex
- Active Agent: Codex (GPT-5)
- Started: 2026-03-09
- Last Updated: 2026-03-09
- Scope Note: Implement S3 throughput improvements and optional date-window pruning for the maintained OpenAQ historical path, with contract-first verification.

## Feature Goal

Reduce OpenAQ historical wall time by addressing S3 transfer overhead first, then avoid unnecessary object downloads when a bounded historical date range is requested.

## Scope Guardrails

- Stay on the maintained historical path only:
  - `scripts/collect_openaq_historical.sh`
  - `src/data_processors/s3_historical_data.py`
  - `src/run_complete_pipeline.py`
  - `src/air_quality_integrated_pipeline.py`
- Keep existing wrapper behavior and raw parquet schema stable.
- Prefer botocore native retry/backoff behavior over hand-rolled sleep loops.
- Make date filtering optional so full-year/multi-month historical runs remain straightforward.
- Keep existing bounded OpenAQ historical contract coverage green.

## Red

1. Update historical OpenAQ contract expectations for new date-window CLI options and bounded-range behavior.
2. Run targeted OpenAQ historical contract coverage and capture RED before implementation.

## Green

1. Phase 1:
   - Configure S3 client with native retries/backoff and larger connection pool.
   - Remove hand-rolled retry sleeps from OpenAQ historical S3 download path.
   - Parallelize per-location object downloads to reduce request latency wall time.
2. Phase 2:
   - Add optional `--start-date`/`--end-date` to historical OpenAQ wrapper and Python downloader.
   - Filter listed S3 objects by requested date range before download.
   - Wire historical date range from complete-pipeline and integrated air-quality historical entrypoints.
3. Re-run targeted contract coverage and confirm green.

## Regression Safety

- Keep `features/contracts/openaq_historical_contract.feature` as the primary gate.
- Preserve existing `--years` path and behavior for users who do not provide date bounds.
- Ensure bounded date runs still produce valid historical raw parquet artifacts.

## Success Criteria

- Historical OpenAQ path uses SDK-native retry/backoff and tuned S3 connections.
- Bounded date-window runs fetch only date-relevant archive objects.
- Contract coverage is green with updated CLI/options expectations.

## Evidence to Capture

- RED command and failure signal.
- GREEN command and pass signal.
- Before/after bounded run timing report references.

## Notes and Findings

- Contract RED failures (before implementation):
  - historical wrapper `--help` output did not include `--start-date`/`--end-date`
  - historical wrapper rejected `--start-date` as an unknown option
- Phase 1 implementation summary:
  - moved S3 retry/backoff to botocore client config (`adaptive` mode)
  - increased S3 connection pool sizing
  - removed hand-rolled sleep/retry loops in the historical S3 path
  - added per-location object download concurrency while preserving per-location output parquet shape
- Phase 2 implementation summary:
  - added optional `--start-date`/`--end-date` to historical wrapper and Python downloader
  - added object-key date filtering for bounded windows
  - wired OpenAQ historical date bounds in complete pipeline and integrated air-quality historical path
- Coverage update:
  - updated `features/contracts/openaq_historical_contract.feature` to cover date-window options and bounded date-range output
  - reused existing date-range parquet step and fixed timezone comparison logic in `features/steps/historical_collection_steps.py`

## Evidence Log

- RED:
  - Command: `/Users/anthonymockler/.codex/skills/airfortomorrow-tests/scripts/run_behave_compact.py features/contracts/openaq_historical_contract.feature`
  - Result: failed in `1.366s`
  - Signal: missing `--start-date`/`--end-date` CLI options and unknown option failure in live scenario
  - Raw log: `/var/folders/gv/_b6pxv9j6k50mxj4c6blq3040000gn/T/airfortomorrow-behave-20260309-211344.log`
- GREEN:
  - Command: `/Users/anthonymockler/.codex/skills/airfortomorrow-tests/scripts/run_behave_compact.py features/contracts/openaq_historical_contract.feature`
  - Result: `2 scenarios passed` in `11.184s`
  - Raw log: `/var/folders/gv/_b6pxv9j6k50mxj4c6blq3040000gn/T/airfortomorrow-behave-20260309-212331.log`
- Post-change bounded benchmark (full-year path, no date-window filtering):
  - Command: `docker run --rm -v "$PWD:/app" -w /app airquality-app:test bash -lc './scripts/collect_openaq_historical.sh --years 2024 --country-codes 111 --workers 2 --location-limit 5 --output-dir data/raw/openaq/historical_phase12_benchmark_20260309_212405'`
  - Timing report: `data/raw/openaq/historical_phase12_benchmark_20260309_212405/historical_download_profile_20260309T142453Z.json`
  - Key signal: bounded download wall time `32.564s` (prior reference run was `233.029s` for same year/country/location-limit shape)
- Date-window contract run timing report:
  - `data/raw/openaq/historical/historical_download_profile_20260309T142343Z.json`
  - Key signal: bounded download wall time `6.125s` for `2024-01-01` to `2024-02-01`
