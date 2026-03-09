# Data Flow

## Operational Goal

The pipeline exists to produce daily H3-indexed PM2.5 estimates from multiple imperfect data sources. In practice, that means taking sparse or differently gridded environmental signals and turning them into one prediction-ready row per cell and day.

## End-to-End Flow

1. Collect source data.
2. Process each source into downstream-usable tables.
3. Merge source outputs into a silver dataset.
4. Run prediction and optional map generation.

## Sources

- OpenAQ and AirGradient provide ground-sensor observations.
- NASA FIRMS provides fire detections and historical archive inputs.
- Himawari provides aerosol optical depth data.
- ERA5 provides meteorological context.

## Concrete Pipeline Stages

### 1. Build the H3 x date frame

- Implemented mainly in `src/make_silver.py`.
- The silver step creates the base H3 frame for the selected countries and cross-joins it with the requested dates.
- This wall-to-wall frame is what lets the model emit predictions even where no sensor is present.

### 2. Bring each source onto that frame

- Air quality:
  - collect and deduplicate OpenAQ and AirGradient observations
  - write processed outputs under `data/processed/airquality/{mode}/`
- FIRMS:
  - turn hotspot detections into H3 fire-intensity signals
  - write outputs under `data/processed/firms/h3/{mode}/`
- Himawari:
  - convert raw satellite files into H3 outputs, daily aggregates, then interpolated daily AOD
  - write outputs under `data/processed/himawari/`
- ERA5:
  - collect weather variables, aggregate to daily H3-aligned tables, and prepare them for downstream joins
  - write outputs under `data/processed/era5/`

### 3. Engineer prediction features

- Implemented in `src/make_silver.py`.
- The silver step does more than join files:
  - it carries the date grain expected by prediction
  - it computes rolling-window features
  - it adds spatial context such as coarser-parent lag features
- This is where the repo's multi-source fusion turns into the model-ready feature matrix.

### 4. Predict PM2.5 and generate outputs

- Implemented in `src/predict_air_quality.py`.
- The predictor loads daily silver files, selects the model feature columns, runs XGBoost inference, clips predictions to a sane range, and saves daily parquet outputs.
- Optional map and validation flows also live here and in `src/sensor_validation.py`.

## Typical Artifact Path

- Raw source outputs land in `data/raw/`.
- Processed source outputs land in `data/processed/`.
- Merged inference-ready outputs land in `data/silver/`.
- Prediction outputs land in `data/predictions/data/`.
- Map outputs land in `data/predictions/map/`.

## Runtime Expectations

- Historical and realtime runs should create or update artifacts produced by the current command.
- Tests must not pass because of leftover files from previous runs.
- FIRMS historical workflows depend on tracked historical inputs already present under `data/raw/firms/historical/`.

## Downstream Contract

The minimum downstream contract is:

- the wrapper command succeeds or fails explicitly
- the run emits a log file or references one
- fresh artifacts are created or updated in the expected directory
- artifacts are non-empty and contain usable values for the requested slice
- the final silver and prediction outputs match the requested countries, dates, and mode

Those properties should be asserted through Behave or other repo-local contract checks, not assumed from manual runs.
