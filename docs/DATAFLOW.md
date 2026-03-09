# Data Flow

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

Those properties should be asserted through Behave or other repo-local contract checks, not assumed from manual runs.
