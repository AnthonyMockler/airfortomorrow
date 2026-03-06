# PROJECT KNOWLEDGE BASE

**Generated:** 2026-03-04
**Commit:** Unknown
**Branch:** Unknown

## OVERVIEW
End-to-end Air Quality Prediction pipeline combining ground sensor data (OpenAQ, AirGradient), satellite fire data (NASA FIRMS), AOD (Himawari), and meteorology (ERA5) to predict PM2.5 levels using an XGBoost model mapped to an H3 discrete global grid.

## STRUCTURE
```
.
├── config/           # Central YAML configuration (config.yaml)
├── scripts/          # Shell scripts for pipeline orchestration
├── src/              # Python implementation layer
│   ├── data_collectors/ # API fetchers (raw data)
│   ├── data_processors/ # Data transformation, H3 indexing, interpolation
│   ├── utils/        # Shared utilities (config_loader, logging, boundaries)
│   └── models/       # Pre-trained XGBoost models
└── data/             # Data storage (raw, processed, silver, predictions)
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Pipeline Orchestration | `scripts/` | `.sh` files that drive the pipeline. Start at `run_complete_pipeline.sh`. |
| Main Python Entry Points | `src/` | `run_complete_pipeline.py`, `make_silver.py`, `predict_air_quality.py`, plus integrated pipelines in `*_integrated_pipeline.py`. |
| Configuration | `config/config.yaml` | No traditional config files (like pyproject.toml). Everything is in YAML. |
| Silver Dataset Generation | `src/make_silver.py` | Bridges processed data into a unified ML-ready parquet. |

## CODE MAP
| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `PipelineRunner` | Class | `src/run_complete_pipeline.py` | Master Python orchestrator |
| `ConfigLoader` | Class | `src/utils/config_loader.py` | Centralized singleton configuration manager |
| `BaseCollector` | Class | `src/data_collectors/base_collector.py` | Abstract base for data collectors |
| `AirQualityProcessor` | Class | `src/data_processors/process_air_quality.py` | Processor for OpenAQ/AirGradient data |
| `predict_air_quality.py` | Script | `src/predict_air_quality.py` | Loads XGBoost, processes silver data, outputs predictions |

## CONVENTIONS
- **Configuration:** YAML-based (`config/config.yaml`). Accessed via `ConfigLoader` in Python and `scripts/utils/config_reader.sh` in Shell.
- **Geographic System:** H3 hex grid (Resolution 8 for main grid, 4 for spatial context).
- **Data Pipeline Flow:** `collectors (API -> raw parquet)` -> `processors (raw -> H3-indexed parquet)` -> `make_silver (merge)` -> `model (predict)`.
- **Modes:** Most collectors/processors support `realtime` and `historical`; some shell scripts are explicitly mode-specific (`collect_openaq_realtime.sh`, `collect_openaq_historical.sh`, `run_himawari_aod_realtime.sh`, `run_himawari_aod_historical.sh`).

## ANTI-PATTERNS (THIS PROJECT)
- **Direct execution of `src/` modules without `PYTHONPATH`:** Always invoke via shell wrappers in `scripts/` which handle working directories properly.
- **Usage of `_load_config()` in `BaseCollector`:** DEPRECATED. Use `self.config_loader` instead.
- **Running tests in host Python:** Do not run `pytest` directly on the host environment. Use `./scripts/run_tests.sh` so tests run inside Docker with project system dependencies.

## COMMANDS
```bash
# Run complete end-to-end realtime pipeline for Thailand and Laos
./scripts/run_complete_pipeline.sh --mode realtime --countries THA LAO

# Run tests (Docker-only harness)
./scripts/run_tests.sh -- -q

# Smoke test (forces Docker rebuild + validates core imports)
./scripts/smoke_test.sh
```

## NOTES
- The project is split strongly into Bash Orchestration (`scripts/`) and Python Implementation (`src/`).
- Executables are currently mixed with packages in `src/`.

## FORK/UPSTREAM WORKFLOW (MANDATORY)
This repository is developed from a personal fork and contributes upstream via clean PR branches.

### Remote model
- `origin` must point to `AnthonyMockler/airfortomorrow` (personal fork).
- `upstream` must point to `unicef/airfortomorrow` (public upstream).
- Never push to `upstream`. Pushes go to `origin` only.

Recommended one-time safety setup:
```bash
git remote set-url origin git@github.com:AnthonyMockler/airfortomorrow.git
git remote add upstream git@github.com:unicef/airfortomorrow.git  # if missing
git remote set-url --push upstream DISABLED
git config remote.pushDefault origin
```

### Branch model
- `main` is a clean integration branch that tracks `upstream/main`.
- `anthony/helpers` stores personal helper docs (`AGENTS.md`, helper markdown files, notes).
- Feature/issue branches (`codex/issue-<id>-<slug>`) must be created from clean `main` (synced to `upstream/main`), never from `anthony/helpers`.

### PR hygiene rules
- Helper markdown commits must stay out of upstream PR branches.
- Open PRs from fork feature branches to `unicef/airfortomorrow:main`.
- Before opening a PR, confirm helper docs are not in the diff.

## ISSUE AUTHORING
- For repo task/improvement issues, follow `ISSUE_CREATION_GUIDELINES.md`.
- Default structure: `Problem` -> `Desired outcome` -> `Constraints / notes` -> `Done when` -> `Verification`.
- Use bug template `.github/ISSUE_TEMPLATE/bug_report.yml` for end-user bug reports.

## ISSUE HANDLING HANDBOOK (AGENTS)
This section defines the required workflow when an agent picks up a GitHub issue in this repository.

### 1) Intake and ownership
1. Confirm the issue is open, unassigned, and not already being worked:
   - `gh issue view <id> --repo AnthonyMockler/airfortomorrow`
   - Check assignees and recent comments for active ownership signals.
2. If the issue is already assigned or actively in progress, do not proceed in parallel.
3. Start all issue work in a clean git worktree so unrelated local changes cannot leak into the issue branch:
   - `git fetch --all --prune`
   - `git worktree add ../airfortomorrow_issue<id> -b codex/issue-<id>-<slug> upstream/main`
4. If available, assign the issue to yourself and immediately post a start comment.

Example start signal:
`Taking this issue now. Assigned to myself and starting implementation on branch codex/issue-<id>-<slug>.`

### 2) Planning and execution
1. Read the issue completely, including `Constraints / notes`, `Done when`, `Verification`, and `Out of scope`.
2. Execute autonomously by default.
3. Only pause for maintainer input when blocked by:
   - Missing access/permissions.
   - Conflicting acceptance criteria that cannot both be satisfied.
   - High-risk decisions with irreversible impact (data loss, security, production behavior changes).
4. Keep scope tied to the issue; avoid opportunistic refactors unless required to satisfy acceptance criteria.

### 3) Branch and commit hygiene
1. Use one clean worktree and one dedicated branch per issue from `main` (or the current canonical base branch):
   - `codex/issue-<id>-<short-slug>`
2. Do not re-use a dirty checkout; do not mix multiple issue scopes on one branch.
3. Commit regularly in logical units with meaningful, imperative commit messages.
4. Keep changes reviewable and include documentation updates when behavior/process changes.

### 4) Validation before PR
1. Verify each `Done when` item is satisfied.
2. Run or perform the checks listed in `Verification`; if something cannot be run, document why.
3. Confirm no contradiction with existing repository guidance (`CONTRIBUTING.md`, `ISSUE_CREATION_GUIDELINES.md`, templates).

### 5) PR creation and issue closeout communication
1. Open a pull request against the correct base branch with:
   - Clear summary of what changed.
   - Test/verification evidence.
   - Explicit link to the issue (for example `Closes #<id>`).
2. Post an issue update comment after opening the PR that includes:
   - What was implemented.
   - Key decisions made.
   - Tradeoffs or known limitations.
   - PR link.
3. If follow-up work is needed, list it explicitly in the issue or PR.

### Maintainer verification checklist (quick review)
Use this checklist to confirm an issue was handled end-to-end with expected hygiene:
- Issue was unassigned/not active before pickup, then assigned at start.
- Work started in a clean worktree (no unrelated modified files at kickoff).
- Start comment was posted before substantive implementation.
- Dedicated branch follows `codex/issue-<id>-...` pattern.
- Commits are scoped and messages are meaningful.
- PR references/closes the issue and includes verification evidence.
- Final issue update comment summarizes implementation, decisions, and tradeoffs.
