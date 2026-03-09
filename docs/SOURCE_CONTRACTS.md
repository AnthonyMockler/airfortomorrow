# Source Contracts

## OpenAQ and AirGradient

- Role: ground-sensor observations used for air-quality inputs.
- Main code and wrappers:
  - `./scripts/run_air_quality_integrated_pipeline.sh`
  - `./scripts/collect_openaq_realtime.sh`
  - `./scripts/collect_openaq_historical.sh`
  - `./scripts/collect_airgradient_data.sh`
  - `src/data_collectors/openaq_collector.py`
  - `src/data_collectors/airgradient_collector.py`
  - `src/data_processors/process_air_quality.py`
- Typical outputs:
  - processed parquet under `data/processed/airquality/realtime/` or `data/processed/airquality/historical/`
- Operational notes:
  - OpenAQ is the primary ground-monitor source for broad monitoring coverage
  - AirGradient adds low-cost sensor coverage and must be deduplicated against overlapping observations
  - larger historical OpenAQ runs can be expensive because archive materialization dominates runtime
- Common failure modes:
  - API or credential failures
  - upstream rate limits or slow historical downloads
- Verification notes:
  - historical collection should use small bounded slices for iterative testing
  - downstream checks should verify usable PM2.5 values and timestamps inside the requested slice

## FIRMS

- Role: fire detections and KDE-derived fire context.
- Main code and wrappers:
  - `./scripts/run_firms_pipeline.sh`
  - `./scripts/run_firms_kde.sh`
  - `./scripts/run_firms_kde_historical.sh`
  - `src/data_collectors/firms_data_collector.py`
  - `src/data_processors/firms_data_processor.py`
  - `src/data_processors/firms_kde_interpolation.py`
  - `src/data_processors/firms_kde_historical.py`
- Typical outputs:
  - H3 fire-intensity parquet under `data/processed/firms/h3/{mode}/`
  - plot outputs under `data/processed/firms/plots/{mode}/`
- Operational notes:
  - FIRMS converts point detections into smoother fire-intensity signals that are more useful for modeling than raw points alone
  - historical workflows depend on tracked bootstrap data in `data/raw/firms/historical/`
- Common failure modes:
  - missing or accidentally deleted historical bootstrap archive
  - empty hotspot windows for the selected slice
- Verification notes:
  - cleanup logic must preserve the tracked historical inputs
  - tests should verify useful fire-intensity outputs rather than only file existence

## Himawari

- Role: aerosol optical depth source with historical and realtime collection paths.
- Main code and wrappers:
  - `./scripts/run_himawari_integrated_pipeline.sh`
  - `./scripts/run_himawari_aod_realtime.sh`
  - `./scripts/run_himawari_aod_historical.sh`
  - `src/data_collectors/himawari_aod.py`
  - `src/data_processors/process_himawari_h3_streaming.py`
  - `src/data_processors/himawari_daily_aggregator.py`
  - `src/data_processors/himawari_idw_interpolator.py`
- Typical outputs:
  - H3 outputs under `data/processed/himawari/h3/`
  - daily aggregates under `data/processed/himawari/daily_aggregated/`
  - interpolated daily AOD under `data/processed/himawari/interpolated/`
- Operational notes:
  - Himawari is the main satellite aerosol signal in the pipeline
  - the flow is multi-stage and heavier than the ground-sensor path
- Common failure modes:
  - JAXA credential issues
  - archive gaps or missing upstream files
  - longer runtimes than other collector paths
- Verification notes:
  - historical runs can be expensive, so contract tests should use small slices
  - artifact assertions should prove useful AOD-derived outputs, not just file existence

## ERA5

- Role: meteorological context for interpolation and downstream prediction.
- Main code and wrappers:
  - `./scripts/run_era5_idw_pipeline.sh`
  - `./scripts/run_era5_realtime.sh`
  - `src/data_collectors/era5_meteorological_idw.py`
  - `src/data_processors/era5_daily_aggregator.py`
- Typical outputs:
  - H3 or intermediate outputs under `data/processed/era5/h3/`
  - daily weather outputs under `data/processed/era5/daily_aggregated/{mode}/`
- Operational notes:
  - ERA5 provides weather context such as temperature, dewpoint, and wind variables used in the model feature set
- Common failure modes:
  - CDS credential failures
  - slow upstream responses or retry-heavy collection windows
- Verification notes:
  - historical tests should use short slices and, when useful, a narrow parameter set such as `2t`
  - credentials and upstream access can make live checks noisier than purely local contract tests

## Common Contract Rules

- Prefer wrapper-level scenarios over one monolithic end-to-end live run.
- Assert current-run artifacts, not stale baseline files.
- Capture the referenced log path for every live or long-running command.
- Keep historical verification bounded enough to support iterative debugging and performance work.
