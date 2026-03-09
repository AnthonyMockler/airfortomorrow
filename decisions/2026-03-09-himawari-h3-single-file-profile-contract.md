# Decision: Himawari H3 Single-File Profiling Contract

## Date

2026-03-09

## Decision

Add a narrow Docker-runnable pytest contract for one representative Himawari NetCDF file that:

- downloads exactly one known historical raw file from JAXA FTP,
- runs it through the shared streaming H3 processor,
- captures per-step timing for the major processing stages,
- and compares the generated H3 parquet against a checked-in reference artifact.

The profiling contract will target the shared streaming processor directly rather than the full integrated pipeline.

## Why

- The full historical Himawari workflow is too slow and too broad for iterative H3 optimization.
- We already know the downloader is no longer the dominant cost in the integrated run.
- The H3 indexing path is shared between historical and realtime in cache-based mode, so a single-file contract exercises the code we actually want to optimize.
- A checked-in representative-output artifact gives us a semantic guardrail while we refactor performance-sensitive code.

## Change Scope

- Add focused plan and verification record for the single-file profiling slice.
- Add targeted pytest coverage and helper utilities for one representative Himawari raw file.
- Add a checked-in expected-output artifact and metadata describing the chosen source file.
- Add lightweight timing instrumentation around the major streaming H3 substeps.

## Non-Goals

- Do not optimize the H3 pipeline in this slice.
- Do not add end-to-end Behave coverage for this micro-benchmark.
- Do not benchmark or compare `raster_to_dataframe(...)` internals beyond timing it as a single stage.
