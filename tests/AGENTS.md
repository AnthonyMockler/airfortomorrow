# TESTS KNOWLEDGE BASE

**Generated:** 2026-03-06

## OVERVIEW
Repository tests use **Behave BDD** as the preferred style for workflow and contract coverage, executed inside Docker for dependency parity.

## STYLE RULES
- Write tests as Gherkin features under `features/` with clear Given/When/Then intent.
- Keep step definitions in `features/steps/` small and reusable.
- Prefer command-level contract checks and atomic workflow checks over monolithic end-to-end scenarios.
- Tag scenarios consistently:
  - `@smoke`: fast runtime/environment checks
  - `@contract`: CLI/help/argument behavior
  - `@quickstart`: README setup/workflow coverage
  - `@slow`: long-running scenarios
  - `@live`: scenarios that require external APIs/network conditions

## EXECUTION RULES
- Run BDD tests through Docker:
  - `./scripts/run_behave_tests.sh`
- Avoid host execution unless debugging locally with explicit opt-in.
- Default Behave execution should exclude `@slow` and `@live`.

## AUTHORING GUIDELINES
- Keep scenarios atomic so failures isolate to one workflow responsibility.
- Validate observable outcomes (exit code, output text, file artifacts).
- Reuse shared command-running helpers from `features/environment.py` instead of custom subprocess logic per step file.
- Use scenario outlines for repeated contract checks (for example, script help coverage).
