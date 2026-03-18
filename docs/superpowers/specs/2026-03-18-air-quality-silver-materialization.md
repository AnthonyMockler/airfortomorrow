# Air Quality Silver Materialization Spec

- Status: Locked for slice 1 execution
- Date: 2026-03-18
- Scope: Define how `silver.air_quality_observations` should be built from OpenAQ and AirGradient bronze in v1.

## Goal

Define a simple, testable, deterministic v1 implementation for air-quality silver that does not carry forward the old pipeline's implicit dataframe behavior.

## Dataset Contract

The published dataset is `silver.air_quality_observations`.

V1 contract:

- output format is plain Parquet
- published partition key is `date_utc`
- `h3_08` is the only managed spatial key
- published silver output must not include lat/lon geometry columns or GeoParquet metadata
- output should contain one row per `date_utc + h3_08`
- output should include `pm25` and `observation_count`
- output should include `source_mix`
- output should include `reference_observation_count` and `low_cost_observation_count`
- output is sparse: only publish cell-days with at least one surviving reading

This dataset is the first canonical analytical air-quality layer. Bronze remains the raw recovery layer.

`silver.air_quality_observations` does not need to emit a dense H3 grid. Dense cell coverage is a later gold-stage concern when building model-ready features.

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

- `date_utc`
- `h3_08`
- `pm25`
- source identifier needed for debugging during the run
- source class information needed to derive `source_mix`

Raw coordinates may be used transiently to compute `h3_08`, but they should not be part of the published silver schema.

The published day column should be named `date_utc`, not the more ambiguous `date`.

### 2. Classify Sensor Source Type

Each surviving reading must be classified as either:

- `reference_grade`
- `low_cost`

This classification is an internal input to the final `source_mix` column.

Rules:

- AirGradient readings should be treated as `low_cost`.
- OpenAQ readings must not be treated as `reference_grade` by default.
- OpenAQ classification should be based on sensor metadata retrieved from the OpenAQ API, not on a blanket assumption about the source.

Current code path to learn from:

- `OpenAQCollector._get_sensors_country()` fetches location metadata from `client.locations.list(...)`
- that code already captures `provider_name` and `owner_name`
- it also stores a rough `sensor_grade` value, but that field is currently just the first instrument name from the `instruments` list, not a final trusted grade label
- `src/data_processors/openaq_realtime_client.py` already merges this metadata back onto realtime measurements before saving output

Live confirmation from the OpenAQ API on 2026-03-18:

- a larger Thailand/Laos sample of 783 locations exposed `provider_name`, `owner_name`, and `instruments` exactly as expected
- observed top providers in that sample were:
  - `AirGradient` (480)
  - `Air4Thai` (259)
  - `Thailand` (33)
  - `Clarity` (3)
  - `HabitatMap` (1)
- observed top instruments in that sample were:
  - `Unknown AirGradient Sensor` (427)
  - `Government Monitor` (295)
  - multiple specific `AirGradient ...` instrument names
  - `Clarity Sensor`
  - `HabitatMap Sensor`

That sample gives a much better v1 rule:

- treat `instruments` as the primary classification signal
- treat known low-cost provider or owner brand names as secondary corroborating signals
- do not use `provider_name = Thailand` by itself as a reference-grade rule
- do not use `owner_name = Unknown Governmental Organization` by itself as a reference-grade rule

Observed reference-grade fixtures from the live sample:

- `provider_name = Air4Thai`, `owner_name = Unknown Governmental Organization`, `instruments = ["Government Monitor"]`
- `provider_name = Thailand`, `owner_name = Unknown Governmental Organization`, `instruments = ["Government Monitor"]`

Observed low-cost fixtures from the live sample:

- `provider_name = AirGradient`, `instruments` containing `Unknown AirGradient Sensor`
- `provider_name = AirGradient`, `instruments` containing named `AirGradient ...` devices
- `provider_name = Clarity`, `instruments = ["Clarity Sensor"]`
- `provider_name = HabitatMap`, `instruments = ["HabitatMap Sensor"]`

For v1, the implementation should build or reuse an explicit OpenAQ sensor-metadata lookup that includes, at minimum:

- `sensor_id`
- `location_id`
- `provider_name`
- `owner_name`
- instrument or manufacturer metadata available from the API response

Classification should be explicit and testable:

- use normalized metadata values
- use explicit matching rules or a small table-driven mapping
- keep the classification code in Python, but keep the known reference-grade and low-cost patterns in config
- normalize values case-insensitively and punctuation-insensitively before matching
- do not silently treat unknown OpenAQ metadata as `reference_grade`

Recommended v1 precedence:

1. If any normalized instrument name contains `government monitor`, classify as `reference_grade`.
2. Else if any normalized instrument, provider, or owner value matches a known low-cost network or manufacturer such as `airgradient`, `clarity`, or `habitatmap`, classify as `low_cost`.
3. Else fail classification and extend the explicit mapping.

If an OpenAQ sensor cannot be classified deterministically as `reference_grade` or `low_cost`, or if its metadata matches both classes, the row should be dropped and logged loudly enough that the mapping can be extended. Do not silently guess.

For v1:

- unknown classification => drop the row and log it loudly
- conflicting classification => drop the row and log it loudly
- include counts plus a small sample of dropped metadata values in durable operator-facing notes
- do not fail the whole day materialization just because a few rows were unclassified or ambiguous

### 3. Convert To H3 Early

Convert each surviving source record to `h3_08` during normalization.

Rows missing usable coordinates or failing H3 conversion should be dropped and logged. They should not fail the whole day materialization in v1.

The old coordinate-based deduplication rule should not be preserved. The managed silver dataset is H3-based, so aggregation should happen on `date_utc + h3_08`, not on raw latitude/longitude equality.

### 4. Normalize Timestamps To UTC

Each source transform must normalize its authoritative source timestamp to `datetime_utc`, then derive `date_utc` from that value.

Rules:

- use the source-specific authoritative timestamp field
- do not mix UTC and local fields casually
- published day aggregation must derive from `datetime_utc`
- rows missing a usable timestamp or failing UTC normalization should be dropped and logged in v1
- dropped timestamp rows should not fail the whole day materialization in v1

This is a deliberate v1 simplification. Future work may need a more careful treatment of local-day boundaries or presentation-layer timezone handling for GMT+7 users, but the canonical silver contract should stay UTC-based for now.

### 5. Temporary Outlier Guardrail

V1 does not implement real outlier detection yet.

Instead:

- discard records where `pm25 > 400`
- do not add extra outlier heuristics without a separate decision

This is explicitly a temporary placeholder and should be called out in code comments, tests, and task documentation as future work.

### 6. No Explicit Duplicate-Removal Step In V1

Do not add a separate exact-duplicate removal step in v1.

If duplicate source records exist, they will contribute to the final mean. That is acceptable for the first implementation and should be treated as an explicit v1 tradeoff, not an accident.

### 7. Aggregate To One Cell-Day Value

After normalization and the temporary `pm25 <= 400` guardrail, combine all surviving OpenAQ and AirGradient readings for the target date and aggregate to one row per `date_utc + h3_08`.

Aggregation rule:

- `pm25 = mean(all surviving readings in that cell on that day)`
- `observation_count = count(all surviving readings in that cell on that day)`
- `reference_observation_count = count(surviving reference-grade readings in that cell on that day)`
- `low_cost_observation_count = count(surviving low-cost readings in that cell on that day)`
- `source_mix = reference_grade` if every surviving reading in the cell-day is `reference_grade`
- `source_mix = low_cost` if every surviving reading in the cell-day is `low_cost`
- `source_mix = mixed_source` if the cell-day contains both `reference_grade` and `low_cost`

This replaces the old behavior that concatenated OpenAQ and AirGradient and then kept the first row for each `date + latitude + longitude`.

## What Not To Copy From The Old Pipeline

The current implementation in `src/data_processors/process_air_quality.py` should not be copied literally.

In particular, do not preserve:

- `drop_duplicates(... keep="first")` over `date_utc + latitude + longitude`
- implicit source preference caused by concatenation order
- published silver outputs that still carry raw geospatial columns as part of the managed schema
- any silent assumption that all OpenAQ observations are reference-grade

## Suggested Implementation Shape

Keep the implementation testable and flat.

An acceptable v1 seam is:

- `normalize_openaq_records(...)`
- `normalize_airgradient_records(...)`
- `classify_sensor_source(...)`
- `aggregate_air_quality_cell_day(...)`

The normalization and aggregation logic should be table-in / table-out code that can be tested with small fixtures independently of the CLI, worker runtime, and storage layout.

## Minimum Test Cases

The implementation should include small deterministic tests for:

- multiple readings in one `date_utc + h3_08` aggregate to their mean
- OpenAQ and AirGradient readings in the same `date_utc + h3_08` aggregate together
- records with `pm25 > 400` are excluded before aggregation
- `observation_count` reflects the number of surviving readings used in the mean
- `reference_observation_count + low_cost_observation_count = observation_count`
- an AirGradient-only cell-day yields `source_mix = low_cost`
- an OpenAQ cell-day with `instruments = ["Government Monitor"]` yields `source_mix = reference_grade`
- an OpenAQ cell-day with provider or instrument metadata identified as `AirGradient`, `Clarity`, or `HabitatMap` yields `source_mix = low_cost`
- a cell-day with both reference-grade and low-cost contributors yields `source_mix = mixed_source`
- unclassified OpenAQ metadata is dropped and logged instead of silently defaulting
- conflicting OpenAQ classification signals are dropped and logged instead of being guessed
- `provider_name = Thailand` on its own does not classify a row as `reference_grade`
- `owner_name = Unknown Governmental Organization` on its own does not classify a row as `reference_grade`
- rows with missing coordinates are dropped and logged
- rows with unusable timestamps are dropped and logged
- output contains `h3_08` and does not publish raw lat/lon columns
- the old `keep first` behavior is not reproduced

The tests for OpenAQ classification should use representative metadata fixtures shaped like the rows produced by the current sensor discovery path, including fields such as `provider_name`, `owner_name`, and instrument metadata from the OpenAQ API response.

## Deferred

These are intentionally out of scope for v1:

- real outlier detection
- explicit duplicate-record removal
- source weighting
- per-site daily averaging before cell aggregation
- richer quality scoring or coverage columns
