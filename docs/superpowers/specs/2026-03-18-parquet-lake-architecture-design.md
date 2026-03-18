# Parquet Lake Architecture Design

- Status: Brainstorming; simplified v1 revision
- Date: 2026-03-18
- Scope: Replace the current brittle workflow with a simpler Python-first pipeline that preserves raw data, keeps bronze/silver/gold boundaries clear, and remains easy to run on one machine.

## Goal

Build a new supported pipeline that:

- preserves raw bronze data so it only needs to be downloaded once
- keeps bronze, silver, gold, and predictions as distinct layers
- makes it easy to swap silver algorithms later without touching bronze
- runs well on one server or even a desktop
- stays simple enough for a relative beginner to understand

## What We Are Optimizing For

This design is intentionally biased toward:

- low operational complexity
- explicit data boundaries
- simple Python code and shell entrypoints
- strong parallelism on one machine
- safe rebuilds from bronze

This design is intentionally **not** trying to become a general-purpose data platform.

## Core Invariants

These are the rules that matter most:

- `bronze` is the canonical recovery layer.
- `silver` is source-specific transform space and is rebuildable.
- `gold` is an explicit materialized feature layer.
- `predictions` read from gold.
- Bronze should stay as close as practical to the source artifact.
- Parallelism should come from explicit work lists and local worker pools, not from ad hoc filesystem loops.
- We should prefer a few simple concepts over a large number of flexible ones.

## Simple V1 Architecture

### 1. Supported Surface

V1 should expose one small supported surface:

- one shell entrypoint
- one Python CLI
- one config file
- one small runtime package

The existing codebase remains useful as reference and migration material, but V1 does not need to preserve the current wrappers or current `src/` boundaries.

### 2. Layer Boundaries

The medallion layers should mean exactly this:

- `bronze` = source truth
- `silver` = source-specific cleaned or transformed data
- `gold` = model-ready feature tables
- `predictions` = inference outputs

Important rules:

- Bronze is never used as a place to hide cleaning logic.
- Silver is where deduplication, outlier handling, interpolation, KDE, IDW, kriging, and similar logic belong.
- Gold is where source-specific silver datasets are merged into model features.
- If we want to compare algorithm variants later, they should become separate published silver dataset IDs rather than mutating one hidden implementation.

### 3. Storage Rules

Managed analytical layers should be Parquet.

Bronze should follow source family rules:

- file and archive sources should preserve source-native files
- live API sources should preserve lossless day-grained `jsonl.gz` raw-record bundles

Bronze should stay as close to the downloaded source as practical:

- no deduplication in bronze
- no cleanup in bronze
- no repacking of file-based bronze into new synthetic bundles
- no pretending that processed parquet is raw data

The only exception is live APIs, where there is no stable source file to preserve. In that case, bronze should store a lossless daily record bundle that keeps the original source record content.

### 4. Runtime Shape

V1 should be a simple command-driven batch runtime:

1. User requests a date or date range for a dataset.
2. The command writes the full todo list up front into a simple SQLite `jobs` table.
3. A local worker pool claims ready jobs and processes them in parallel.
4. Outputs are validated and written to the target layer.
5. A manifest is written for the published partition.
6. A small SQLite database records run history and convenience indexes.

This is deliberately simpler than a full planner/orchestrator:

- no always-on services
- no general asset scheduler
- no long-lived leased-worker system
- no heavy control plane

SQLite is a convenience index and run log, not the heart of the architecture.

Jobs should stay minimal. A job row only needs:

- dataset ID
- date
- layer
- status
- retry count
- required upstream dataset-date dependencies
- last error
- timestamps

The runtime should precompute the whole todo list at the start of a command. Workers should only claim jobs whose required upstream manifests already exist. Existing published outputs should be skipped by default unless a rebuild is explicitly requested. Forced rebuilds should publish a new run and repoint the current manifest for that date.

### 5. Manifest Model

V1 should use **one manifest per published partition**.

That manifest should be simple and readable. It should inline the important metadata instead of splitting it across multiple manifest types.

At minimum, each partition manifest should record:

- dataset ID
- partition keys
- publish time
- files written
- upstream inputs used
- coverage/readiness summary
- artifact list for bronze partitions, including path, size, and checksum

This keeps the integrity benefits we want without inventing a heavier manifest hierarchy for v1.

### 6. Parallelism Model

Parallelism should be explicit, but simple.

The pattern should be:

- build a list of work items
- process them with a local worker pool
- collect results
- publish the partition

Task granularity should stay source-specific:

- Himawari may use file-level work internally
- API sources may use day-level or chunk-level work internally
- downstream publish boundaries can still be date-level

The important thing is to avoid implicit “scan directories until things seem done” behavior.

### 7. SQLite Role

SQLite is acceptable, but only in a narrow role:

- run history
- simple status queries
- minimal job queue state for backfills and batch runs
- lightweight lookup index for published partitions

If SQLite disappeared, the system should still be understandable and recoverable from storage plus manifests.

## Source Policies

### Himawari

- Treat existing NetCDF bronze as likely salvageable.
- Validate files for truncation/corruption.
- Relocate them into a cleaner bronze layout.
- Preserve the files themselves byte-for-byte.
- Allow a disposable parse cache later if raw decode cost is too high.

### ERA5

- Do not trust `earthkit_cache` as bronze yet.
- Investigate what those files actually are before deciding the bronze artifact.
- Do not build the architecture around assumptions about the current cache.

### OpenAQ and AirGradient

- Do not adopt the current so-called raw datasets as bronze.
- Redownload bronze into the new layout.
- For live API collection, bronze should be daily `jsonl.gz` bundles that preserve source records as fetched.
- Bronze may be partial for these sources.
- Silver should still build from available bronze by default.

### FIRMS

- Keep source-native CSV or archive artifacts in bronze where practical.
- Allow `empty_complete` style publication when the source was checked successfully and there were simply no detections.

## Partitioning Rules

V1 should partition published datasets by `date` only.

For V1:

- do not partition by country
- do not add spatial shard keys to bronze, silver, or gold
- keep spatial IDs such as H3 cells as columns, not partition keys

## Bronze Adoption and Migration

Migration should be conservative.

The correct default is:

- salvage trustworthy bronze
- redownload untrustworthy bronze
- rebuild silver from managed bronze

Current working policy:

- Himawari: validate, relocate, adopt
- ERA5: investigate first
- OpenAQ: redownload
- AirGradient: redownload

Bronze relocation may change directory layout, but it should not change file contents or file granularity.

## Coverage and Partial Data

The system should prefer availability over strict blocking for sensor/API sources.

That means:

- OpenAQ and AirGradient bronze can publish partial coverage
- silver can build from available bronze by default
- gold can build from available silver by default
- predictions can run from available gold by default

For V1, coverage should be surfaced in:

- partition manifests
- simple CLI/log warnings

Richer operator sidecars can be added later if they prove necessary, but they do not need to be part of the first slice.

## Cache Policy

Regenerable cache is allowed only for heavy binary geospatial formats where raw parsing is expensive, such as:

- NetCDF
- GeoTIFF
- possibly GRIB

Cache rules:

- cache is not bronze
- cache is not silver
- cache is disposable
- cache must be derivable from bronze

API and tabular sources should not get a cache layer by default.

## What V1 Should Not Build

To keep the system understandable, V1 should explicitly avoid:

- a general-purpose orchestrator
- an always-on queue service
- a large adapter class hierarchy before we need it
- a complicated manifest taxonomy
- a heavy metadata catalog
- rich operational dashboards
- automatic downstream rebuilds when upstream bronze changes
- a full table-format layer such as Iceberg or Delta

If we need more sophistication later, we should add it only after the simple version proves inadequate.

## Future Upgrade Path

If V1 succeeds but later becomes too limited, the most likely upgrades are:

1. Better partition versioning and richer manifests
2. More sophisticated backfill bookkeeping in SQLite
3. Stronger spatial sharding policies for large silver/gold assets
4. Optional richer operator summaries
5. A table format such as Iceberg, if the custom Parquet layout becomes the real bottleneck

Those are later moves, not starting assumptions.

## Recommended V1 Direction

The simplest defensible design is:

- source-native bronze
- Parquet silver and gold
- one small CLI
- one small runtime package
- explicit date-based commands
- local multiprocessing for parallel work
- one manifest per published partition
- one SQLite file for convenience and run history

That gives us the benefits we actually care about without turning the repository into a custom data platform.
