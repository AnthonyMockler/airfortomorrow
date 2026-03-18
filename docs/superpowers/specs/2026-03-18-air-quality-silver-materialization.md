# Air Quality Silver Materialization Spec

- Status: Brainstorming
- Date: 2026-03-18
- Scope: Define how `silver.air_quality_observations` should be built from OpenAQ and AirGradient bronze in v1.

## Goal

Define a simple, testable, deterministic v1 implementation for air-quality silver that does not carry forward the old pipeline's implicit dataframe behavior.

## Dataset Contract

The published dataset is `silver.air_quality_observations`.

V1 contract:

- output format is plain Parquet
- published partition key is `date`
- `h3_08` is the only managed spatial key
- published silver output must not include lat/lon geometry columns or GeoParquet metadata
- output should contain one row per `date + h3_08`

This dataset is the first canonical analytical air-quality layer. Bronze remains the raw recovery layer.

## Inputs

`silver.air_quality_observations:<date>` should be built from the relevant OpenAQ and AirGradient bronze inputs for that date.

Sources:

- OpenAQ historical bronze
- OpenAQ realtime bronze
- AirGradient historical bronze
- AirGradient realtime bronze

Bronze may be partial. Silver should still build from whatever bronze exists for the target date.

## V1 Processing Rules

### 1. Normalize Source Records

Normalize OpenAQ and AirGradient records into a common row shape inside the transform.

The transform should derive, at minimum:

- `date`
- `h3_08`
- `pm25`
- source identifier needed for debugging during the run

Raw coordinates may be used transiently to compute `h3_08`, but they should not be part of the published silver schema.

### 2. Convert To H3 Early

Convert each surviving source record to `h3_08` during normalization.

The old coordinate-based deduplication rule should not be preserved. The managed silver dataset is H3-based, so aggregation should happen on `date + h3_08`, not on raw latitude/longitude equality.

### 3. Temporary Outlier Guardrail

V1 does not implement real outlier detection yet.

Instead:

- discard records where `pm25 > 400`
- do not add extra outlier heuristics without a separate decision

This is explicitly a temporary placeholder and should be called out in code comments, tests, and task documentation as future work.

### 4. No Explicit Duplicate-Removal Step In V1

Do not add a separate exact-duplicate removal step in v1.

If duplicate source records exist, they will contribute to the final mean. That is acceptable for the first implementation and should be treated as an explicit v1 tradeoff, not an accident.

### 5. Aggregate To One Cell-Day Value

After normalization and the temporary `pm25 <= 400` guardrail, combine all surviving OpenAQ and AirGradient readings for the target date and aggregate to one row per `date + h3_08`.

Aggregation rule:

- `pm25 = mean(all surviving readings in that cell on that day)`

This replaces the old behavior that concatenated OpenAQ and AirGradient and then kept the first row for each `date + latitude + longitude`.

## What Not To Copy From The Old Pipeline

The current implementation in `src/data_processors/process_air_quality.py` should not be copied literally.

In particular, do not preserve:

- `drop_duplicates(... keep="first")` over `date_utc + latitude + longitude`
- implicit source preference caused by concatenation order
- published silver outputs that still carry raw geospatial columns as part of the managed schema

## Suggested Implementation Shape

Keep the implementation testable and flat.

An acceptable v1 seam is:

- `normalize_openaq_records(...)`
- `normalize_airgradient_records(...)`
- `aggregate_air_quality_cell_day(...)`

The normalization and aggregation logic should be table-in / table-out code that can be tested with small fixtures independently of the CLI, worker runtime, and storage layout.

## Minimum Test Cases

The implementation should include small deterministic tests for:

- multiple readings in one `date + h3_08` aggregate to their mean
- OpenAQ and AirGradient readings in the same `date + h3_08` aggregate together
- records with `pm25 > 400` are excluded before aggregation
- output contains `h3_08` and does not publish raw lat/lon columns
- the old `keep first` behavior is not reproduced

## Deferred

These are intentionally out of scope for v1:

- real outlier detection
- explicit duplicate-record removal
- source weighting
- per-site daily averaging before cell aggregation
- richer quality scoring or coverage columns
