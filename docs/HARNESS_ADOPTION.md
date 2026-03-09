# Harness Adoption

## Purpose

This repo is adopting a more explicit harness-engineering workflow so that humans and coding agents can load context faster, follow the same operating model, and rely on repository-local validation instead of ad hoc chat instructions.

## Implemented So Far

- Phase 0:
  - first-pass operating principles were frozen in `decisions/2026-03-09-harness-engineering-adoption.md`
  - the working plan was activated in `plans/2026-03-09-harness-engineering-adoption-tdd-plan.md`
- Phase 1:
  - root `AGENTS.md` became a short operating map
  - durable repository knowledge moved into focused files under `docs/`
- Phase 1.5:
  - rebalanced the docs toward repository purpose, concrete code ownership, and pipeline behavior
  - softened over-broad Behave-first wording so workflow contracts and narrower Python logic are documented differently

## Planned Later Phases

- add mechanical repository guardrails
- extend repository-hygiene contract checks
- add structured run manifests
- split CI into fast blocking lanes and slower scheduled checks
- add recurring cleanup and portability guidance for other repos

## Rollout Constraint

Early phases are intentionally docs-and-governance heavy. The goal is to improve clarity first, then add enforcement once the team is confident the rules are correct and low-noise.
