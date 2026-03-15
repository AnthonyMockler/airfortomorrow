# Decision: OpenAQ Historical Sample Contract

## Date

2026-03-09

## Decision

Add a focused historical OpenAQ collector contract around `scripts/collect_openaq_historical.sh` using a small bounded location sample, instead of relying on the full Air Quality historical pipeline for every iteration.

The bounded contract will be enabled by a new location-cap option in the historical collector path, and it will validate real S3-backed historical parquet output for one country and one year.

## Why

- OpenAQ historical is currently the slowest remaining historical path.
- The existing historical Air Quality contract is too broad for iterative OpenAQ optimization because it also runs AirGradient and downstream processing.
- We need a narrower live loop that still uses real historical data and the real historical entrypoint.
- A location cap is a lower-risk way to bound the historical collector than inventing synthetic fixtures.

## Change Scope

- Add a focused markdown plan for the bounded historical OpenAQ collector test.
- Add a Behave contract for `collect_openaq_historical.sh`.
- Add a location-limit option to the historical OpenAQ wrapper/Python entrypoint.
- Add or extend step definitions needed to validate bounded historical OpenAQ raw parquet outputs.

## Non-Goals

- Do not optimize the OpenAQ historical S3 path in this slice.
- Do not replace the existing broad historical Air Quality contract.
- Do not add mocks or synthetic historical OpenAQ fixtures.
