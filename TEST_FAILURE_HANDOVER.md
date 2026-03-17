# Test Failure Handover (from full run `2026-03-16`)

## 1) `features/contracts/behave_compact_shim.feature:12`
- **Failed test:** root agent guidance points to compact Behave shim.
- **Evidence:** full-run failure list in [airfortomorrow-behave-20260316-102905.log:18](/var/folders/gv/_b6pxv9j6k50mxj4c6blq3040000gn/T/airfortomorrow-behave-20260316-102905.log:18); explicit assertion in [behave_compact_latest.log:15](/tmp/behave_compact_latest.log:15) says root `AGENTS.md` is missing `"full raw output is explicitly needed"`.
- **Suggested fix:** add that exact phrase to root [AGENTS.md:44](/Users/anthonymockler/Documents/unicef/airfortomorrow/AGENTS.md:44) (it already exists in [tests/AGENTS.md:24](/Users/anthonymockler/Documents/unicef/airfortomorrow/tests/AGENTS.md:24)).

## 2) `features/contracts/behave_compact_shim.feature:17`
- **Failed test:** compact shim long-run output guidance.
- **Evidence:** listed as failed in full-run log [airfortomorrow-behave-20260316-102905.log:19](/var/folders/gv/_b6pxv9j6k50mxj4c6blq3040000gn/T/airfortomorrow-behave-20260316-102905.log:19); targeted rerun now passes in [behave_compact_latest.log:18](/tmp/behave_compact_latest.log:18).
- **Suggested fix:** treat as transitive from failure #1; fix #1 and rerun full suite.

## 3) `features/contracts/himawari_downloader_contract.feature:11`
- **Failed test:** historical downloader-only bounded raw files.
- **Evidence:** listed in full-run failures [airfortomorrow-behave-20260316-102905.log:20](/var/folders/gv/_b6pxv9j6k50mxj4c6blq3040000gn/T/airfortomorrow-behave-20260316-102905.log:20); same feature is currently flaky (reruns can pass).
- **Suggested fix:** harden raw-file assertions to avoid relying on the newest `.nc` file; use “at least one updated non-empty file” semantics.

## 4) `features/contracts/himawari_downloader_contract.feature:22`
- **Failed test:** realtime downloader-only bounded raw files.
- **Evidence:** full-run failure list [airfortomorrow-behave-20260316-102905.log:21](/var/folders/gv/_b6pxv9j6k50mxj4c6blq3040000gn/T/airfortomorrow-behave-20260316-102905.log:21); related brittle assertion is in [himawari_steps.py:155](/Users/anthonymockler/Documents/unicef/airfortomorrow/features/steps/himawari_steps.py:155) (requires *latest* raw file non-empty). Himawari logs show newest files can be “no valid data” and removed, e.g. [integrated_realtime_pipeline_20260316_041745.log:289](/Users/anthonymockler/Documents/unicef/airfortomorrow/logs/integrated_realtime_pipeline_20260316_041745.log:289).
- **Suggested fix:** change step logic in [himawari_steps.py:155](/Users/anthonymockler/Documents/unicef/airfortomorrow/features/steps/himawari_steps.py:155) to validate any updated non-empty `.nc` file (or latest non-empty), not strictly latest-by-mtime.

## 5) `features/contracts/himawari_realtime_contract.feature:26`
- **Failed test:** realtime integrated Himawari artifacts.
- **Evidence:** listed in full-run failures [airfortomorrow-behave-20260316-102905.log:22](/var/folders/gv/_b6pxv9j6k50mxj4c6blq3040000gn/T/airfortomorrow-behave-20260316-102905.log:22). Recent targeted rerun passed end-to-end with all artifact checks.
- **Suggested fix:** treat as flake; add retry-once policy for this live slow scenario and capture raw scenario logs on first failure for deterministic triage.

## 6) `features/quickstart/basic_workflow.feature:26`
- **Failed test:** realtime run authentication-failure scan.
- **Evidence:** listed in full-run failures [airfortomorrow-behave-20260316-102905.log:23](/var/folders/gv/_b6pxv9j6k50mxj4c6blq3040000gn/T/airfortomorrow-behave-20260316-102905.log:23). Scenario timeout is 900s in [basic_workflow.feature:28](/Users/anthonymockler/Documents/unicef/airfortomorrow/features/quickstart/basic_workflow.feature:28); similar realtime pipeline runs can be near/over this range.
- **Suggested fix:** raise timeout margin (e.g. 1200s) or reduce workload in this scenario (`--hours 6`) to remove timeout-driven flake.

## 7) `features/smoke/setup_script.feature:5`
- **Failed test:** `setup.sh` success markers.
- **Evidence:** listed in full-run failures [airfortomorrow-behave-20260316-102905.log:24](/var/folders/gv/_b6pxv9j6k50mxj4c6blq3040000gn/T/airfortomorrow-behave-20260316-102905.log:24). Root cause was outdated bootstrap manifest expectations (old CSV assets) in [setup.sh:57](/Users/anthonymockler/Documents/unicef/airfortomorrow/scripts/setup.sh:57).
- **Suggested fix:** already implemented: update [bootstrap_assets_manifest.tsv:2](/Users/anthonymockler/Documents/unicef/airfortomorrow/assets/checksums/bootstrap_assets_manifest.tsv:2) to parquet entries; keep this as regression check.

---

**Note on “huge skipped” counts:** in subset runs (like smoke), large skips are expected from tag filtering; example in [smoke_latest.log:529](/tmp/smoke_latest.log:529).
