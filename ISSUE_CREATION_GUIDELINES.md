# GitHub Issue Creation Guidelines

## Purpose
This note defines how maintainers and coding agents should draft issues for this repository so they are actionable, testable, and easy to hand off.

## Preferred Issue Structure
For implementation and improvement tasks, use this section order:

1. `Problem`
2. `Desired outcome`
3. `Constraints / notes`
4. `Done when`
5. `Verification`
6. `Out of scope` (recommended)

Keep each section concrete and implementation-friendly.

## Template Usage

### Task-style issues (default for release hardening and repo improvements)
- Template: `.github/ISSUE_TEMPLATE/public_release_task.md`
- Typical labels: `public-release` plus one topical label (`documentation`, `security`, `testing`, `ci`, `governance`, etc.)

### Bug reports from external users
- Template: `.github/ISSUE_TEMPLATE/bug_report.yml`

## Quality Bar for Every New Issue
- One issue should represent one clearly scoped deliverable.
- Include exact file paths where relevant.
- Include acceptance criteria under `Done when` that are binary (pass/fail).
- Include at least one concrete verification command or check.
- Call out explicit non-goals in `Out of scope` to prevent scope creep.
- Use clear, action-oriented titles (for example, `Fix stale ERA5 wrapper reference to missing module`).

## Recommended Authoring Workflow

1. Draft in Markdown first (local file or scratch buffer).
2. Validate structure and checks:
- Are all required sections present?
- Is verification realistic on this repo?
- Are constraints specific enough for a handoff?
3. Create the GitHub issue.

## CLI Workflow Notes (`gh`)
Use whichever method is practical:

- Interactive template flow:
  - `gh issue create -R AnthonyMockler/air_quality_prediction --template "Public Release Task"`
- Non-interactive body-file flow:
  - `gh issue create -R AnthonyMockler/air_quality_prediction --title "<title>" --body-file /path/to/body.md --label public-release`

Note: current `gh` behavior does not support combining `--template` with `--body-file` in non-interactive mode. If using `--body-file`, include the full structure directly in that file.

## Copy-Paste Skeleton
```md
## Problem

## Desired outcome

## Constraints / notes
- 

## Done when
- 

## Verification
- 

## Out of scope
- 
```
