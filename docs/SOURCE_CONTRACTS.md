# Source Contracts

## OpenAQ and AirGradient

- Role: ground-sensor observations used for air-quality inputs.
- Wrappers:
  - `./scripts/run_air_quality_integrated_pipeline.sh`
  - `./scripts/collect_openaq_realtime.sh`
  - `./scripts/collect_openaq_historical.sh`
  - `./scripts/collect_airgradient_data.sh`
- Notes:
  - historical collection should use small bounded slices for iterative testing
  - downstream checks should verify usable PM2.5 values and timestamps inside the requested slice

## FIRMS

- Role: fire detections and KDE-derived fire context.
- Wrappers:
  - `./scripts/run_firms_pipeline.sh`
  - `./scripts/run_firms_kde.sh`
  - `./scripts/run_firms_kde_historical.sh`
- Notes:
  - historical workflows depend on tracked bootstrap data in `data/raw/firms/historical/`
  - cleanup logic must preserve those inputs

## Himawari

- Role: aerosol optical depth source with historical and realtime collection paths.
- Wrappers:
  - `./scripts/run_himawari_integrated_pipeline.sh`
  - `./scripts/run_himawari_aod_realtime.sh`
  - `./scripts/run_himawari_aod_historical.sh`
- Notes:
  - historical runs can be expensive, so contract tests should use small slices
  - artifact assertions should prove useful AOD-derived outputs, not just file existence

## ERA5

- Role: meteorological context for interpolation and downstream prediction.
- Wrappers:
  - `./scripts/run_era5_idw_pipeline.sh`
  - `./scripts/run_era5_realtime.sh`
- Notes:
  - historical tests should use short slices and, when useful, a narrow parameter set such as `2t`
  - credentials and upstream access can make live checks noisier than purely local contract tests

## Common Contract Rules

- Prefer wrapper-level scenarios over one monolithic end-to-end live run.
- Assert current-run artifacts, not stale baseline files.
- Capture the referenced log path for every live or long-running command.
- Keep historical verification bounded enough to support iterative debugging and performance work.
