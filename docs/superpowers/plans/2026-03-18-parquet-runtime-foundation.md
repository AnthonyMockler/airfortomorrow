# Parquet Runtime Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Introduce manifest-based partition publication plus a rebuildable SQLite index, then pilot the new runtime on silver dataset publication and prediction reads without rewriting every source pipeline at once.

**Architecture:** Add a small shared runtime under `src/runtime/` for dataset layout, manifest serialization, publish/read semantics, SQLite indexing, and backfill planning. Keep the public shell-wrapper workflow intact, preserve Parquet as the storage truth, and migrate `silver.features` and `predictions.pm25` first while upstream processed datasets remain on their current layout.

**Tech Stack:** Python 3, Parquet, Polars, PyArrow datasets/filesystems, SQLite, JSON manifests, Behave, pytest, shell wrappers in `scripts/`

---

## Scope Guard

This spec covers multiple independent migrations. This plan intentionally handles only the first shippable slice:

- shared manifest/runtime foundation
- SQLite index and rebuild/status commands
- `data/silver/*` publish semantics
- prediction reads through manifest resolution

Follow-on plans should migrate `data/processed/*` source datasets one family at a time.

## File Structure

- Create: `src/runtime/__init__.py`
- Create: `src/runtime/layout.py`
- Create: `src/runtime/manifest.py`
- Create: `src/runtime/publish.py`
- Create: `src/runtime/read.py`
- Create: `src/runtime/index_db.py`
- Create: `src/runtime/backfill.py`
- Create: `src/runtime/cli.py`
- Create: `tests/test_runtime_config.py`
- Create: `tests/test_runtime_layout.py`
- Create: `tests/test_runtime_publish.py`
- Create: `tests/test_runtime_index_db.py`
- Create: `tests/test_silver_runtime.py`
- Create: `tests/test_runtime_backfill.py`
- Create: `features/contracts/parquet_runtime_contract.feature`
- Create: `features/steps/parquet_runtime_steps.py`
- Create: `scripts/rebuild_partition_index.sh`
- Create: `scripts/show_partition_status.sh`
- Modify: `config/config.yaml`
- Modify: `src/utils/config_loader.py`
- Modify: `scripts/utils/config_reader.sh`
- Modify: `src/make_silver.py`
- Modify: `scripts/make_silver.sh`
- Modify: `src/predict_air_quality.py`
- Modify: `scripts/predict_air_quality.sh`
- Modify: `docs/DATAFLOW.md`
- Modify: `docs/ARCHITECTURE.md`

### Task 1: Add Runtime Config and Path Plumbing

**Files:**
- Create: `tests/test_runtime_config.py`
- Modify: `config/config.yaml`
- Modify: `src/utils/config_loader.py`
- Modify: `scripts/utils/config_reader.sh`

- [ ] **Step 1: Write the failing config tests**

```python
from src.utils.config_loader import ConfigLoader


def test_runtime_metadata_paths_exist_in_config():
    config = ConfigLoader()
    assert config.get_path("metadata.base")
    assert config.get_path("metadata.sqlite")
    assert config.get_path("metadata.manifests")
```

- [ ] **Step 2: Run the targeted pytest**

Run: `./scripts/run_tests.sh -- tests/test_runtime_config.py -q`
Expected: FAIL because the runtime metadata path keys do not exist yet.

- [ ] **Step 3: Add config keys for metadata and runtime roots**

```yaml
paths:
  metadata:
    base: "data/metadata"
    sqlite: "data/metadata/runtime_index.sqlite"
    manifests: "data/metadata/manifests"
```

Also add minimal helper coverage in both config readers so Python and shell code resolve the same paths.

- [ ] **Step 4: Re-run the targeted pytest**

Run: `./scripts/run_tests.sh -- tests/test_runtime_config.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_runtime_config.py config/config.yaml src/utils/config_loader.py scripts/utils/config_reader.sh
git commit -m "feat: add runtime metadata configuration"
```

### Task 2: Lock the Publish Contract With Behave

**Files:**
- Create: `features/contracts/parquet_runtime_contract.feature`
- Create: `features/steps/parquet_runtime_steps.py`
- Create: `tests/test_runtime_layout.py`

- [ ] **Step 1: Write a Tier A contract feature for runtime publication**

Cover these behaviors:

- `scripts/show_partition_status.sh` fails clearly for an unknown dataset
- publishing a test partition writes `current.json` plus an immutable run manifest
- rebuilding the index from manifests reproduces published partition state

- [ ] **Step 2: Add minimal step definitions that intentionally fail**

```python
@then("the published partition should have a current manifest pointer")
def step_impl(context):
    raise AssertionError("not implemented")
```

- [ ] **Step 3: Run Tier A Behave**

Run: `./scripts/run_behave_tests_compact.sh --tier a`
Expected: FAIL because the new runtime contract is red.

- [ ] **Step 4: Add a focused unit test for layout rules**

```python
def test_partition_layout_does_not_partition_by_h3():
    layout = dataset_partition_path("silver.features", mode="historical", date="2025-01-03", country="THA")
    assert "h3_08=" not in str(layout)
```

- [ ] **Step 5: Run the targeted pytest**

Run: `./scripts/run_tests.sh -- tests/test_runtime_layout.py -q`
Expected: FAIL because no runtime layout module exists yet.

- [ ] **Step 6: Commit the red tests**

```bash
git add features/contracts/parquet_runtime_contract.feature features/steps/parquet_runtime_steps.py tests/test_runtime_layout.py
git commit -m "test: add runtime publish contracts"
```

### Task 3: Implement Runtime Layout and Manifest Models

**Files:**
- Create: `src/runtime/__init__.py`
- Create: `src/runtime/layout.py`
- Create: `src/runtime/manifest.py`
- Modify: `tests/test_runtime_layout.py`

- [ ] **Step 1: Implement dataset and partition path derivation**

```python
def dataset_partition_path(dataset: str, *, mode: str, date: str, country: str) -> str:
    return f"{dataset_root(dataset)}/mode={mode}/date={date}/country={country}"
```

The implementation should also provide helper paths for:

- `runs/run-<run_id>/`
- `manifests/run-<run_id>.json`
- `manifests/current.json`

- [ ] **Step 2: Implement manifest models and serialization**

```python
@dataclass(frozen=True)
class PartitionManifest:
    dataset: str
    mode: str
    date: str
    country: str
    run_id: str
    files: list[str]
    row_count: int
    schema_fingerprint: str
```

- [ ] **Step 3: Re-run the unit tests**

Run: `./scripts/run_tests.sh -- tests/test_runtime_layout.py -q`
Expected: PASS

- [ ] **Step 4: Add one more manifest serialization test**

Run: `./scripts/run_tests.sh -- tests/test_runtime_layout.py tests/test_runtime_publish.py -q`
Expected: `tests/test_runtime_publish.py` is still missing or failing, which is acceptable before Task 4.

- [ ] **Step 5: Commit**

```bash
git add src/runtime/__init__.py src/runtime/layout.py src/runtime/manifest.py tests/test_runtime_layout.py
git commit -m "feat: add runtime layout and manifest models"
```

### Task 4: Implement Publish, Read, and SQLite Index Semantics

**Files:**
- Create: `src/runtime/publish.py`
- Create: `src/runtime/read.py`
- Create: `src/runtime/index_db.py`
- Create: `tests/test_runtime_publish.py`
- Create: `tests/test_runtime_index_db.py`

- [ ] **Step 1: Write failing publish and index tests**

```python
def test_publish_partition_writes_current_pointer(tmp_path):
    result = publish_partition(...)
    assert result.current_manifest_path.exists()


def test_rebuild_index_from_manifests_restores_partition_state(tmp_path):
    rebuild_index_from_storage(...)
    assert fetch_partition(...).run_id == "run-123"
```

- [ ] **Step 2: Run the targeted pytest**

Run: `./scripts/run_tests.sh -- tests/test_runtime_publish.py tests/test_runtime_index_db.py -q`
Expected: FAIL because publish and index modules do not exist yet.

- [ ] **Step 3: Implement the publish protocol**

The minimal publish flow should:

1. write Parquet to a run-scoped directory
2. validate files and schema
3. write `run-<run_id>.json`
4. update `current.json`
5. upsert the SQLite index

- [ ] **Step 4: Implement manifest-based reads**

```python
def resolve_current_manifest(dataset: str, *, mode: str, date: str, country: str) -> PartitionManifest:
    ...
```

Prediction and downstream code should be able to consume file lists from this API later without knowing the on-disk layout.

- [ ] **Step 5: Re-run the targeted pytest**

Run: `./scripts/run_tests.sh -- tests/test_runtime_publish.py tests/test_runtime_index_db.py -q`
Expected: PASS

- [ ] **Step 6: Run Tier A Behave**

Run: `./scripts/run_behave_tests_compact.sh --tier a`
Expected: the new contract is closer to green, though wrapper-command scenarios may still fail until Task 5.

- [ ] **Step 7: Commit**

```bash
git add src/runtime/publish.py src/runtime/read.py src/runtime/index_db.py tests/test_runtime_publish.py tests/test_runtime_index_db.py
git commit -m "feat: add manifest publish runtime"
```

### Task 5: Add Supported Wrapper Commands for Index Rebuild and Status

**Files:**
- Create: `src/runtime/cli.py`
- Create: `scripts/rebuild_partition_index.sh`
- Create: `scripts/show_partition_status.sh`
- Modify: `features/contracts/parquet_runtime_contract.feature`
- Modify: `features/steps/parquet_runtime_steps.py`

- [ ] **Step 1: Add failing wrapper assertions to Behave**

Cover:

- bad dataset name fails fast with a clear message
- rebuild command succeeds against fixture manifests
- status command prints the currently published run id

- [ ] **Step 2: Run Tier A Behave**

Run: `./scripts/run_behave_tests_compact.sh --tier a`
Expected: FAIL because the wrapper scripts do not exist yet.

- [ ] **Step 3: Implement the runtime CLI and shell wrappers**

```bash
./scripts/rebuild_partition_index.sh --dataset silver.features
./scripts/show_partition_status.sh --dataset silver.features --mode historical --date 2025-01-03 --country THA
```

The shell wrappers should own argument validation and call into `src/runtime/cli.py`.

- [ ] **Step 4: Re-run Tier A Behave**

Run: `./scripts/run_behave_tests_compact.sh --tier a`
Expected: PASS for the new runtime contract scenarios

- [ ] **Step 5: Commit**

```bash
git add src/runtime/cli.py scripts/rebuild_partition_index.sh scripts/show_partition_status.sh features/contracts/parquet_runtime_contract.feature features/steps/parquet_runtime_steps.py
git commit -m "feat: add runtime index and status commands"
```

### Task 6: Pilot the Runtime on Silver Publication

**Files:**
- Modify: `src/make_silver.py`
- Modify: `scripts/make_silver.sh`
- Create: `tests/test_silver_runtime.py`

- [ ] **Step 1: Write a failing test for silver partition publication**

```python
def test_make_silver_publishes_manifested_partition(tmp_path):
    result = materialize_silver_partition(...)
    assert result.manifest.dataset == "silver.features"
```

- [ ] **Step 2: Run the targeted pytest**

Run: `./scripts/run_tests.sh -- tests/test_silver_runtime.py tests/test_runtime_publish.py -q`
Expected: FAIL because silver still writes directly to output directories.

- [ ] **Step 3: Refactor silver writing into a partition-materialization function**

Suggested seam inside `src/make_silver.py`:

```python
def materialize_silver_partition(*, mode: str, run_date: date, countries: list[str], ...):
    frame = build_silver_frame(...)
    return publish_dataframe_partition(dataset="silver.features", dataframe=frame, ...)
```

- [ ] **Step 4: Update the shell wrapper to report published partitions, not just file counts**

The wrapper should still validate fresh artifacts, but it should resolve published manifests rather than raw directory scans.

- [ ] **Step 5: Re-run targeted pytest and Tier A Behave**

Run: `./scripts/run_tests.sh -- tests/test_silver_runtime.py tests/test_runtime_publish.py -q`
Expected: PASS

Run: `./scripts/run_behave_tests_compact.sh --tier a`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/make_silver.py scripts/make_silver.sh tests/test_silver_runtime.py
git commit -m "feat: publish silver partitions through runtime"
```

### Task 7: Switch Predictions to Manifest-Resolved Silver Reads

**Files:**
- Modify: `src/predict_air_quality.py`
- Modify: `scripts/predict_air_quality.sh`
- Modify: `features/regressions/predict_command_realtime.feature`

- [ ] **Step 1: Add a failing regression for missing published silver partitions**

Required behavior:

- prediction fails fast when the requested silver partition is unpublished
- prediction reads the file list from the current silver manifest when published

- [ ] **Step 2: Run Tier A Behave**

Run: `./scripts/run_behave_tests_compact.sh --tier a`
Expected: FAIL because prediction still scans directories directly.

- [ ] **Step 3: Replace directory scanning in prediction with manifest resolution**

```python
manifest = resolve_current_manifest("silver.features", mode=mode, date=target_date, country=country_group)
silver_df = pl.scan_parquet(manifest.files)
```

- [ ] **Step 4: Update the shell wrapper’s preflight checks**

Replace “count parquet files in silver dir” with “verify the required silver partition is published”.

- [ ] **Step 5: Re-run Tier A Behave and targeted pytest**

Run: `./scripts/run_behave_tests_compact.sh --tier a`
Expected: PASS

Run: `./scripts/run_tests.sh -- tests/test_runtime_publish.py tests/test_runtime_index_db.py -q`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/predict_air_quality.py scripts/predict_air_quality.sh features/regressions/predict_command_realtime.feature
git commit -m "feat: read silver partitions from manifests"
```

### Task 8: Add Backfill Planning and Update Docs

**Files:**
- Create: `src/runtime/backfill.py`
- Modify: `docs/DATAFLOW.md`
- Modify: `docs/ARCHITECTURE.md`

- [ ] **Step 1: Write failing tests for missing-partition planning**

```python
def test_plan_backfill_returns_only_unpublished_dates():
    plan = plan_missing_partitions(...)
    assert plan == ["2025-01-02", "2025-01-03"]
```

- [ ] **Step 2: Run the targeted pytest**

Run: `./scripts/run_tests.sh -- tests/test_runtime_backfill.py -q`
Expected: FAIL because backfill planning is not implemented yet.

- [ ] **Step 3: Implement backfill planning against SQLite plus manifest reconciliation**

The planner should:

- expand the requested date range
- query published partitions from SQLite
- reconcile against manifests if the index is stale
- return only missing or invalid partitions

- [ ] **Step 4: Update architecture and dataflow docs**

Document:

- the manifest/current-pointer read model
- SQLite as a rebuildable cache
- silver as the first migrated dataset

- [ ] **Step 5: Re-run targeted pytest and Tier A Behave**

Run: `./scripts/run_tests.sh -- tests/test_runtime_backfill.py -q`
Expected: PASS

Run: `./scripts/run_behave_tests_compact.sh --tier a`
Expected: PASS

- [ ] **Step 6: Run broader regression verification**

Run: `./scripts/run_tests.sh`
Expected: PASS

Run: `./scripts/run_behave_tests_compact.sh --tier a`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add src/runtime/backfill.py docs/DATAFLOW.md docs/ARCHITECTURE.md tests/test_runtime_backfill.py
git commit -m "feat: add backfill planner for runtime"
```

## Execution Notes

- Do not rewrite upstream source processors in this plan.
- Preserve supported entrypoints in `scripts/`.
- Fail fast on invalid mode/flag combinations in every new wrapper.
- Keep SQLite rebuildable from manifest files.
- Validate fresh artifacts from the current run rather than trusting pre-existing files.
- Use the compact Behave harness for routine verification and `./scripts/run_tests.sh` for pytest coverage.
