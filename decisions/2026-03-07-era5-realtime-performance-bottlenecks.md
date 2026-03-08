# Decision: ERA5 Realtime Performance Optimization Focus

## Date
2026-03-07

## Decision
Prioritize ERA5 realtime performance work on request orchestration and wait-policy cleanup before deep interpolation algorithm changes.

## Why
- Fresh ERA5-only realtime benchmark (THA, `2t`, `--hours 24`) completed in ~108 seconds pipeline duration and ~113 seconds step duration, with a large share of time attributable to explicit wait policies.
- Current wrapper ignores explicit `--idw-rings`/`--idw-weight-power` overrides and always re-applies config defaults, reducing operator control and forcing slower interpolation settings.
- Realtime mode forcibly expands short lookbacks to 7 days, which increases request count and processing volume for bounded test runs.
- There are fixed sleeps and layered retry delays in the realtime request loop that are not adaptive to actual provider signals.

## Change Scope
- Make ERA5 wrapper respect explicit CLI overrides for IDW settings.
- Separate “prediction-safe 7-day window” behavior from “collection benchmark/control” behavior with explicit flags.
- Replace fixed request pacing sleeps with adaptive policy driven by response outcomes.
- Keep output file naming/schema contracts stable unless explicitly versioned.

## Non-Goals
- No model training/prediction changes.
- No rewrite of all IDW math in first iteration.
- No expansion to non-ERA5 pipelines during this optimization pass.
