# SCRIPTS KNOWLEDGE BASE

**Generated:** 2026-03-06

## OVERVIEW
Primary orchestration layer for the Air Quality Prediction pipeline. Pure Bash implementation that manages environment setup, PYTHONPATH, and execution of the Python layer.

## STRUCTURE
```
scripts/
├── utils/                 # Shared Bash utilities (config_reader.sh, common.sh)
└── [workflow].sh          # Execution wrappers for specific pipeline phases
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Main Pipeline | `run_complete_pipeline.sh` | Orchestrates the end-to-end data fetching and prediction process |
| Test Harness | `run_tests.sh` | Wraps pytest inside a controlled Docker environment |
| Config Access | `utils/config_reader.sh` | Parses `config/config.yaml` using `yq` for shell scripts |

## CONVENTIONS
- **Docker-locked CI:** Tests (`pytest`) are strictly executed within the Docker container to ensure system dependency parity (GDAL, ecCodes).
- **Environment Bootstrapping:** `utils/common.sh` handles universal `PYTHONPATH` exports and logging setup.
- **Robust Path Resolution:** Scripts reliably use `BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"` to resolve absolute paths relative to the repo root.
- **Centralized Config:** Configuration values are retrieved via `config_reader.sh` rather than hardcoded.

## ANTI-PATTERNS (THIS DIRECTORY)
- **Direct Python invocation without module flag:** Avoid `python3 src/module.py`. Prefer package-aware execution: `python -m src.module`.
- **Redundant fallback defaults:** Do not hardcode extensive default variables in shell scripts if they duplicate values managed in `config/config.yaml`.
