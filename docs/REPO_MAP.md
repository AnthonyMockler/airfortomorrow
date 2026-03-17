# Repo Map

## Top-Level Directories

- `scripts/`: shell wrappers, test harness entrypoints, and shared Bash utilities
- `src/`: Python collectors, processors, silver-data assembly, prediction, and shared utilities
- `features/`: Behave feature files, environment hooks, and step definitions
- `config/`: YAML configuration, centered on `config/config.yaml`
- `data/`: mutable runtime artifacts and tracked bootstrap inputs
- `assets/`: supporting static inputs such as worldpop, landcover, DEM, and sensor lists
- `plans/`: active markdown work records
- `decisions/`: short markdown decision notes
- `.github/workflows/`: GitHub Actions definitions

## Main Entrypoints

- `./scripts/run_complete_pipeline.sh`: end-to-end orchestration entrypoint
- `./scripts/run_air_quality_integrated_pipeline.sh`: air-quality collection and processing workflow
- `./scripts/run_firms_pipeline.sh`: FIRMS workflow
- `./scripts/run_himawari_integrated_pipeline.sh`: Himawari workflow
- `./scripts/run_era5_idw_pipeline.sh`: ERA5 workflow
- `./scripts/make_silver.sh`: silver dataset assembly
- `./scripts/predict_air_quality.sh`: prediction and map generation

## Test Entrypoints

- `./scripts/run_behave_tests_compact.sh --tier a|b|c|all`: preferred tiered Behave entrypoint
- `./scripts/run_behave_tests.sh`: raw Docker Behave harness
- `./scripts/run_tests.sh`: pytest wrapper
- `./scripts/smoke_test.sh`: Tier A smoke subset wrapper

## Data and Output Layout

- `data/raw/`: collector outputs and historical bootstrap inputs
- `data/processed/`: processed source outputs used downstream
- `data/silver/`: merged training or inference frames
- `data/predictions/data/`: prediction parquet outputs
- `data/predictions/map/`: rendered PNG map outputs

## Ownership Hints

- Wrapper behavior and user-facing CLI semantics usually live in `scripts/`.
- Core data logic usually lives in `src/data_collectors/`, `src/data_processors/`, `src/make_silver.py`, and `src/predict_air_quality.py`.
- Workflow and regression guarantees should be expressed in `features/` before production code changes.
- Process notes belong in `plans/` and `decisions/`, not in random markdown files.
