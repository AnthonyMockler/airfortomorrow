# Public Release Gap Analysis (Pre-Release Pass)

**Date:** 2026-03-06  
**Scope:** Repository-readiness for making this private project public, with focus on clarity, runnability, and professional OSS posture.

## 1) Research-backed Checklist

Checklist criteria were built from:
- GitHub collaboration/readiness guidance: [Is your repository collaboration-ready?](https://assets.ctfassets.net/wfutmusr1t3h/5rVxDuN6xj6D0kP2fQmIoT/e1f74f2f177e13d76a9f9f77989eebaf/Collaboration-readme.pdf)
- GitHub Docs community health files: [About community profiles for public repositories](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-community-profiles-for-public-repositories)
- GitHub Docs contributor/support files: [Setting guidelines for repository contributors](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors), [Adding support resources](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/adding-support-resources-to-your-project), [Configuring private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/working-with-repository-security-advisories/configuring-private-vulnerability-reporting-for-a-repository)
- Open Source Guides: [Starting an Open Source Project](https://opensource.guide/starting-a-project/)
- OpenSSF Scorecard checks: [scorecard checks](https://github.com/ossf/scorecard/blob/main/docs/checks.md)

### Checklist Status

| Area | Criterion | Status | Notes |
|---|---|---|---|
| Community health | `README.md`, `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md` present | ✅ | Present and substantial |
| Community health | `CODE_OF_CONDUCT.md` present | ❌ | Missing |
| Community health | `SUPPORT.md` present | ❌ | Missing |
| Community health | PR template present | ❌ | Missing (`.github/pull_request_template.md`) |
| Governance | `CODEOWNERS` present | ❌ | Missing |
| Security | Private vulnerability reporting enabled in GitHub settings | ⚠️ | Not verifiable from local repo |
| Security | No embedded access signatures/secret-like tokens in tracked files | ❌ | Signed Azure blob URLs committed in setup script |
| Security | Avoid shell injection patterns in wrappers (`eval`) | ❌ | Multiple wrappers use `eval` |
| Run experience | Quick-start commands match actual scripts/flags | ⚠️ | Drift/mismatch found in docs and entrypoint output |
| Run experience | Entrypoint/help text references valid commands | ❌ | Entrypoint lists non-existent scripts |
| Run experience | Minimal dependency friction for discovery (`--help`) | ⚠️ | Wrapper help paths fail without `yq` |
| CI quality gates | Automated tests exist and run in CI | ❌ | `pytest` finds zero tests; no test workflow |
| CI quality gates | Lint/type/static checks in CI | ❌ | No lint/type workflows found |
| Build hygiene | Docker ignore file correctly named `.dockerignore` | ✅ | `.dockerignore` is present and used by Docker builds |
| OSS polish | Changelog/release notes process documented | ❌ | No `CHANGELOG.md` or release process doc |

## 2) Prioritized Issue Backlog

### P0 (Fix Before Public Release)

1. **Add missing community-health files (`CODE_OF_CONDUCT.md`, `SUPPORT.md`, PR template).**  
   Why: These are first-class GitHub collaboration signals and reduce friction for public contributors.
   Evidence: files absent at repo root and `.github/`.

2. **Remove embedded signed blob URLs from setup scripts and replace with durable/public-safe distribution.**  
   Why: Signed query tokens in source are sensitive operational material and can expire, breaking onboarding.
   Evidence: [scripts/setup.sh](scripts/setup.sh):70 (and lines 71-77 contain `sig=` query parameters).

3. **Introduce minimum automated tests and wire them into CI.**  
   Why: Public users and contributors need basic confidence against regressions.
   Evidence: local `pytest -q` => `no tests ran`; workflows currently only cover notebook hygiene and security scans.

4. **Fix command drift in container entrypoint and README examples.**  
   Why: Broken/stale command guidance damages first-run experience.
   Evidence: [entrypoint.sh](entrypoint.sh):24 references `run_era5_integrated_pipeline.sh` (missing), [entrypoint.sh](entrypoint.sh):31 references `make_silver.sh.sh`, [entrypoint.sh](entrypoint.sh):36-37 references missing training scripts; [README.md](README.md):305 uses `--generate-maps` but script accepts `--generate-map`.

### P1 (Strongly Recommended Before Public Release)

5. **Replace `eval`-based command execution in shell wrappers with argument-safe arrays.**  
   Why: `eval` is avoidable risk and conflicts with security-hardening expectations for public repos.
   Evidence: [scripts/run_firms_kde.sh](scripts/run_firms_kde.sh):208, [scripts/run_firms_kde_historical.sh](scripts/run_firms_kde_historical.sh):204, [scripts/run_era5_realtime.sh](scripts/run_era5_realtime.sh):179.

6. **Remove or repair stale `run_era5_realtime.sh` path.**  
   Why: Script currently points to a non-existent module, causing deterministic failure when used.
   Evidence: [scripts/run_era5_realtime.sh](scripts/run_era5_realtime.sh):179 calls `src/data_collectors/era5_meteorological.py` (missing; current implementation is `era5_meteorological_idw.py` / integrated pipeline).

7. **Add `CODEOWNERS` and define review ownership.**  
   Why: Clarifies responsibility and accelerates contribution handling.
   Evidence: no `CODEOWNERS` or `.github/CODEOWNERS`.

8. **Keep `.dockerignore` exclusions aligned with Docker build inputs.**  
   Why: A lean context reduces build time and lowers accidental file leakage into images.
   Evidence: [.dockerignore](.dockerignore):1 defines cache, VCS, env, and virtualenv exclusions.

### P2 (Professional Polish / Follow-up)

9. **Add release/change communication artifact (`CHANGELOG.md` or GitHub Releases policy).**  
   Why: Improves transparency for external users when behavior changes.
   Evidence: no changelog/release notes file.

10. **Make wrapper scripts resilient when `yq` is missing (especially for `--help`).**  
    Why: New contributors often try `--help` first; hard failure is unnecessary friction.
    Evidence: [scripts/utils/config_reader.sh](scripts/utils/config_reader.sh):12-14 exits immediately if `yq` not present.

## 3) Suggested Fix Order

1. P0 items 1-4 (public-facing trust and runability).
2. P1 items 5-8 (security posture and maintainability).
3. P2 items 9-10 (polish and contributor UX).
