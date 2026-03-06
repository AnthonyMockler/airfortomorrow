# SRC KNOWLEDGE BASE

**Generated:** 2026-03-06

## OVERVIEW
Core Python implementation layer. Handles data collection (API fetches), processing (H3-indexed transformations), silver dataset aggregation, and XGBoost machine learning inference.

## STRUCTURE
```
src/
├── data_collectors/    # API fetchers (OpenAQ, AirGradient, FIRMS, Himawari)
├── data_processors/    # Interpolation and H3 discrete global grid assignments
├── models/             # Artifacts (xgboost_model.json)
├── utils/              # Shared Python utilities (config_loader.py, logging)
└── [entry].py          # Executable main files (make_silver.py, predict_air_quality.py)
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Feature Merging | `make_silver.py` | Combines processed data sources into `silver/` datasets |
| ML Inference | `predict_air_quality.py` | Generates PM2.5 predictions and AQI maps |
| Configuration | `utils/config_loader.py` | Singleton class parsing the root `config.yaml` |

## CONVENTIONS
- **H3-Centric Architecture:** All geospatial data operates on the H3 hexagonal grid (Resolution 8 for main grid, 4 for spatial context) instead of traditional coordinate joins.
- **Dual-Role Modules:** Nearly all Python files in `src/` can be executed standalone via `if __name__ == "__main__":` block.
- **Single Source of Truth:** Settings are managed through `ConfigLoader` parsing `config/config.yaml`—not through argument parsers or dotenvs.

## ANTI-PATTERNS (THIS DIRECTORY)
- **Direct invocation via CLI without Shell wrapper:** Never run `python src/file.py`. Execution must go through `scripts/*.sh` to inherit correct Docker variables and `PYTHONPATH`.
- **Usage of `_load_config()`:** Deprecated pattern in base classes. Always use `self.config_loader`.
