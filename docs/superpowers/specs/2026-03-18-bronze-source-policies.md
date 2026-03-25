# Bronze Source Policies

- Status: Reference detail for slice 1 and later phases
- Date: 2026-03-18
- Scope: Capture source-family bronze decisions without crowding the core architecture spec.

## Himawari

- Treat existing NetCDF bronze as likely salvageable.
- Validate files for truncation or corruption.
- Relocate them into a cleaner bronze layout.
- Preserve the files themselves byte-for-byte.
- Allow a disposable parse cache later if raw decode cost is too high.

## ERA5

- Do not trust `earthkit_cache` as bronze yet.
- Investigate what those files actually are before deciding the bronze artifact.
- Do not build the architecture around assumptions about the current cache.
- Exclude ERA5 from the first implemented slice until the bronze artifact is defined clearly.

## OpenAQ And AirGradient

- Do not adopt the current so-called raw datasets as bronze.
- Redownload bronze into the new layout.
- For OpenAQ historical, use `location_id × month` bronze fetch jobs and preserve the original archive `csv.gz` objects.
- For OpenAQ realtime, use `date` bronze fetch jobs that can fan out across sensors internally and publish one daily `jsonl.gz` bundle.
- Defer finer-grained `sensor_id × date` jobs and coarser multi-day realtime windows unless the day-level rule proves wrong in practice.
- For live API collection, bronze should be daily `jsonl.gz` bundles that preserve source records as fetched.
- Bronze may be partial for these sources.
- Silver should still build from available bronze by default.

## FIRMS

- Keep source-native CSV or archive artifacts in bronze where practical.
- For FIRMS historical, preserve source files as-is and treat each source file as a bronze artifact.
- For FIRMS realtime, use one fetch job per poll of the South East Asia feed set and record each downloaded satellite CSV as its own bronze artifact.
- Allow `empty_complete` style publication when the source was checked successfully and there were simply no detections.
