# Decision: Himawari H3 In-Memory Raster Path

## Date

2026-03-09

## Decision

Replace the temporary on-disk GeoTIFF step in the shared Himawari streaming H3 processor with an in-memory raster dataset that preserves the existing rasterio masking semantics.

The optimization target is the per-file NetCDF-to-raster staging step identified by the single-file profiling contract. The output contract will continue to be enforced by the representative-file artifact test.

## Why

- The single-file profile showed `netcdf_to_tif` is the dominant repeatable cost inside the shared H3 loop.
- The current implementation writes a GeoTIFF to disk, reopens it, reads it back, then deletes it.
- Preserving rasterio-based masking while removing disk I/O is lower risk than reimplementing crop/mask logic from scratch.
- The representative-file artifact test already gives us a strong correctness guardrail against semantic drift.

## Change Scope

- Refactor the per-file streaming path in `src/data_processors/process_himawari_h3_streaming.py`.
- Keep the output schema and values stable.
- Reuse the existing single-file profiling contract as the main regression and timing check.

## Non-Goals

- Do not change `raster_to_dataframe(...)` behavior.
- Do not redesign the overall H3 pipeline or add multi-file parallelism in this slice.
- Do not optimize boundary loading in this slice.
