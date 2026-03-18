# Parquet Lake Architecture Design

- Status: Approved for planning
- Date: 2026-03-18
- Scope: Replace the current brittle script orchestration with a simpler, more robust, Parquet-native architecture that still runs comfortably on a single machine.

## Goal

Keep the operational model simple enough to run on one large server or a desktop, while making the data lake resilient to partial failures, reruns, and large historical backfills.

## Constraints From Discussion

- Prefer the operational simplicity of Python scripts and local execution.
- Avoid proprietary platforms and hosted orchestration lock-in.
- Keep data in Parquet files.
- Engineer for high parallelism and robust recovery from failures.
- Support both local disk and S3-compatible object storage.
- Batch operation is acceptable; true streaming is not required.
- Initial migration must support a one-time historical backfill of roughly four years.
- If a metadata store exists, keep it very small and rebuildable.

## Surveyed Options

### Option A: Pure Python + Parquet + Manifest Files

Keep storage as partitioned Parquet directories and implement publish, lineage, and recovery with Python plus small manifest files.

This is the simplest operational model, but it becomes brittle again if manifest, partition, and recovery rules are not made explicit.

### Option B: Python Assets + Lightweight Orchestrator

Model datasets as assets and let a small orchestrator track partitions, retries, and lineage while compute still lives in Python and storage still lives in Parquet.

This is a strong general-purpose option, but it adds an always-on service and more structure than is justified by the current constraints.

### Option C: Full Lakehouse Stack

Use a formal table layer such as Iceberg or Delta on top of Parquet, with a catalog and stronger snapshot semantics.

This is attractive at larger scale or with many concurrent writers, but it adds complexity and a tooling bias the current project does not need yet.

## Decision

Choose **Option A2**:

- Storage truth lives in Parquet files plus immutable manifest files.
- A small SQLite index tracks runs, partitions, lineage pointers, and watermarks.
- SQLite is explicitly **rebuildable** from storage metadata and is not the source of truth.

This keeps the system easy to run on one server, preserves portability, and avoids re-creating brittle “just scan directories and hope” behavior.

## Proposed Architecture

### 1. Keep the Existing External Shape

Retain the current user-facing wrapper model in [`scripts/`](/Users/anthonymockler/Documents/unicef/airfortomorrow/scripts) and the Python implementation model in [`src/`](/Users/anthonymockler/Documents/unicef/airfortomorrow/src).

The external workflow should still feel like:

1. Collect raw source data
2. Transform source data into cleaned source-specific datasets
3. Build the silver feature dataset
4. Run prediction

The architectural change is in how these steps materialize, publish, discover, and recover dataset partitions.

### 2. Treat Datasets as Partitioned Assets

Even without a separate orchestrator, each dataset should be treated as a partitioned asset with:

- an explicit partition key
- a declared upstream dependency set
- a stable schema contract
- a manifest describing the currently published version of each partition

Example asset groups for this repository:

- `raw.openaq`
- `raw.airgradient`
- `raw.himawari`
- `raw.era5`
- `raw.firms`
- `processed.air_quality`
- `processed.himawari_h3`
- `processed.himawari_daily`
- `processed.himawari_interpolated`
- `processed.era5_daily`
- `processed.firms_h3`
- `silver.features`
- `predictions.pm25`

### 3. Write-Validate-Publish Protocol

Every partition materialization should follow the same protocol:

1. Write outputs to a run-scoped staging location.
2. Validate file presence, schema, and basic row-level sanity checks.
3. Write an immutable manifest for that run.
4. Update the partition’s tiny “current” pointer last.
5. Update the SQLite index from the published manifest.

This makes failures cheap to recover from:

- if a run dies before publish, the partition has not changed
- if validation fails, the bad run is quarantined
- if SQLite is lost, published state can be rebuilt from manifests

### 4. Storage Layout

Keep the current medallion-ish layers but make publication explicit:

- `data/raw/` remains the landing area for raw and minimally normalized source data
- `data/processed/` remains the layer for source-specific cleaned outputs
- `data/silver/` remains the merged feature dataset
- `data/predictions/` remains the prediction layer

Inside each dataset, stop relying on “latest file wins”. Use a partition layout that supports both local disk and object storage:

```text
<dataset-root>/
  mode=<mode>/
    date=<YYYY-MM-DD>/
      country=<ISO3-or-group>/
        manifests/
          run-<run_id>.json
          current.json
        runs/
          run-<run_id>/
            part-000.parquet
            part-001.parquet
```

Notes:

- `current.json` points to the immutable run manifest to read.
- `run-<run_id>.json` contains file list, schema fingerprint, row count, timestamps, upstream input references, and validation status.
- Readers resolve `current.json` instead of scanning `runs/` directly.

### 5. Partitioning Rules

Partition by the axes that matter operationally, not by every analytical dimension.

Recommended defaults:

- Partition by `mode`
- Partition by `date`
- Partition by `country` only when it materially reduces write/read cost
- Keep `h3_08`, `location_id`, and similar high-cardinality identifiers as columns, not partition keys

For large daily partitions, shard within a partition by file count or target size. Aim for moderately large Parquet files rather than millions of tiny files.

### 6. Metadata Index

Introduce a tiny SQLite file, for example under `data/metadata/`, with tables for:

- runs
- dataset partitions
- published manifests
- upstream dependency edges
- watermarks by source and mode
- validation results

SQLite responsibilities:

- make backfill planning cheap
- answer “what is published for 2025-01-03?”
- answer “what failed and needs retry?”
- answer “what upstream partitions fed this silver partition?”

SQLite non-responsibilities:

- it does not own the data
- it does not own the only copy of lineage
- it must be safe to rebuild from storage manifests

### 7. Read Path

Reading should move from file-globbing conventions toward manifest resolution:

- Python readers first resolve published manifests
- then read the Parquet files listed by those manifests
- joins and scans can use PyArrow Datasets, DuckDB, or Polars depending on the workload

This keeps the storage contract stable while allowing the compute engine to vary by workload.

### 8. Parallelism Model

The system should be engineered for parallelism at the partition level:

- different dates can run independently
- different datasets for the same date can run independently when dependencies are satisfied
- validation and publish happen per partition, not only at the end of a giant pipeline

This is the right fit for a single large server:

- use process-level parallelism for partition workers
- keep one logical writer per published partition
- allow many partitions to be materialized at once

### 9. Backfill and Recovery Model

The one-time four-year backfill should use the same mechanics as daily batch runs.

There should not be a separate “historical mode architecture”. Instead:

- the planner expands a date range into partition work items
- workers materialize partitions independently
- failed partitions remain unpublished
- reruns only target missing or invalid partitions

This also improves daily reliability because the routine batch path and the backfill path are the same.

### 10. Local Disk and Object Storage Compatibility

The design should assume a filesystem abstraction rather than hard-coded local paths.

Requirements:

- local disk works for development and simple deployments
- S3-compatible stores work without architectural changes
- publish semantics rely on writing small manifest files, not mutating Parquet files in place

This is intentionally simpler than introducing a full table catalog now.

## Non-Goals

- Do not introduce Kafka or true streaming infrastructure.
- Do not require Spark, a JVM-first lakehouse stack, or a hosted control plane.
- Do not rewrite the entire pipeline in one step.
- Do not partition by H3 cell.

## Why Not Iceberg Now?

Iceberg remains the best likely future upgrade path if the project eventually needs stronger table semantics, more writers, or cleaner schema evolution at scale.

It is not the first move because:

- the project is single-server first
- batch is sufficient
- portability and simplicity are higher priorities than formal lakehouse features
- the team prefers Python scripts over a heavier control plane

The current design deliberately keeps that upgrade path open by using immutable Parquet files plus explicit manifests.

## Staged Migration Strategy

Migrate in slices, not all at once:

1. Add the shared manifest and SQLite runtime.
2. Pilot it on one high-value dataset path.
3. Switch silver publication to manifest-driven reads and writes.
4. Migrate source-specific processed datasets one by one.
5. Retire legacy “latest file wins” scanning once equivalent coverage exists.

## Source Notes

This design was informed by the current repository architecture plus these open-source references:

- Dagster asset and partition concepts: https://docs.dagster.io/guides/build/assets/defining-assets
- Dagster partitioning and backfills: https://docs.dagster.io/guides/build/partitions-and-backfills/partitioning-assets
- Dagster schedules: https://docs.dagster.io/guides/automate/schedules/
- PyArrow datasets: https://arrow.apache.org/docs/python/dataset.html
- DuckDB Parquet support: https://duckdb.org/docs/stable/data/parquet/overview
- Apache Iceberg overview: https://iceberg.apache.org/docs/latest/
- Delta Lake overview: https://delta.io/learn/getting-started/
