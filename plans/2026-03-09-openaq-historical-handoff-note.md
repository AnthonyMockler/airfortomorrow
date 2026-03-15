# OpenAQ Historical Handoff Note

- Status: Handoff
- Date: 2026-03-09

## Keep

- Keep the bounded historical OpenAQ contract in [openaq_historical_contract.feature](/Users/anthonymockler/Documents/unicef/airfortomorrow/features/contracts/openaq_historical_contract.feature).
- Keep the supporting wrapper and downloader plumbing in:
  - [collect_openaq_historical.sh](/Users/anthonymockler/Documents/unicef/airfortomorrow/scripts/collect_openaq_historical.sh)
  - [s3_historical_data.py](/Users/anthonymockler/Documents/unicef/airfortomorrow/src/data_processors/s3_historical_data.py)

## Current Safety Loop

- Focused contract:
  - `./scripts/run_behave_tests_compact.sh features/contracts/openaq_historical_contract.feature`
- Bounded live sample:
  - `./scripts/collect_openaq_historical.sh --years 2024 --country-codes 111 --workers 2 --location-limit 5`
- Last result:
  - `2 scenarios passed` in `3m59.840s`

## What The Next Agent Should Do

- Stay on the existing historical path only:
  - `scripts/collect_openaq_historical.sh`
  - `src/data_processors/s3_historical_data.py`
- Use the existing bounded contract as the regression check.
- Build a narrow measurement loop around the historical downloader so we can separate:
  - location discovery time
  - S3 listing time
  - object download and gzip read time
  - dataframe concat/parse time
  - parquet write time
  - skip-path overhead
- Identify which stages are actually slow and which are already cheap before changing behavior.

## Goal For The Next Slice

- Produce evidence about where historical OpenAQ time is going on the real maintained path.
- Use that evidence to choose the first optimization target.
- Keep the existing historical contract green while doing it.
