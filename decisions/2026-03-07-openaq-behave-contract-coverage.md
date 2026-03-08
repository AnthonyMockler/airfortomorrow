# Decision: OpenAQ Behave Contract Coverage

## Date
2026-03-07

## Decision
Add focused Behave coverage for the OpenAQ realtime collector and its integration surface so we can preserve current CLI/API contracts while improving performance later.

## Why
- OpenAQ is currently the slowest realtime collector and is the first optimization target.
- We need protection against accidental contract drift while refactoring rate-limiting and retry behavior.
- Existing Behave coverage validates full quickstart flows but does not deeply assert OpenAQ CLI surfaces and OpenAQ raw-data contract shape.

## Change Scope
- Add OpenAQ-specific Behave scenarios for command-line interface contract and OpenAQ-only pipeline invocation.
- Add OpenAQ-specific Behave step definitions to validate realtime parquet schema and data usefulness.
- Execute OpenAQ-focused Behave scenarios in Docker and capture evidence.

## Non-Goals
- No production behavior changes in collectors/processors.
- No retry/rate-limit policy changes in this step.
- No expansion to non-OpenAQ pipeline test coverage.
