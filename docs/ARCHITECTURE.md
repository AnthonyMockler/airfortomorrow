# Architecture

## Layers

The repository has a deliberate split between user-facing shell wrappers and Python implementation code.

1. Shell wrappers in `scripts/` own command-line ergonomics, environment setup, logging, and orchestration.
2. Python entrypoints in `src/` own collection, processing, silver-data assembly, and prediction logic.
3. Shared configuration flows through `config/config.yaml`.
4. Behave features in `features/` verify workflow behavior at the command level.

## Configuration Model

- Python code should read configuration through `src/utils/config_loader.py`.
- Shell scripts should read configuration through `scripts/utils/config_reader.sh`.
- Configuration values should not be duplicated broadly in argument parsing or ad hoc environment defaults.

## Data Model

- The spatial backbone is the H3 grid.
- Source-specific collectors produce raw or minimally processed outputs.
- Processors normalize source outputs onto H3 and time-aware tables.
- `make_silver.py` builds the silver dataset used by prediction.
- `predict_air_quality.py` loads the trained XGBoost model and emits PM2.5 and map outputs.

## Modes

Most workflows have `realtime` and `historical` modes.

- `realtime` focuses on current collection and prediction.
- `historical` focuses on bounded date ranges for backfills, validation, and analysis.

Mode-specific arguments should fail fast when invalid or incomplete.

## Non-Negotiable Architecture Rules

- User-facing execution should go through wrapper scripts in `scripts/`.
- Do not treat direct `python src/...` execution as the supported path.
- In `BaseCollector`-derived code, use `self.config_loader` rather than reviving deprecated local config-loading patterns.
