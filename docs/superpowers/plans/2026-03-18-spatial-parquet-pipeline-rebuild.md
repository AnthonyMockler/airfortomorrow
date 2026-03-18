# Parquet Pipeline Rebuild

- Status: Planned; simplified v1 revision
- Owner: Codex + Anthony
- Last Updated: 2026-03-18

## Goal

Replace the current brittle workflow with a simpler Python-first pipeline that:

- preserves bronze as raw recovery data
- rebuilds silver cleanly from bronze
- materializes gold explicitly
- keeps the runtime understandable on one machine

## V1 Principles

This plan intentionally favors:

- one small supported CLI
- one small runtime package
- one SQLite file for convenience, not a heavy control plane
- one manifest per published partition
- explicit batch commands
- local multiprocessing
- source-by-source migration instead of a big-bang rewrite

## V1 Non-Goals

Do not build these in the first slice:

- a general orchestrator
- an always-on queue or scheduler
- a deep adapter class hierarchy
- multiple manifest object types
- rich operational sidecars
- automatic downstream rebuilds when bronze changes
- a broad rewrite of every source before one end-to-end path works

## Target V1 Surface

The first supported surface should stay very small:

- `./scripts/aq_pipeline.sh collect ...`
- `./scripts/aq_pipeline.sh materialize ...`
- `./scripts/aq_pipeline.sh build-gold ...`
- `./scripts/aq_pipeline.sh predict ...`

`backfill` and `status` can be added later as convenience commands after the first slice is working end to end.

The implementation should live in a small new package, likely `src/parquet_pipeline/`, but the package should stay shallow.

## Data Rules To Preserve

The plan must keep these architecture decisions:

- bronze is canonical
- silver is rebuildable
- gold is explicit
- predictions read from gold
- file/archive bronze remains source-native
- live API bronze is daily `jsonl.gz`
- OpenAQ and AirGradient bronze may be partial
- silver/gold/predictions build from available upstream data by default
- Himawari bronze should be validated and relocated before adoption
- ERA5 `earthkit_cache` should not be adopted until understood
- cache is allowed only for heavy binary geospatial formats

## Execution Model

V1 should run from explicit job lists, not filesystem scans.

For any command, the runtime should first compute the full todo list and record it in a simple SQLite `jobs` table. A local worker pool should then claim ready jobs, run them, publish the output partition, write the manifest, and mark the job complete.

Job granularity should stay simple:

- bronze collection jobs are source-specific
- silver, gold, and prediction jobs should default to one job per dataset per date

Job rows should stay minimal. Most jobs only need:

- dataset ID
- layer
- status
- retry count
- required upstream dataset-date dependencies
- last error
- timestamps

Bronze fetch jobs are the exception:

- they may use a source-specific `job_key` instead of a single date
- they may publish multiple daily bronze partitions from one fetch
- they should store the list of expected output dates explicitly

Examples:

- `silver.himawari_aod:2025-01-03`
- `silver.era5_weather:2025-01-03`
- `silver.air_quality_observations:2025-01-03`
- `gold.model_features:2025-01-03`

Workers should only claim jobs whose required upstream manifests already exist. Failed jobs should retry a small number of times, then remain failed. Downstream jobs should stay blocked until their upstream requirements succeed. Existing published outputs should be skipped by default unless a rebuild is explicitly requested. A forced rebuild should publish a new run and repoint the current manifest for that date. Bronze fetch retries should skip dates that were already published successfully.

This keeps parallelism explicit without turning the system into a full orchestrator. Heavy spatial processors should stay coarse in v1: the default job is “process this day,” not “process this tile.”

## Phase 1: Minimal Runtime Foundation

Build the smallest useful runtime first.

### Scope

- add one shell wrapper
- add one Python CLI
- add simple config loading
- add partition path helpers
- add one partition manifest format
- add a small SQLite database for run history, status lookup, jobs, and bronze fetch output-date tracking

### Shape

The runtime should work like this:

1. User requests a dataset and date or date range.
2. Code expands that request into the full todo list and stores it in SQLite.
3. Local worker processes claim ready jobs and handle the work in parallel.
4. The partition is validated and published.
5. A manifest is written next to the partition.
6. SQLite records job and run state for convenience.

### Files

- Create: `scripts/aq_pipeline.sh`
- Create: `src/parquet_pipeline/__init__.py`
- Create: `src/parquet_pipeline/cli.py`
- Create: `src/parquet_pipeline/config.py`
- Create: `src/parquet_pipeline/layout.py`
- Create: `src/parquet_pipeline/manifests.py`
- Create: `src/parquet_pipeline/runtime.py`
- Create: `src/parquet_pipeline/status_db.py`

### Tests

- one CLI contract feature for the supported commands
- targeted pytest for config, layout, manifest, and SQLite behavior

### Notes

Keep the manifest simple. For bronze, artifact entries should be inline inside the partition manifest rather than split into separate per-artifact manifest files.

Keep bronze fetch rules explicit in config for v1. The planner should not invent adaptive fetch windows at runtime.

## Phase 2: Bronze Migration and Collection

Handle bronze source-by-source, conservatively.

### Himawari

- inventory existing NetCDF files
- validate completeness/integrity
- relocate to the new bronze layout
- publish bronze manifests against the relocated files

### OpenAQ and AirGradient

- do not adopt current raw directories
- recollect bronze into the new layout
- configure OpenAQ historical with `location_id × month` fetch jobs over the archive `csv.gz` objects
- configure OpenAQ realtime with `date` fetch jobs that may fan out across sensors internally
- note but defer `sensor_id × date` and multi-day OpenAQ realtime fetch strategies unless day-level fetches prove inadequate
- store live API bronze as daily `jsonl.gz`
- preserve raw records without deduplication

### ERA5

- inspect the current `earthkit_cache`
- decide what the real bronze artifact should be
- do not adopt legacy cache blindly
- keep ERA5 out of the first implementation slice until that decision is made

### FIRMS

- define the bronze layout around source-native files
- preserve historical source files as-is
- collect realtime bronze with one fetch job per poll of the full feed set, recording one artifact per downloaded satellite CSV
- allow no-detection days to publish cleanly

## Phase 3: First End-to-End Vertical Slice

Prove the architecture with one full path before expanding.

### First Slice

The first end-to-end path should be:

1. OpenAQ bronze
2. AirGradient bronze
3. `silver.air_quality_observations`
4. `gold.model_features`
5. `predictions.pm25`

### Why This First

This slice proves the important workflow boundaries:

- bronze is raw and separate
- silver owns cleanup and deduplication
- gold is explicit
- predictions consume gold
- partial upstream coverage flows through the pipeline without blocking

### Tests

- CLI contract for collect/materialize/build-gold/predict
- pytest around bronze ingestion, silver materialization, and gold/prediction reads

## Phase 4: Remaining Silver Assets

Add the other source families one at a time.

### FIRMS

- build `silver.firms_intensity`
- support empty-but-valid source days

### Himawari

- build `silver.himawari_aod`
- keep wide-context transforms intact before any spatial sharding
- add a disposable cache only if raw parse cost demands it

### ERA5

- define the true bronze artifact first
- then build `silver.era5_weather`

## Phase 5: Spatial Sharding Only Where Needed

For V1, published partitions should use `date` only.

- do not partition by country
- do not add spatial shard keys to bronze, silver, or gold
- keep H3 or other spatial IDs as columns

## Suggested File Layout

Keep the package shallow enough that a beginner can read it.

An acceptable v1 shape is:

- `src/parquet_pipeline/cli.py`
- `src/parquet_pipeline/config.py`
- `src/parquet_pipeline/layout.py`
- `src/parquet_pipeline/manifests.py`
- `src/parquet_pipeline/runtime.py`
- `src/parquet_pipeline/status_db.py`
- `src/parquet_pipeline/bronze/`
- `src/parquet_pipeline/silver/`
- `src/parquet_pipeline/gold/`
- `src/parquet_pipeline/predict/`

Only split these further when the modules become hard to understand.

## Verification

Before calling V1 real, verify:

- the CLI can collect, materialize, build gold, and predict for a small date range
- Himawari adoption works on a representative sample
- OpenAQ and AirGradient bronze are clearly raw and separate from silver
- silver can be deleted and rebuilt from bronze
- gold can be deleted and rebuilt from silver
- predictions read gold, not silver
- the runtime works on one machine without extra services

## Deferred Until Later

If V1 works, later improvements can include:

- richer operator-facing coverage summaries
- more formal backfill bookkeeping
- stronger partition versioning
- more detailed lineage storage
- a heavier table format if Parquet plus manifests stops being enough

Those are later upgrades, not part of the first build.
