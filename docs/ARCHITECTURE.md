# Architecture

## What This Repository Does

Air for Tomorrow is a data and modeling pipeline, not a web app or generic library. Its job is to ingest heterogeneous environmental data, align it to a shared H3 grid, engineer daily features, and emit PM2.5 predictions plus optional visual outputs for Thailand and Laos.

## Layers

The repository has a deliberate split between user-facing shell wrappers and Python implementation code.

1. Shell wrappers in `scripts/` own command-line ergonomics, environment setup, logging, and orchestration.
2. Python entrypoints in `src/` own collection, processing, silver-data assembly, and prediction logic.
3. Shared configuration flows through `config/config.yaml`.
4. Behave features in `features/` verify workflow behavior at the command level.

## Main Execution Path

The typical operational path is:

1. `./scripts/run_complete_pipeline.sh`
2. `src/run_complete_pipeline.py`
3. source-specific wrappers for Himawari, FIRMS, ERA5, OpenAQ, and AirGradient
4. `./scripts/make_silver.sh`
5. `src/make_silver.py`
6. `./scripts/predict_air_quality.sh`
7. `src/predict_air_quality.py`

That path matters because the shell layer owns environment setup and runtime ergonomics, while the Python layer owns the data logic.

## Concrete Code Map

- `scripts/run_complete_pipeline.sh`: top-level wrapper used for most user-facing runs
- `src/run_complete_pipeline.py`: orchestrates per-source workflows and downstream phases
- `src/data_collectors/`: source acquisition and source-specific collection logic
- `src/data_processors/`: source-specific transformation, aggregation, interpolation, and H3 shaping
- `src/make_silver.py`: builds the H3 x date base frame, merges processed sources, and engineers model features
- `src/predict_air_quality.py`: loads silver files, prepares model features, writes prediction parquet, and optionally generates maps and validation outputs
- `src/sensor_validation.py`: historical-mode validation logic against observed sensors
- `src/utils/config_loader.py`: canonical Python-side configuration access

## Configuration Model

- Python code should read configuration through `src/utils/config_loader.py`.
- Shell scripts should read configuration through `scripts/utils/config_reader.sh`.
- Configuration values should not be duplicated broadly in argument parsing or ad hoc environment defaults.

## Data Model

- The spatial backbone is the H3 grid.
- Source-specific collectors produce raw or minimally processed outputs.
- Processors normalize source outputs onto H3 and time-aware tables.
- `make_silver.py` builds the silver dataset used by prediction.
- `predict_air_quality.py` loads the trained XGBoost model and emits prediction parquet plus optional maps and validation outputs.
- Static layers such as world population, landcover, elevation, and boundaries provide contextual features and geography support.

## Modes

Most workflows have `realtime` and `historical` modes.

- `realtime` focuses on current collection and prediction.
- `historical` focuses on bounded date ranges for backfills, validation, and analysis.

Mode-specific arguments should fail fast when invalid or incomplete.

## Non-Negotiable Architecture Rules

- User-facing execution should go through wrapper scripts in `scripts/`.
- Many `src/` files have standalone CLIs, but do not treat direct `python src/...` execution as the supported path.
- In `BaseCollector`-derived code, use `self.config_loader` rather than reviving deprecated local config-loading patterns.
