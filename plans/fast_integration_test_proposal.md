# Minimal Integration Testing Plan for Quickstart

## Status
Implemented on 2026-03-08. This proposal is retained for historical context.

This plan introduces a fast, reliable integration test that mirrors the "Quickstart" workflow (Docker build/run) but completes in under 10 minutes.

## User Review Required

> [!IMPORTANT]
> To achieve a fast test, I propose adding a `TEST_MODE` environment variable that limits the number of OpenAQ sensors collected. This ensures we test the **logic** of the downloader, processing, and inference without waiting for 700+ sensors to be fetched.

## Proposed Changes

### Core Infrastructure

#### [MODIFY] [openaq_collector.py](file:///Users/anthonymockler/Documents/unicef/airfortomorrow/src/data_collectors/openaq_collector.py)
- Update `_get_sensors_data` to respect a `limit_sensors` parameter or a `TEST_MODE` environment variable.
- If in test mode, only process a small subset (e.g., first 5-10 sensors) instead of the full list.

### Scripts

#### [NEW] [integration_test.sh](file:///Users/anthonymockler/Documents/unicef/airfortomorrow/scripts/integration_test.sh)
- A new script designed to be run inside the Docker container.
- Executes: `./scripts/run_complete_pipeline.sh --mode realtime --hours 1 --countries LAO --parallel` (minimal parameters).
- Sets `TEST_MODE=1` to trigger limited sensor collection.
- Verifies that expected output files exist in:
    - `data/silver/realtime/`
    - `data/predictions/data/realtime/`
- Reports a clear PASS/FAIL.

---

## Verification Plan

### Automated Tests
1. **Local Script Test**: Run `scripts/integration_test.sh` inside the Docker container.
   ```bash
   # Build the image first
   docker build -t airquality-app .
   # Run the integration test directly
   docker run --rm -it -e TEST_MODE=1 airquality-app ./scripts/integration_test.sh
   ```
2. **Standard Pipeline Contract**: Verify `./scripts/run_tests.sh` still passes (to ensure no regressions in base collector logic).

### Manual Verification
- Review the logs of the integration test to confirm only a handful of sensors were processed.
- Verify that the parquet file produced by the "minimal" run is valid and contains realistic data for the selected sensors.
