# Decision: Static Boundary Assets

## Date

2026-03-09

## Decision

Add Thailand and Laos ADM0 GeoJSON boundary files as checked-in static assets under `assets/boundaries/`, tracked via Git LFS, and update the boundary loader to prefer those assets before using the local cache or downloading from geoBoundaries.

## Why

- Thailand and Laos are the default geographic scope for the project and are used repeatedly across collectors and processors.
- Checked-in static boundary assets reduce dependency on runtime network access for the most common paths.
- Preferring static assets over cache/download keeps local and CI behavior more deterministic.
- The existing representative-file Himawari contract already gives us a strong correctness guardrail for one real consumer of these boundaries.

## Change Scope

- Add `THA` and `LAO` ADM0 GeoJSON files under `assets/boundaries/`.
- Track those files with Git LFS.
- Update `src/utils/boundary_utils.py` to resolve boundaries in this order:
  1. checked-in static asset
  2. local cache
  3. remote download
- Add targeted unit coverage for the static-asset preference.

## Non-Goals

- Do not add every country boundary as a checked-in asset.
- Do not remove the cache/download fallback.
- Do not change the buffer or merge semantics.
