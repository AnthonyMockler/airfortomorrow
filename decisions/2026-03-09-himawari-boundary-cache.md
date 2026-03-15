# Decision: Himawari Boundary Cache

## Date

2026-03-09

## Decision

Cache raw geoBoundaries country GeoJSON files locally and load them from disk on subsequent runs instead of refetching them from GitHub every time `create_country_boundaries(...)` is called.

The buffer and merge operations will remain unchanged so the boundary semantics that feed Himawari masking stay aligned with the previous implementation.

## Why

- The representative single-file Himawari H3 profile showed boundary creation is the next-largest timed section after download.
- The current implementation always performs network fetches from GitHub even when the same country boundary is requested repeatedly.
- Caching the raw country geometry is lower risk than caching a pre-buffered merged polygon because it preserves the existing buffer and union codepath exactly.

## Change Scope

- Add raw boundary file caching in `src/utils/boundary_utils.py`.
- Reuse the existing single-file Himawari profiling contract as the regression and timing check.
- Record before/after timing evidence in the working plans.

## Non-Goals

- Do not change the buffer algorithm.
- Do not cache the buffered merged polygon in this slice.
- Do not change Himawari H3 processing logic outside of consuming the existing boundary utility.
