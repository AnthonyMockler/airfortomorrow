# Decision
Replace ERA5 realtime AWS mirror fixed inter-request sleeps with a shared, adaptive rate-limit control path that uses explicit retry classification (including HTTP 429), exponential backoff with jitter, and bounded retries.

# Why
The current collector inserts a hard-coded 10-second sleep between AWS date requests. In typical 7-day realtime runs this dominates wall time while still being blind to actual server feedback. Existing logs show large fixed-wait cost with low attributable compute overhead, so static delay is the highest-confidence optimization target with minimal contract risk.

# Change Scope
- ERA5 realtime AWS request loop in `src/data_collectors/era5_meteorological_idw.py`.
- Introduce reusable request-with-backoff helper(s) for AWS retrieval path.
- Remove fixed `sleep(10)` pacing between dates.
- Improve retry/error classification for 429/503/transient transport errors.
- Add Behave coverage for no fixed-wait log behavior plus existing contract/output checks.
- Capture before/after timing evidence using the existing ERA5 live benchmark scenario.

# Non-Goals
- No redesign of pipeline-level threading model in `run_complete_pipeline.py`.
- No changes to ERA5 output schema, filenames, or downstream silver/prediction interfaces.
- No broad refactor of historical CDS path beyond contract-preserving safety.
- No tuning of IDW algorithm fidelity or interpolation parameters.
