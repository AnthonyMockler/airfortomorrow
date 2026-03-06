# User Testing Notes: README Quick Start Walkthrough

Session: 2026-03-06 (Asia/Bangkok, UTC+7)
Repository: `/Users/anthonymockler/Documents/split/air_quality_prediction`
Tester mode: First-time user simulation (no code changes)

---

## Step 0
**Timestamp:** 2026-03-06 16:04:08 +07  
**What step I am about to take:** Locate the README file and confirm repository root contents.  
**Why I am taking this step / where I am reading from:** README is the entry point for first-time setup; this follows user request and `README.md` discovery from repo root.  
**What I expect to happen:** I should find `README.md` and core project directories (`scripts`, `src`, `config`, etc.).  
**What actually happened:** `README.md` was found. Root listing confirmed expected structure including `scripts/`, `src/`, `config/`, `data/`, `assets/`, and supporting docs.

## Step 1
**Timestamp:** 2026-03-06 16:04:08 +07  
**What step I am about to take:** Open `README.md` and extract the Quick Start section.  
**Why I am taking this step / where I am reading from:** The requested exercise is to follow Quick Start exactly; source is `README.md` section `## Quick Start`.  
**What I expect to happen:** I should see prerequisites and a numbered setup flow (clone, credentials, docker, run pipeline, verify outputs).  
**What actually happened:** Quick Start was found at `README.md` line 76. It contains:
- Prerequisites: Docker, Git LFS, API credentials (Himawari, CDS, OpenAQ)
- Step 1: Clone + Git LFS commands
- Step 2: `cp env_template .env`
- Step 3: `docker build` + `docker run`
- Step 4: `./scripts/setup.sh` then `./scripts/run_complete_pipeline.sh ...`
- Step 5: output verification paths

## Step 2
**Timestamp:** 2026-03-06 16:04:08 +07  
**What step I am about to take:** Capture baseline local repo state before executing Quick Start commands.  
**Why I am taking this step / where I am reading from:** Good user-testing hygiene before setup actions; aligns with reproducibility and traceability.  
**What I expect to happen:** Branch and status should be readable, ideally clean or at least known.  
**What actually happened:** Current branch is `main`. No staged/unstaged tracked file changes were shown at that moment.

## Step 3
**Timestamp:** 2026-03-06 16:04:41 +07  
**What step I am about to take:** Validate Quick Start prerequisites (Docker, Git LFS, and credential template readiness).  
**Why I am taking this step / where I am reading from:** `README.md` Quick Start -> `Prerequisites` section (lines 78-84).  
**What I expect to happen:** Docker and Git LFS should be installed; env template should clearly list required credentials; `.env` should be straightforward to create from template.  
**What actually happened:**
- Docker client and daemon appear available: `docker --version` -> `27.5.1`; `docker info` returned server version `27.5.1`.
- Git LFS is installed: `git-lfs/3.7.1`.
- `env_template` includes required variables (`HIMAWARI_FTP_USER`, `HIMAWARI_FTP_PASSWORD`, `CDSAPI_URL`, `CDSAPI_KEY`, `OPENAQ_API_KEY`).
- Important friction found: `.env` currently exists as a **directory**, not a file. This conflicts with Quick Start Step 2 (`cp env_template .env`) and may confuse first-time users if their local environment has the same state.

## Step 4
**Timestamp:** 2026-03-06 16:05:05 +07  
**What step I am about to take:** Execute Quick Start Step 1 actions for Git LFS bootstrap and verify repository remote context.  
**Why I am taking this step / where I am reading from:** `README.md` Quick Start Step 1 (`git clone ...`, `git lfs install`, `git lfs pull`).  
**What I expect to happen:** LFS should initialize cleanly, and large files should be fetched without errors.  
**What actually happened:**
- `git lfs install` succeeded (`Updated Git hooks. Git LFS initialized.`).
- `git lfs pull` returned successfully with no additional output.
- Remote context check showed:
  - `upstream`: `https://github.com/unicef/air_quality_prediction.git`
  - `anthony`: `https://github.com/AnthonyMockler/air_quality_prediction.git`
- Usability note: README clone URL points to the UNICEF repo, while this working copy also has a personal fork remote. This is normal for contributors, but could be clarified for first-time users deciding which remote to clone from.

## Step 5
**Timestamp:** 2026-03-06 16:05:29 +07  
**What step I am about to take:** Run Quick Start Step 2 command `cp env_template .env`.  
**Why I am taking this step / where I am reading from:** `README.md` Quick Start Step 2 (`Configure credentials`).  
**What I expect to happen:** A root-level `.env` file should be created from `env_template`, then user edits credentials in that file.  
**What actually happened:**
- Command executed successfully, but because `.env` is currently a directory, output was: `env_template -> .env/env_template`.
- Resulting file path is `.env/env_template` (not root `.env` file expected by Docker mount command in Step 3).
- User-impact note: This is a high-friction setup trap. A first-time user can believe they completed Step 2, but Step 3 expects `-v "$(pwd)/.env:/app/.env"` where `.env` should be a **file**.

## Step 6
**Timestamp:** 2026-03-06 16:13:46 +07  
**What step I am about to take:** Apply user-provided fix: remove accidental `.env` directory, create proper root `.env` file, and populate credentials.  
**Why I am taking this step / where I am reading from:** Follow-up instruction from user during test session to correct setup and restart testing.  
**What I expect to happen:** `.env` should become a regular file (not directory), with required variables present so collectors can authenticate.  
**What actually happened:**
- Confirmed starting state: `.env` was a directory.
- Removed directory and created root `.env` file from template workflow.
- Populated values for `HIMAWARI_FTP_USER`, `HIMAWARI_FTP_PASSWORD`, `CDSAPI_URL`, `CDSAPI_KEY`, and `OPENAQ_API_KEY`.
- Verified `.env` is now `ASCII text` file at repo root and all required keys exist.

---

## Restarted Walkthrough (Run 2, with credentials configured)

## Step 7
**Timestamp:** 2026-03-06 16:14:12 +07  
**What step I am about to take:** Re-open README Quick Start and restate the documented sequence before rerun.  
**Why I am taking this step / where I am reading from:** User asked to restart the entire process from scratch after `.env` correction; source is `README.md` Quick Start lines 76-127.  
**What I expect to happen:** The same five-step flow should be identifiable and executable with corrected credential setup.  
**What actually happened:** Quick Start section confirmed with expected subsections: Prerequisites, Clone, Configure credentials, Build/Run Docker, In-container pipeline run, and output verification.

## Step 8
**Timestamp:** 2026-03-06 16:15:52 +07  
**What step I am about to take:** Re-check prerequisites in Run 2 (`docker`, `git lfs`, and `.env` validity).  
**Why I am taking this step / where I am reading from:** `README.md` Quick Start `Prerequisites` and Step 2 dependency assumptions.  
**What I expect to happen:** Docker and Git LFS should still be installed; `.env` should now be a valid file with required keys.  
**What actually happened:**
- Docker client/server available (`27.5.1`).
- Git LFS available (`3.7.1`).
- `.env` now correctly appears as a file (`ASCII text`), not a directory.
- Required keys are present in `.env`: Himawari FTP, CDS API URL/key, and OpenAQ key.

## Step 9
**Timestamp:** 2026-03-06 16:24:38 +07  
**What step I am about to take:** Re-run Quick Start Step 1 Git LFS commands in Run 2.  
**Why I am taking this step / where I am reading from:** `README.md` Quick Start Step 1 requires `git lfs install` and `git lfs pull` after clone.  
**What I expect to happen:** LFS should initialize (idempotent) and pull command should complete without error.  
**What actually happened:**
- `git lfs install` succeeded (`Updated Git hooks. Git LFS initialized.`).
- `git lfs pull` returned successfully with no additional output.
- Remote inspection still shows both `upstream` (UNICEF) and `anthony` remotes in this local checkout.

## Step 10
**Timestamp:** 2026-03-06 16:24:38 +07  
**What step I am about to take:** Recover from mid-test interruption and verify baseline before continuing Run 2.  
**Why I am taking this step / where I am reading from:** User requested continuation after interruption; good practice is to validate no leftover runtime state.  
**What I expect to happen:** No active containers, `.env` still valid, and repo state stable for next step.  
**What actually happened:**
- `docker ps` shows no running containers.
- `.env` remains a root file.
- Working tree has only the running test log (`USER_TESTING_QUICKSTART_NOTES.md`) as untracked.

## Step 11
**Timestamp:** 2026-03-06 16:39:25 +07  
**What step I am about to take:** Execute Quick Start Step 3 (`docker build -t airquality-app .`) in Run 2.  
**Why I am taking this step / where I am reading from:** `README.md` Quick Start Step 3 requires local image build before container run.  
**What I expect to happen:** Docker build should complete (mostly cached), with image `airquality-app:latest` available.  
**What actually happened:**
- Build completed successfully using mostly cached layers.
- Image exported and tagged as `airquality-app:latest`.
- Same two Dockerfile warnings seen as Run 1 (`UndefinedVar` for `$PYTHONPATH` and `$LD_LIBRARY_PATH`), non-blocking.

## Step 12
**Timestamp:** 2026-03-06 16:39:25 +07  
**What step I am about to take:** Execute Quick Start Step 3 runtime command (`docker run ... -v $(pwd)/.env:/app/.env ...`).  
**Why I am taking this step / where I am reading from:** Continue documented Quick Start flow into containerized runtime.  
**What I expect to happen:** Container should start, pass setup checks, and drop into shell.  
**What actually happened:**
- Container startup succeeded.
- Bootstrap file validation passed.
- Runtime still prints `./scripts/setup.sh: line 147: free: command not found` (non-fatal but noisy).
- Shell prompt opened at `/app` as expected.

## Step 13
**Timestamp:** 2026-03-06 16:39:25 +07  
**What step I am about to take:** Execute Quick Start Step 4 first command `./scripts/setup.sh` inside container.  
**Why I am taking this step / where I am reading from:** Step 4 explicitly instructs running setup before first prediction command.  
**What I expect to happen:** Setup should verify dependencies and finish successfully.  
**What actually happened:**
- Setup completed successfully.
- Same non-fatal `free: command not found` message appeared.

## Step 14
**Timestamp:** 2026-03-06 16:39:25 +07  
**What step I am about to take:** Execute Quick Start Step 4 main command:
`./scripts/run_complete_pipeline.sh --mode realtime --countries THA LAO --generate-maps --parallel`  
**Why I am taking this step / where I am reading from:** This is the first full prediction run defined by Quick Start.  
**What I expect to happen:** Data collection, processing, silver dataset generation, and prediction pipeline should run end-to-end (first run ~20-40 minutes per README).  
**What actually happened (ongoing run snapshot):**
- Major improvement after credential fix: previously failing pipelines now authenticate and run.
- Completed successfully so far:
  - FIRMS (~95s)
  - Himawari (~206s)
  - AirGradient (~532s)
  - ERA5 (~680s)
- Remaining in progress: OpenAQ collection.
  - OpenAQ log shows active batch processing (743 sensors, batch size 10, 2 workers).
- Progress reached roughly batch `33/75` (~43%) at snapshot time.
- Observed intermittent read timeouts/retries, but pipeline continues.
- Top-level orchestrator output still only shows heartbeat lines while OpenAQ runs (`Still running: openaq`), which can feel opaque without opening component logs.

## Step 15
**Timestamp:** 2026-03-06 16:46:32 +07  
**What step I am about to take:** Continue monitoring the same Run 2 pipeline command until either completion or meaningful timeboxed observation point.  
**Why I am taking this step / where I am reading from:** `README.md` indicates first run may take 20-40 minutes; this step checks whether flow reaches downstream phases in that window.  
**What I expect to happen:** OpenAQ should eventually complete, allowing pipeline to move to processing/silver/prediction phases.  
**What actually happened:**
- Over additional monitoring, OpenAQ remained the final active collector.
- Progress advanced to `Batch 52/75` before stopping observation.
- Orchestrator repeatedly printed only `Still running: openaq` without detailed sub-progress.
- I stopped with `Ctrl+C` at this checkpoint to capture a reproducible timeboxed first-user experience snapshot.

## Step 16
**Timestamp:** 2026-03-06 16:46:32 +07  
**What step I am about to take:** Execute Quick Start Step 5 verification checks after the interrupted/timeboxed run.  
**Why I am taking this step / where I am reading from:** `README.md` Quick Start Step 5 defines expected output locations for silver dataset, predictions, maps, and logs.  
**What I expect to happen:** If pipeline completed, output directories/files should exist under `data/silver/realtime` and `data/predictions/...`.  
**What actually happened:**
- `data/silver/realtime`: not present.
- `data/predictions/data/realtime`: not present.
- `data/predictions/map/realtime`: not present.
- Latest pipeline log exists: `logs/complete_pipeline_20260306_092551.log`.
- Interpretation: Step 5 outputs are blocked until OpenAQ finishes and pipeline advances beyond data collection.
