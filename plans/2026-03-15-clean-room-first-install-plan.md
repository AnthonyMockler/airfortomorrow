# Clean Room First-Install Plan

- Status: Planned
- Owner: Codex
- Last Updated: 2026-03-15

## Goal

Reproduce a true first-time user experience by executing only the README Quick Start install steps inside a newly created isolated Docker daemon that has no prior project images, layers, containers, or volumes.

This must detect onboarding failures that local-dev state can hide, including the failures Achim reported.

- missing `git-lfs` install step (`brew install git-lfs` on macOS)
- incorrect build context causing missing `requirements.txt` / `entrypoint.sh`
- incomplete checkout/LFS hydration that makes repo appear partially empty
- missing `env_template` or broken `.env` setup path

## README-Only Contract

The clean-room harness may orchestrate isolation, but the install sequence inside the isolated environment must come only from `README.md` Quick Start.

Allowed install commands are exactly:

1. `git clone https://github.com/unicef/airfortomorrow.git`
2. `cd airfortomorrow`
3. `git lfs install`
4. `git lfs pull`
5. `cp env_template .env`
6. `docker build -t airquality-app .`
7. `docker run --rm -it --memory=16g ... airquality-app` (same mounts/flags as README)
8. inside container:
   - `./scripts/setup.sh`
   - `./scripts/run_complete_pipeline.sh --mode realtime --countries THA LAO --generate-maps --parallel`

No extra install commands, no substituted flags, and no standalone "file exists" assertions as pass criteria.

## Isolation Model

1. Start an ephemeral Docker daemon (`docker:dind`) with a brand-new data root.
2. Run all onboarding steps from a separate runner container against that daemon.
3. Clone from remote inside the isolated runner workspace.
4. Execute the exact README command sequence above.
5. Destroy daemon + workspace after run.

No host checkout, host image cache, or host project volumes are used.

## Red

Add behavior tests for strict README replay in clean-room:

1. Add `@cleanroom` Behave feature that runs the clean-room README replay harness.
2. Scenario A: strict README replay in isolated daemon (expected to fail today if docs are incomplete or assumptions are hidden).
3. Scenario B: strict README replay with required credentials provided via CI secrets.
4. Capture RED evidence:
   - `./scripts/run_behave_tests_compact.sh --tags='@cleanroom'`

## Green

### Phase 1: Strict README Replay Harness

Add `scripts/clean_room_first_install.sh` as the canonical entrypoint:

1. Launch ephemeral `docker:dind` container with random name and fresh volume.
2. Wait for isolated daemon health (`docker info` via `DOCKER_HOST`).
3. Launch runner container with `git`, `git-lfs`, `bash`, and `docker` CLI.
4. In runner, execute only the README Quick Start commands in the same order and syntax.
5. Export run logs/report to host `logs/cleanroom/`.
6. Tear down daemon container and ephemeral volume.

### Phase 2: README Gap Reporting

If strict replay fails, classify failure as a README onboarding gap and report:

1. failing README step number
2. exact command
3. first actionable error line
4. suggested README fix (docs change, not harness workaround)

### Phase 3: CI Execution

Add `.github/workflows/clean-room-first-install.yml`:

1. Run on `workflow_dispatch`.
2. Run on schedule (weekly preferred).
3. Use fresh GitHub-hosted runner and invoke `scripts/clean_room_first_install.sh`.
4. Upload clean-room logs/report artifacts.

Keep this workflow non-blocking for normal PR checks until stable.

### Phase 4: Disk/Resource Reporting

The harness must emit:

1. bytes downloaded by clone + LFS pull
2. clean-room image size
3. peak Docker data-root size
4. wall-clock time per stage

Use this to publish real first-install guidance for Mac users.

## Verification

1. `./scripts/run_behave_tests_compact.sh --tags='@cleanroom'`
2. `./scripts/clean_room_first_install.sh`
3. `./scripts/smoke_test.sh`

Acceptance criteria:

1. Entire flow succeeds from an isolated daemon with no reused project cache.
2. Install steps executed in clean-room are exactly the README Quick Start steps.
3. Failures are reported as README step failures with raw command/error evidence.
4. Clean-room report includes enough data to answer disk-space onboarding questions.

## Notes

1. This plan intentionally avoids relying on the local checkout to validate first-install behavior.
2. Existing quickstart tests remain useful for regression, but strict README replay in clean-room is the onboarding gate.
