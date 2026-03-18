# Spatially Partitioned Parquet Pipeline Rebuild Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a new supported Parquet pipeline that treats legacy code as reference only, uses explicit bronze/silver/gold datasets, supports different historical and realtime retrieval adapters, and publishes large partitions safely through manifests plus a rebuildable SQLite index.

**Architecture:** The supported system lives in a new `src/parquet_pipeline/` package and a new public wrapper `scripts/aq_pipeline.sh`. Retrieval-path differences such as realtime APIs versus historical archives are modeled as separate source adapters and bronze dataset IDs, while downstream silver and gold assets share unified schemas. Partitioning is asset-specific: use date-only partitions where transforms need wide spatial context, and introduce a spatial shard key only at stages where partitions are otherwise too large, with the default candidate being `h3_04` but validated by tests before it becomes policy.

**Tech Stack:** Python 3, Polars, PyArrow, Parquet, SQLite, JSON manifests, Behave, pytest, shell wrapper scripts, existing source code used only as migration reference

---

## Scope Guard

This plan supersedes the deleted `parquet-runtime-foundation` plan.

It changes the implementation strategy in four important ways:

- the new supported interface is not constrained by the current wrappers
- the new supported implementation is not constrained by the current `src/` module boundaries
- `gold` becomes an explicit materialized Parquet layer, not an implied outcome of `silver`
- historical and realtime collection paths are first-class adapter differences, not just a `mode` flag

This plan still executes in phases. The framework and CLI land first, then source families migrate one by one into the new runtime until `gold.model_features` and `predictions.pm25` are fully supported.

## File Structure

- Create: `config/parquet_pipeline.yaml`
- Create: `scripts/aq_pipeline.sh`
- Create: `src/parquet_pipeline/__init__.py`
- Create: `src/parquet_pipeline/config.py`
- Create: `src/parquet_pipeline/cli.py`
- Create: `src/parquet_pipeline/assets.py`
- Create: `src/parquet_pipeline/partitions.py`
- Create: `src/parquet_pipeline/layout.py`
- Create: `src/parquet_pipeline/manifests.py`
- Create: `src/parquet_pipeline/index_db.py`
- Create: `src/parquet_pipeline/publish.py`
- Create: `src/parquet_pipeline/read.py`
- Create: `src/parquet_pipeline/validators.py`
- Create: `src/parquet_pipeline/backfill.py`
- Create: `src/parquet_pipeline/adapters/__init__.py`
- Create: `src/parquet_pipeline/adapters/base.py`
- Create: `src/parquet_pipeline/adapters/openaq_api.py`
- Create: `src/parquet_pipeline/adapters/openaq_archive.py`
- Create: `src/parquet_pipeline/adapters/airgradient_realtime.py`
- Create: `src/parquet_pipeline/adapters/airgradient_historical.py`
- Create: `src/parquet_pipeline/adapters/firms_nrt.py`
- Create: `src/parquet_pipeline/adapters/firms_archive.py`
- Create: `src/parquet_pipeline/adapters/himawari_realtime.py`
- Create: `src/parquet_pipeline/adapters/himawari_historical.py`
- Create: `src/parquet_pipeline/adapters/era5_realtime.py`
- Create: `src/parquet_pipeline/adapters/era5_historical.py`
- Create: `src/parquet_pipeline/transforms/__init__.py`
- Create: `src/parquet_pipeline/transforms/air_quality.py`
- Create: `src/parquet_pipeline/transforms/firms.py`
- Create: `src/parquet_pipeline/transforms/himawari.py`
- Create: `src/parquet_pipeline/transforms/era5.py`
- Create: `src/parquet_pipeline/gold/__init__.py`
- Create: `src/parquet_pipeline/gold/build_gold_features.py`
- Create: `src/parquet_pipeline/predict/__init__.py`
- Create: `src/parquet_pipeline/predict/run_predictions.py`
- Create: `tests/test_pipeline_config.py`
- Create: `tests/test_asset_registry.py`
- Create: `tests/test_partition_strategy.py`
- Create: `tests/test_manifest_runtime.py`
- Create: `tests/test_index_db.py`
- Create: `tests/test_backfill.py`
- Create: `tests/test_air_quality_adapters.py`
- Create: `tests/test_firms_transforms.py`
- Create: `tests/test_himawari_transforms.py`
- Create: `tests/test_era5_transforms.py`
- Create: `tests/test_gold_features.py`
- Create: `tests/test_prediction_runtime.py`
- Create: `features/contracts/new_pipeline_cli_contract.feature`
- Create: `features/contracts/gold_layer_contract.feature`
- Create: `features/contracts/source_adapter_contract.feature`
- Create: `features/steps/new_pipeline_steps.py`
- Modify: `docs/DATAFLOW.md`
- Modify: `docs/ARCHITECTURE.md`

## Supported Dataset Taxonomy

The new pipeline should use explicit dataset IDs instead of a global `mode` partition:

- Bronze:
  - `bronze.openaq_api`
  - `bronze.openaq_archive`
  - `bronze.airgradient_realtime`
  - `bronze.airgradient_historical`
  - `bronze.firms_nrt`
  - `bronze.firms_archive`
  - `bronze.himawari_realtime`
  - `bronze.himawari_historical`
  - `bronze.era5_realtime`
  - `bronze.era5_historical`
- Silver:
  - `silver.air_quality_observations`
  - `silver.firms_intensity`
  - `silver.himawari_aod`
  - `silver.era5_weather`
- Gold:
  - `gold.model_features`
- Predictions:
  - `predictions.pm25`

The storage layout should partition by asset-specific keys, not by a universal `mode=` directory.

## Task 1: Freeze the New Public CLI and Contracts

**Files:**
- Create: `features/contracts/new_pipeline_cli_contract.feature`
- Create: `features/contracts/gold_layer_contract.feature`
- Create: `features/contracts/source_adapter_contract.feature`
- Create: `features/steps/new_pipeline_steps.py`

- [ ] **Step 1: Write the failing Behave contracts for the new supported CLI**

Required scenarios:

- `./scripts/aq_pipeline.sh collect openaq-api --date 2026-01-03 --countries THA`
- `./scripts/aq_pipeline.sh collect openaq-archive --start-date 2025-01-01 --end-date 2025-01-03 --countries THA`
- `./scripts/aq_pipeline.sh materialize silver.air_quality_observations --date 2025-01-03 --countries THA`
- `./scripts/aq_pipeline.sh build-gold --date 2025-01-03 --countries THA`
- `./scripts/aq_pipeline.sh predict --date 2025-01-03 --countries THA`
- invalid asset names fail fast
- `gold.model_features` must be a required materialized dataset, not an implicit in-memory frame

- [ ] **Step 2: Add failing step definitions**

```python
@then('the command should report the published dataset id "gold.model_features"')
def step_impl(context):
    raise AssertionError("not implemented")
```

- [ ] **Step 3: Run Tier A Behave**

Run: `./scripts/run_behave_tests_compact.sh --tier a`
Expected: FAIL because the new CLI and contracts do not exist.

- [ ] **Step 4: Commit the red contracts**

```bash
git add features/contracts/new_pipeline_cli_contract.feature features/contracts/gold_layer_contract.feature features/contracts/source_adapter_contract.feature features/steps/new_pipeline_steps.py
git commit -m "test: add new parquet pipeline CLI contracts"
```

## Task 2: Define the New Config, Asset Registry, and Partition Policy

**Files:**
- Create: `config/parquet_pipeline.yaml`
- Create: `src/parquet_pipeline/config.py`
- Create: `src/parquet_pipeline/assets.py`
- Create: `src/parquet_pipeline/partitions.py`
- Create: `tests/test_pipeline_config.py`
- Create: `tests/test_asset_registry.py`
- Create: `tests/test_partition_strategy.py`

- [ ] **Step 1: Write failing tests for the asset registry**

```python
def test_gold_layer_is_explicit_asset():
    registry = load_asset_registry()
    assert registry["gold.model_features"].layer == "gold"


def test_openaq_api_and_archive_are_distinct_bronze_assets():
    registry = load_asset_registry()
    assert registry["bronze.openaq_api"].dataset_id != registry["bronze.openaq_archive"].dataset_id
```

- [ ] **Step 2: Add failing tests for partition policy**

```python
def test_partition_strategy_does_not_use_mode_directory():
    key = build_partition_key("silver.air_quality_observations", date="2025-01-03", spatial_key=None)
    assert "mode=" not in key.storage_path


def test_large_assets_can_opt_into_spatial_sharding():
    strategy = get_partition_strategy("gold.model_features")
    assert strategy.supports_spatial_shard is True
```

- [ ] **Step 3: Run the targeted pytest**

Run: `./scripts/run_tests.sh -- tests/test_pipeline_config.py tests/test_asset_registry.py tests/test_partition_strategy.py -q`
Expected: FAIL because the new config and registry do not exist.

- [ ] **Step 4: Implement the new standalone config and asset registry**

```python
@dataclass(frozen=True)
class AssetDefinition:
    dataset_id: str
    layer: str
    partition_grain: str
    supports_spatial_shard: bool
    upstream_assets: tuple[str, ...]
```

Put the new supported configuration in `config/parquet_pipeline.yaml`, not into the legacy config tree.

- [ ] **Step 5: Implement partition policy as code**

Use per-asset strategies such as:

- date-only partitions for transforms that require broad context
- date plus spatial shard for large post-transform assets
- optional country grouping only when it materially changes performance

The candidate spatial shard should default to `h3_04`, but the code must keep it configurable because the final choice is still open.

- [ ] **Step 6: Re-run the targeted pytest**

Run: `./scripts/run_tests.sh -- tests/test_pipeline_config.py tests/test_asset_registry.py tests/test_partition_strategy.py -q`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add config/parquet_pipeline.yaml src/parquet_pipeline/config.py src/parquet_pipeline/assets.py src/parquet_pipeline/partitions.py tests/test_pipeline_config.py tests/test_asset_registry.py tests/test_partition_strategy.py
git commit -m "feat: add parquet pipeline config and asset registry"
```

## Task 3: Build the New Runtime Layout, Manifest Model, and SQLite Index

**Files:**
- Create: `src/parquet_pipeline/__init__.py`
- Create: `src/parquet_pipeline/layout.py`
- Create: `src/parquet_pipeline/manifests.py`
- Create: `src/parquet_pipeline/index_db.py`
- Create: `src/parquet_pipeline/publish.py`
- Create: `src/parquet_pipeline/read.py`
- Create: `src/parquet_pipeline/validators.py`
- Create: `tests/test_manifest_runtime.py`
- Create: `tests/test_index_db.py`

- [ ] **Step 1: Write failing publish and index tests**

```python
def test_publish_partition_writes_current_pointer(tmp_path):
    result = publish_partition(...)
    assert result.current_manifest_path.exists()


def test_current_pointer_contains_dataset_id_not_mode(tmp_path):
    manifest = read_current_manifest(...)
    assert manifest.dataset_id == "gold.model_features"
    assert "mode" not in manifest.partition_keys


def test_rebuild_index_recovers_partition_state(tmp_path):
    rebuild_index_from_manifests(...)
    assert fetch_partition(...).published_run_id == "run-123"
```

- [ ] **Step 2: Run the targeted pytest**

Run: `./scripts/run_tests.sh -- tests/test_manifest_runtime.py tests/test_index_db.py -q`
Expected: FAIL because the runtime does not exist yet.

- [ ] **Step 3: Implement dataset layout helpers**

```python
def partition_root(dataset_id: str, *, date: str, spatial_shard: str | None = None, country_group: str | None = None) -> Path:
    ...
```

The layout must support:

- immutable run directories
- `manifests/run-<run_id>.json`
- `manifests/current.json`
- published metadata keyed by asset-specific partition fields

- [ ] **Step 4: Implement the manifest schema**

```python
@dataclass(frozen=True)
class PartitionManifest:
    dataset_id: str
    run_id: str
    partition_keys: dict[str, str]
    files: list[str]
    row_count: int
    schema_fingerprint: str
    upstream_manifests: list[str]
```

- [ ] **Step 5: Implement the SQLite index as a rebuildable cache**

Tables should cover:

- published partitions
- runs
- validation results
- upstream lineage edges
- source watermarks

- [ ] **Step 6: Re-run the targeted pytest**

Run: `./scripts/run_tests.sh -- tests/test_manifest_runtime.py tests/test_index_db.py -q`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add src/parquet_pipeline/__init__.py src/parquet_pipeline/layout.py src/parquet_pipeline/manifests.py src/parquet_pipeline/index_db.py src/parquet_pipeline/publish.py src/parquet_pipeline/read.py src/parquet_pipeline/validators.py tests/test_manifest_runtime.py tests/test_index_db.py
git commit -m "feat: add parquet pipeline runtime and index"
```

## Task 4: Add the New CLI and Supported Wrapper

**Files:**
- Create: `scripts/aq_pipeline.sh`
- Create: `src/parquet_pipeline/cli.py`
- Modify: `features/contracts/new_pipeline_cli_contract.feature`
- Modify: `features/steps/new_pipeline_steps.py`

- [ ] **Step 1: Add failing wrapper assertions for help and invalid args**

Required checks:

- unknown subcommand fails clearly
- unsupported asset name fails clearly
- date-range arguments are required for archive adapters
- single-date arguments are required for daily materialization and prediction commands

- [ ] **Step 2: Run Tier A Behave**

Run: `./scripts/run_behave_tests_compact.sh --tier a`
Expected: FAIL because the supported wrapper still does not exist.

- [ ] **Step 3: Implement the wrapper and CLI**

```bash
./scripts/aq_pipeline.sh collect openaq-api --date 2026-01-03 --countries THA
./scripts/aq_pipeline.sh materialize silver.air_quality_observations --date 2025-01-03 --countries THA
./scripts/aq_pipeline.sh build-gold --date 2025-01-03 --countries THA
./scripts/aq_pipeline.sh predict --date 2025-01-03 --countries THA
./scripts/aq_pipeline.sh rebuild-index
./scripts/aq_pipeline.sh status gold.model_features --date 2025-01-03 --countries THA
```

The wrapper remains the supported entrypoint. It should call into `src/parquet_pipeline/cli.py`.

- [ ] **Step 4: Re-run Tier A Behave**

Run: `./scripts/run_behave_tests_compact.sh --tier a`
Expected: the CLI contract scenarios move closer to green, but source commands still fail until adapters are implemented.

- [ ] **Step 5: Commit**

```bash
git add scripts/aq_pipeline.sh src/parquet_pipeline/cli.py features/contracts/new_pipeline_cli_contract.feature features/steps/new_pipeline_steps.py
git commit -m "feat: add supported parquet pipeline CLI"
```

## Task 5: Implement the Air Quality Adapter Pattern and First Silver Asset

**Files:**
- Create: `src/parquet_pipeline/adapters/__init__.py`
- Create: `src/parquet_pipeline/adapters/base.py`
- Create: `src/parquet_pipeline/adapters/openaq_api.py`
- Create: `src/parquet_pipeline/adapters/openaq_archive.py`
- Create: `src/parquet_pipeline/adapters/airgradient_realtime.py`
- Create: `src/parquet_pipeline/adapters/airgradient_historical.py`
- Create: `src/parquet_pipeline/transforms/air_quality.py`
- Create: `tests/test_air_quality_adapters.py`
- Modify: `features/contracts/source_adapter_contract.feature`

- [ ] **Step 1: Write failing tests for retrieval-path divergence**

```python
def test_openaq_api_and_archive_normalize_to_same_schema():
    api_df = collect_openaq_api(...)
    archive_df = collect_openaq_archive(...)
    assert api_df.schema == archive_df.schema


def test_air_quality_transform_consumes_multiple_bronze_assets():
    result = materialize_air_quality_observations(...)
    assert result.dataset_id == "silver.air_quality_observations"
```

- [ ] **Step 2: Run the targeted pytest**

Run: `./scripts/run_tests.sh -- tests/test_air_quality_adapters.py -q`
Expected: FAIL because the new adapters and transform do not exist.

- [ ] **Step 3: Implement the base adapter interface**

```python
class SourceAdapter(Protocol):
    dataset_id: str

    def collect(self, *, date_range: DateRange, countries: list[str]) -> pl.DataFrame:
        ...
```

- [ ] **Step 4: Implement OpenAQ and AirGradient adapters**

Rules:

- realtime and historical code paths remain separate adapters
- both normalize to shared bronze schemas
- legacy modules may be called or copied as reference, but the supported implementation lives here

- [ ] **Step 5: Implement `silver.air_quality_observations`**

The transform should read published bronze manifests, normalize duplicates and outliers, and publish the silver dataset through the new runtime.

- [ ] **Step 6: Re-run targeted pytest and Tier A Behave**

Run: `./scripts/run_tests.sh -- tests/test_air_quality_adapters.py tests/test_manifest_runtime.py -q`
Expected: PASS

Run: `./scripts/run_behave_tests_compact.sh --tier a`
Expected: source-adapter contract scenarios for air quality pass

- [ ] **Step 7: Commit**

```bash
git add src/parquet_pipeline/adapters/__init__.py src/parquet_pipeline/adapters/base.py src/parquet_pipeline/adapters/openaq_api.py src/parquet_pipeline/adapters/openaq_archive.py src/parquet_pipeline/adapters/airgradient_realtime.py src/parquet_pipeline/adapters/airgradient_historical.py src/parquet_pipeline/transforms/air_quality.py tests/test_air_quality_adapters.py features/contracts/source_adapter_contract.feature
git commit -m "feat: add air quality adapters and silver asset"
```

## Task 6: Implement FIRMS, Himawari, and ERA5 Silver Assets With Asset-Specific Partitioning

**Files:**
- Create: `src/parquet_pipeline/adapters/firms_nrt.py`
- Create: `src/parquet_pipeline/adapters/firms_archive.py`
- Create: `src/parquet_pipeline/adapters/himawari_realtime.py`
- Create: `src/parquet_pipeline/adapters/himawari_historical.py`
- Create: `src/parquet_pipeline/adapters/era5_realtime.py`
- Create: `src/parquet_pipeline/adapters/era5_historical.py`
- Create: `src/parquet_pipeline/transforms/firms.py`
- Create: `src/parquet_pipeline/transforms/himawari.py`
- Create: `src/parquet_pipeline/transforms/era5.py`
- Create: `tests/test_firms_transforms.py`
- Create: `tests/test_himawari_transforms.py`
- Create: `tests/test_era5_transforms.py`

- [ ] **Step 1: Write failing tests for source-family transforms**

```python
def test_firms_transform_can_publish_daily_intensity_partition():
    result = materialize_firms_intensity(...)
    assert result.dataset_id == "silver.firms_intensity"


def test_himawari_transform_defers_spatial_sharding_until_after_wide_context_steps():
    plan = get_partition_execution_plan("silver.himawari_aod")
    assert plan.pre_interpolation_spatial_shard is None


def test_era5_transform_can_publish_weather_partition():
    result = materialize_era5_weather(...)
    assert result.dataset_id == "silver.era5_weather"
```

- [ ] **Step 2: Run the targeted pytest**

Run: `./scripts/run_tests.sh -- tests/test_firms_transforms.py tests/test_himawari_transforms.py tests/test_era5_transforms.py -q`
Expected: FAIL because those adapters and transforms do not exist.

- [ ] **Step 3: Implement FIRMS adapters and transform**

Historical and realtime collection paths must remain separate adapters but converge into `silver.firms_intensity`.

- [ ] **Step 4: Implement Himawari adapters and transform**

Do not spatially shard too early. The plan must preserve wide-neighborhood requirements for interpolation steps before the final publish boundary.

- [ ] **Step 5: Implement ERA5 adapters and transform**

Use the same adapter split and publish semantics as the other source families.

- [ ] **Step 6: Re-run the targeted pytest**

Run: `./scripts/run_tests.sh -- tests/test_firms_transforms.py tests/test_himawari_transforms.py tests/test_era5_transforms.py -q`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add src/parquet_pipeline/adapters/firms_nrt.py src/parquet_pipeline/adapters/firms_archive.py src/parquet_pipeline/adapters/himawari_realtime.py src/parquet_pipeline/adapters/himawari_historical.py src/parquet_pipeline/adapters/era5_realtime.py src/parquet_pipeline/adapters/era5_historical.py src/parquet_pipeline/transforms/firms.py src/parquet_pipeline/transforms/himawari.py src/parquet_pipeline/transforms/era5.py tests/test_firms_transforms.py tests/test_himawari_transforms.py tests/test_era5_transforms.py
git commit -m "feat: add source family adapters and silver transforms"
```

## Task 7: Materialize the Explicit Gold Layer

**Files:**
- Create: `src/parquet_pipeline/gold/__init__.py`
- Create: `src/parquet_pipeline/gold/build_gold_features.py`
- Create: `tests/test_gold_features.py`
- Modify: `features/contracts/gold_layer_contract.feature`

- [ ] **Step 1: Write failing tests for `gold.model_features`**

```python
def test_gold_builder_reads_all_required_silver_assets():
    manifest = build_gold_model_features(...)
    assert manifest.dataset_id == "gold.model_features"


def test_gold_builder_can_use_spatial_sharding():
    strategy = get_partition_strategy("gold.model_features")
    assert strategy.supports_spatial_shard is True
```

- [ ] **Step 2: Run the targeted pytest**

Run: `./scripts/run_tests.sh -- tests/test_gold_features.py -q`
Expected: FAIL because the gold builder does not exist.

- [ ] **Step 3: Implement explicit gold materialization**

```python
def build_gold_model_features(*, date: date, countries: list[str], spatial_shard: str | None = None) -> PartitionManifest:
    ...
```

Rules:

- read published silver manifests, not raw directories
- emit a materialized Parquet dataset
- include only model-ready columns and lineage metadata

- [ ] **Step 4: Re-run targeted pytest and Tier A Behave**

Run: `./scripts/run_tests.sh -- tests/test_gold_features.py -q`
Expected: PASS

Run: `./scripts/run_behave_tests_compact.sh --tier a`
Expected: the gold-layer contract passes

- [ ] **Step 5: Commit**

```bash
git add src/parquet_pipeline/gold/__init__.py src/parquet_pipeline/gold/build_gold_features.py tests/test_gold_features.py features/contracts/gold_layer_contract.feature
git commit -m "feat: add explicit gold model features layer"
```

## Task 8: Read Predictions From Gold and Add Backfill Planning

**Files:**
- Create: `src/parquet_pipeline/predict/__init__.py`
- Create: `src/parquet_pipeline/predict/run_predictions.py`
- Create: `src/parquet_pipeline/backfill.py`
- Create: `tests/test_prediction_runtime.py`
- Create: `tests/test_backfill.py`
- Modify: `features/contracts/new_pipeline_cli_contract.feature`

- [ ] **Step 1: Write failing prediction and backfill tests**

```python
def test_prediction_requires_published_gold_partition():
    with pytest.raises(MissingPartitionError):
        run_predictions(...)


def test_backfill_planner_expands_dates_and_skips_published_partitions():
    plan = plan_backfill(...)
    assert plan.missing_dates == ["2025-01-02", "2025-01-03"]
```

- [ ] **Step 2: Run the targeted pytest**

Run: `./scripts/run_tests.sh -- tests/test_prediction_runtime.py tests/test_backfill.py -q`
Expected: FAIL because prediction and backfill modules do not exist.

- [ ] **Step 3: Implement prediction reads from `gold.model_features`**

```python
manifest = resolve_current_manifest("gold.model_features", date="2025-01-03", spatial_shard=None, country_group="THA")
gold_df = pl.scan_parquet(manifest.files)
```

- [ ] **Step 4: Implement backfill planning**

The planner should:

- understand adapter-specific historical collection paths
- expand date ranges
- inspect published manifests
- consult SQLite watermarks
- emit only missing or invalid work items

- [ ] **Step 5: Re-run targeted pytest and Tier A Behave**

Run: `./scripts/run_tests.sh -- tests/test_prediction_runtime.py tests/test_backfill.py -q`
Expected: PASS

Run: `./scripts/run_behave_tests_compact.sh --tier a`
Expected: all new pipeline contract scenarios pass

- [ ] **Step 6: Commit**

```bash
git add src/parquet_pipeline/predict/__init__.py src/parquet_pipeline/predict/run_predictions.py src/parquet_pipeline/backfill.py tests/test_prediction_runtime.py tests/test_backfill.py features/contracts/new_pipeline_cli_contract.feature
git commit -m "feat: add predictions and backfill planning to parquet pipeline"
```

## Task 9: Document the New Supported Architecture and Verify It End to End

**Files:**
- Modify: `docs/DATAFLOW.md`
- Modify: `docs/ARCHITECTURE.md`

- [ ] **Step 1: Update architecture docs**

Document:

- the new supported wrapper `scripts/aq_pipeline.sh`
- explicit bronze, silver, gold, and prediction datasets
- adapter-specific historical and realtime collection paths
- asset-specific partition strategies and the configurable spatial shard
- legacy code as migration reference only

- [ ] **Step 2: Run unit and contract verification**

Run: `./scripts/run_tests.sh`
Expected: PASS

Run: `./scripts/run_behave_tests_compact.sh --tier a`
Expected: PASS

- [ ] **Step 3: Run one bounded end-to-end historical smoke**

Run: `./scripts/aq_pipeline.sh collect openaq-archive --start-date 2025-01-01 --end-date 2025-01-03 --countries THA`
Expected: PASS

Run: `./scripts/aq_pipeline.sh materialize silver.air_quality_observations --date 2025-01-03 --countries THA`
Expected: PASS

Run: `./scripts/aq_pipeline.sh build-gold --date 2025-01-03 --countries THA`
Expected: PASS

Run: `./scripts/aq_pipeline.sh predict --date 2025-01-03 --countries THA`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add docs/DATAFLOW.md docs/ARCHITECTURE.md
git commit -m "docs: document the new parquet pipeline architecture"
```

## Execution Notes

- Do not route new work through the legacy `run_complete_pipeline` path.
- Do not use `mode` as a storage partition key in the new runtime.
- Use separate bronze dataset IDs when historical and realtime retrieval paths differ.
- Keep the spatial shard configurable until dataset-size evidence locks it down.
- Do not spatially shard intermediate transforms before neighborhood-dependent steps finish.
- `gold.model_features` is a required persisted dataset, not an implementation detail.
- The legacy wrappers and modules may be used for reference, comparison, and extraction, but the supported implementation lives only under `src/parquet_pipeline/` and `scripts/aq_pipeline.sh`.
