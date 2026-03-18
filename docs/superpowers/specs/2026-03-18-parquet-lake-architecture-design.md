# Parquet Lake Architecture Design

- Status: Brainstorming; requirements still being refined
- Date: 2026-03-18
- Scope: Replace the current brittle workflow with a new Parquet-native architecture that is simple to run on one machine, explicit about lineage and parallelism, and conservative about reusing existing data.

## Goal

Build a new supported pipeline that:

- preserves trustworthy bronze data so it only needs to be downloaded once
- keeps bronze, silver, gold, and predictions as distinct layers
- keeps source cleaning and feature engineering clearly separated
- makes parallel execution explicit through planning and worker leasing
- supports both historical backfills and daily batch runs without relying on ad hoc filesystem loops

## Constraints From Discussion

- Prefer a one-server or desktop-friendly operating model.
- Avoid proprietary or hosted workflow platforms.
- Keep data in Parquet where practical for managed layers, but preserve source-native bronze artifacts where they are the true downloaded files.
- Batch is acceptable; true streaming is not required.
- Bronze must remain available as source truth.
- Silver should be considered rebuildable and less trusted than bronze.
- Gold must be an explicit materialized Parquet layer for model-ready features.
- Historical and realtime collection paths may differ by source and must be modeled explicitly.
- `mode` should not be a universal storage partition key.
- Spatial sharding is necessary for some large assets, but must not be introduced before transforms that require wider spatial context.
- Existing bronze should be salvaged where trustworthy; silver can be rebuilt.

## Decisions Locked So Far

- Bronze is the canonical source-truth layer and should stay as close as practical to the downloaded source format.
- Silver is source-specific transformation space and is intentionally rebuildable.
- Gold is an explicit materialized Parquet layer.
- Predictions read from gold, not directly from silver.
- Algorithm variants such as IDW and kriging should eventually become separate published dataset IDs.
- The new supported pipeline does not need to preserve the current wrappers or current Python module boundaries.
- Execution should be planner-driven and worker-leased, not directory-scan-driven.
- Task granularity is source-specific rather than universally file-level or day-level.
- `mode` is not a storage partition key.
- Trustworthy legacy bronze should be adopted conservatively.
- Existing Himawari bronze should be validated, relocated into a new bronze layout, and then adopted.
- Existing OpenAQ and AirGradient so-called raw data should not be adopted as bronze and should be redownloaded.
- Existing ERA5 `earthkit_cache` files are not yet understood and should not be adopted as canonical bronze.
- Regenerable cache is allowed only for heavy binary geospatial sources such as NetCDF, GeoTIFF, and possibly GRIB.
- Regenerable cache is non-canonical, disposable, and must live outside bronze/silver/gold.
- OpenAQ and AirGradient bronze should always publish what was collected rather than failing publication for incomplete coverage.
- Silver should build from whatever bronze is available by default, including partial bronze.
- Gold and predictions should also build by default from available upstream data, even when some upstream bronze or silver inputs are partial.
- Partial upstream coverage should be surfaced through manifest metadata, CLI/log warnings, and a compact dataset-level coverage summary artifact alongside gold and prediction outputs.
- Coverage and quality signals should not be embedded as fields inside gold or prediction parquet outputs by default.
- The sidecar coverage summary should be human-readable and stored next to the dataset output or partition it describes.
- The sidecar coverage summary should be rich enough for operators to understand dataset statuses, counts, and source-specific notes without opening manifests.
- For file- and archive-based bronze sources, preserve source-native downloaded artifacts where practical.
- For live API-based bronze sources, preserve lossless canonical raw-record bundles rather than unstable request/page payload dumps.
- For live API-based bronze sources, the preferred bundle format is gzipped line-delimited JSON (`jsonl.gz` / `ndjson.gz`) kept as close as practical to the source records.
- For live API-based bronze sources, the preferred bundle boundary is one day per source partition.
- For live API-based bronze sources, canonicalization is limited to lossless day-grained bundling; all original source record content must be preserved.
- For live API-based bronze sources, fetch/provenance metadata should live at the bundle or manifest level rather than being wrapped around every record.
- Bronze publication should use hierarchical manifests: one manifest for the published partition plus per-artifact manifest entries for each source file or bronze bundle inside that partition.
- Bronze per-artifact manifest entries should record content checksums by default.
- The default bronze checksum should be a fast non-cryptographic hash rather than a cryptographic hash.
- Live API bronze should preserve duplicate records exactly as fetched; deduplication belongs in silver.
- Day-grained bronze partitions for live API sources may be superseded by newer, fuller published versions for the same day.
- Superseded upstream bronze should not automatically trigger downstream rebuilds.
- The system should not actively surface a stale flag on downstream outputs by default when newer upstream bronze versions exist.

## Surveyed Options

### Option A: Pure Python + Parquet + Manifest Files

Keep storage as partitioned Parquet plus explicit manifests and a small SQLite index.

This remains the preferred operating model because it fits the simplicity constraint, but it only works if manifests, work planning, and lineage are treated as first-class architecture rather than conventions.

### Option B: Python Assets + Lightweight Orchestrator

Add a dedicated orchestrator while keeping compute in Python and storage in Parquet.

This remains a valid fallback if the custom planning and queue semantics become too costly to maintain, but it is not the current preferred direction.

### Option C: Full Lakehouse Stack

Adopt a formal table layer such as Iceberg or Delta on top of Parquet.

This remains a plausible future upgrade path if the number of writers, schema evolution needs, or table-management demands outgrow the simpler design.

## Decision Direction

Continue designing around **Option A2**:

- immutable Parquet datasets plus manifests
- a rebuildable SQLite index for runs, queue state, lineage, and watermarks
- a new supported pipeline surface not constrained by the current wrappers or Python module layout
- legacy code kept only as migration reference or skeletons

This is still a design direction, not a locked implementation spec.

## Proposed Architecture

### 1. New Supported Surface

The new supported pipeline does not need to preserve the current shell wrappers or the current `src/` layout.

It should expose a new, smaller, supported surface that is deliberately designed for:

- explicit collection commands
- explicit materialization commands
- explicit gold-building commands
- explicit prediction commands
- explicit backfill planning, status, and recovery

The existing repository remains useful as a source of reference implementations, source-specific extraction logic, and known contracts, but it is not the architecture boundary for the new system.

### 2. Layer Boundaries

The new architecture should enforce these semantics:

- `bronze` = source truth
- `silver` = source-specific cleaned or transformed datasets
- `gold` = model-ready merged feature tables
- `predictions` = inference outputs

Key rules:

- Bronze is immutable and should be reused whenever it is trustworthy.
- Bronze should remain source-native where the downloaded artifact itself is important for provenance or future reprocessing.
- File and archive sources should preserve source-native artifacts in bronze wherever practical.
- Live API sources should preserve lossless raw-record bundles in bronze, not transport-level request/page dumps.
- The preferred live-API bronze bundle format is `jsonl.gz` / `ndjson.gz`.
- The preferred live-API bronze bundle boundary is one day per source partition.
- Live API bronze bundling must preserve all original source record content and may only add fetch/provenance metadata needed for replay and lineage.
- That fetch/provenance metadata should live at the bundle or manifest level by default, so each record line remains as close as practical to the source record.
- Duplicate records fetched from live APIs should remain in bronze exactly as fetched; cleanup and deduplication begin in silver.
- For live API sources, a day partition may be republished as a newer version when later collection recovers additional records for that same day.
- Downstream silver, gold, and prediction outputs should not be automatically invalidated or rebuilt when a newer upstream bronze version appears for the same partition.
- Lineage should retain the relationship between outputs and the specific upstream versions they used, but stale-vs-newer-upstream status does not need to be surfaced by default.
- Silver is intentionally rebuildable.
- Gold is explicitly materialized; it is not just an in-memory join step hidden inside prediction.
- Predictions read from gold, not directly from silver.

### 3. Dataset Taxonomy

The architecture should use explicit dataset IDs rather than a universal `mode` partition.

Examples of likely bronze dataset IDs:

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

Examples of likely silver dataset IDs:

- `silver.air_quality_observations`
- `silver.firms_intensity`
- `silver.himawari_aod`
- `silver.era5_weather`

Examples of likely gold and prediction dataset IDs:

- `gold.model_features`
- `predictions.pm25`

Algorithm variants such as IDW versus kriging should eventually become separate published dataset IDs when those experiments become active, rather than hidden implementation details under one canonical dataset.

### 4. Planner-Driven Execution Model

Normal execution should be planner-driven, not scan-loop-driven.

The intended model is:

1. A planner starts from a requested target dataset and date range.
2. The planner expands upstream dependencies and creates explicit work items.
3. Collection adapters enumerate exact remote files, objects, or API pages needed for bronze tasks.
4. Work items are written into a durable SQLite-backed queue or run table.
5. Worker processes lease ready tasks, materialize outputs, publish manifests, and mark the work complete.
6. Downstream work becomes runnable only when required upstream manifests exist.

This means the hot path is:

- plan
- lease
- execute
- publish
- unlock dependents

It is **not**:

- loop over directories
- infer state from whatever files happen to exist
- repeatedly rescan until something seems done

Periodic reconciliation scans are still useful for recovery or index rebuilds, but they should not be the main orchestration model.

Task granularity should be source-specific:

- file-level where the source naturally exposes stable files and fine-grained retries are valuable
- day-, chunk-, or page-level where those are the natural source work units

Publish granularity is a separate decision from task granularity. A bronze partition can be published at a coarser boundary than the worker tasks used to produce it.

### 5. Write-Validate-Publish Protocol

Every materialization should follow the same protocol:

1. Write outputs into a run-scoped location.
2. Validate file integrity, schema, and basic content expectations.
3. Write an immutable run manifest.
4. Update the partition’s current pointer last.
5. Update SQLite from the published manifest.

This keeps partial failures contained:

- if a run dies before publish, the partition has not changed
- if validation fails, the bad run is not published
- if SQLite is lost, the published state can be rebuilt from manifests

For bronze, manifests should be hierarchical:

- a partition-level manifest that describes the published bronze partition
- per-artifact manifest entries for each adopted file, downloaded file, or API bronze bundle included in that partition

This supports precise salvage, checksumming, quarantine, and selective retries without forcing downstream consumers to read bronze at artifact granularity.

Per-artifact entries should include checksums by default so that adoption, relocation, validation, and later integrity checks are based on content rather than only path or file size.

The default checksum should optimize for throughput on multi-terabyte bronze inventories. A stronger cryptographic checksum can still be added later for specific migration or audit workflows if needed.

### 6. Storage Layout

The layout should support layer separation, optional spatial sharding, and explicit publish boundaries.

Illustrative pattern:

```text
<dataset-root>/
  date=<YYYY-MM-DD>/
    country_group=<group>/
      spatial_shard=<optional-shard>/
        manifests/
          run-<run_id>.json
          current.json
        runs/
          run-<run_id>/
            part-000.parquet
            part-001.parquet
```

Notes:

- `mode=` should not be a universal directory partition.
- Retrieval-path differences belong in dataset IDs or adapter choice, not in a blanket partition rule.
- `spatial_shard=` is optional and asset-specific.
- `current.json` points to the immutable manifest that readers should resolve.

Any regenerable acceleration cache for heavy binary sources should live outside this canonical managed layout, for example under `data/cache/`, and should never be treated as bronze or silver.

### 7. Partitioning Rules

Partitioning should be asset-specific.

Current working rules:

- Partition by `date` unless a dataset has a better natural grain.
- Add `country_group` only when it materially changes performance or operational isolation.
- Add a spatial shard only when the asset is too large without one.
- Keep high-cardinality identifiers such as `h3_08` and `location_id` as columns, not top-level partition keys.

The leading candidate for a spatial shard is `h3_04`, but that is not locked yet.

Important guardrail:

- do not spatially shard intermediate transforms before neighborhood-dependent steps such as IDW, KDE, or kriging have finished consuming the wider context they need

This means some assets will likely be:

- date-only in bronze
- date-only in early silver
- date plus spatial shard in later silver or gold

### 8. Bronze Adoption Strategy

The migration should salvage existing bronze wherever possible through an **adopt-and-verify** step.

That means:

- inventory legacy files
- classify them into candidate new bronze dataset IDs
- validate them
- publish adoption manifests for the trusted subset
- quarantine or reingest the rest

Current source-by-source direction:

- Himawari:
  - likely adopt existing NetCDF bronze after validating that files are complete and not truncated
  - relocate validated files into the new canonical bronze layout before adoption
- ERA5:
  - do not trust `earthkit_cache` as canonical bronze yet
  - the `.cache` files need investigation before adoption
  - until understood, ERA5 legacy cache should be treated as unknown, not as managed bronze
- OpenAQ and AirGradient:
  - current so-called raw data appears processed already
  - do not adopt it as canonical bronze
  - plan to redownload into new bronze datasets
  - OpenAQ historical should preserve archive-native files where practical
  - OpenAQ realtime and AirGradient should preserve lossless canonical raw-record bundles in `jsonl.gz` form rather than request/page dumps

This keeps the migration conservative:

- salvage trustworthy bronze
- rebuild all silver
- avoid blessing ambiguous or already-processed data as source truth

Bronze adoption should not create a permanent second bronze copy for convenience. The goal is one canonical bronze copy in the new layout, not a duplicated lake.

### 9. Cache Policy

Regenerable cache is allowed only for heavy binary geospatial sources where reparsing is expensive.

Current direction:

- allowed for sources such as Himawari NetCDF, GeoTIFF, and possibly GRIB-based ERA5 artifacts if needed
- not allowed by default for tabular or API-driven sources such as OpenAQ and AirGradient

Cache rules:

- cache is non-canonical
- cache is disposable and safe to delete
- cache must be derivable from bronze plus code/version metadata
- downstream science and modeling code should not treat cache as a managed data layer

### 10. Bronze Readiness Rules

Bronze readiness should be source-specific rather than universal.

Current direction:

- Himawari:
  - strict completeness per day is realistic because the collector can enumerate a concrete set of hourly source files for each day
- ERA5:
  - strict completeness per day and parameter bundle is the likely target, but only after the new bronze artifact is defined
- FIRMS:
  - strict completeness per collection window or feed set is reasonable
  - an `empty_complete` state should be allowed when all expected source checks ran successfully but there were simply no detections
- OpenAQ:
  - always publish what was collected
  - coverage metadata should be recorded on every bronze manifest
- AirGradient:
  - always publish what was collected
  - coverage metadata should be recorded on every bronze manifest

Bronze manifests should eventually support explicit states such as:

- `complete`
- `partial`
- `empty_complete`
- `failed`
- `quarantined`
- `adopted`

For OpenAQ and AirGradient, `partial` should be treated as a normal bronze publication state rather than an error condition.

### 11. Silver Consumption Rule

Silver should consume published bronze by default, including partial bronze.

That means:

- silver does not block waiting for bronze completeness on sources where partial publication is normal
- silver outputs should carry enough lineage and coverage metadata to reveal when upstream bronze was partial
- completeness-sensitive downstream assets may still add stronger validation later, but the default behavior is to build

This is an intentional tradeoff toward availability and forward progress for sensor/API sources.

### 12. Gold and Prediction Consumption Rule

Gold and prediction runs should also proceed by default from available upstream inputs.

That means:

- `gold.model_features` does not block by default when some upstream silver inputs were built from partial bronze
- prediction runs do not block by default when some upstream gold inputs reflect partial upstream coverage
- manifests and lineage need to make partial upstream coverage visible rather than hiding it

This continues the same availability-first design choice used for OpenAQ and AirGradient bronze publication.

### 13. Observability Contract

Partial upstream coverage should be visible by default.

Required surfaces:

- detailed coverage and lineage metadata in manifests
- warnings in CLI and log output when upstream coverage was partial
- a compact dataset-level coverage summary artifact written alongside gold and prediction outputs

The sidecar summary should stay dataset-level and human-readable. It should live next to the output it describes and include:

- upstream dataset names
- readiness states such as `complete`, `partial`, or `empty_complete`
- useful counts such as observed versus expected work where available
- short operator-facing notes
- small source-specific details when they materially help interpretation

Detailed per-partition lineage remains in manifests rather than being duplicated into a large operator-facing report.

Coverage and quality signaling should stay out of the gold and prediction parquet schemas by default. Those datasets should remain focused on analytical/model outputs, while manifests and sidecar summaries carry operational completeness context.

### 14. Backfill and Recovery Model

Backfill and daily operation should share the same runtime mechanics, but not necessarily the same collection adapters.

The key distinction is:

- the runtime model stays the same
- the source adapter chosen for collection may differ between historical and realtime

For example:

- realtime OpenAQ may use an API adapter
- historical OpenAQ may use an archive adapter

The planner should understand those differences explicitly instead of pretending they are the same task with a different flag.

Recovery behavior should be:

- failed work remains unpublished
- reruns target missing or invalid partitions
- the queue can be rebuilt from manifests and desired targets
- stale-index recovery is allowed through reconciliation

### 15. Local Disk and Object Storage Compatibility

The design should assume a filesystem abstraction rather than hard-coded local paths.

Requirements:

- local disk works for development and simple deployments
- S3-compatible stores work without architectural changes
- publish semantics rely on manifests and immutable runs, not in-place mutation

### 16. Open Questions

These requirements are still being locked down:

- Which assets should first opt into spatial sharding?
- Is `h3_04` the correct first spatial shard, or should another intermediate grain be used?
- What exactly are the ERA5 `earthkit_cache` files, and can any of them be adopted safely?
- When should algorithm variants become first-class published datasets in practice, versus remaining a later concern?
- What coverage metadata should be required on OpenAQ and AirGradient bronze and propagated into silver?

## Non-Goals

- Do not introduce streaming infrastructure.
- Do not force Spark or a JVM-first lakehouse stack.
- Do not trust ambiguous legacy “raw” data just because it already exists.
- Do not collapse bronze, silver, and gold into one generic “Parquet lake” concept.

## Staged Migration Direction

The current migration direction should be:

1. Lock the requirements and clean architecture spec.
2. Investigate legacy bronze salvageability by source.
3. Design the planner, queue, and manifest runtime.
4. Decide where spatial sharding starts for each asset family.
5. Build the new supported surface.
6. Adopt trustworthy bronze and redownload untrustworthy bronze.
7. Rebuild silver and gold from managed bronze.

## Source Notes

This design direction was informed by the current repository architecture plus these open-source references:

- Dagster asset and partition concepts: https://docs.dagster.io/guides/build/assets/defining-assets
- Dagster partitioning and backfills: https://docs.dagster.io/guides/build/partitions-and-backfills/partitioning-assets
- PyArrow datasets: https://arrow.apache.org/docs/python/dataset.html
- DuckDB Parquet support: https://duckdb.org/docs/stable/data/parquet/overview
- Apache Iceberg overview: https://iceberg.apache.org/docs/latest/
- Delta Lake overview: https://delta.io/learn/getting-started/
