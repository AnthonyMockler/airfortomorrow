# DPG Submission Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a full DPG submission readiness package for Air for Tomorrow, including public reviewer-facing documentation, updated application draft evidence, and gated follow-up research for partner, responsible-AI, and standards claims.

**Architecture:** Keep `dpg_submission/` as the working/internal-prep area while promoting only polished, reviewer-safe content into public repository docs. Use `docs/DPG_READINESS.md` as the central public evidence page, with targeted updates to `MODELCARD.MD` and `README.md` only when evidence review shows a concrete gap.

**Tech Stack:** Markdown documentation, DPG Standard/questionnaire, repository evidence files, web research references, `rtk`-prefixed shell verification, optional markdown/link checking.

---

## File Structure

- Create: `docs/DPG_READINESS.md`
  - Public reviewer-facing DPG evidence page.
  - Maps every DPG indicator to concise claims, evidence links, and scope notes.
- Modify: `README.md`
  - Add a short pointer to `docs/DPG_READINESS.md` after that page is complete.
- Modify conditionally: `MODELCARD.MD`
  - Improve only if responsible-AI review finds gaps against existing model-card claims, UN Global Pulse, or UNICEF AI guidance.
- Modify: `dpg_submission/questionnaire_draft.md`
  - Keep as the copy/paste application draft and update it with final public evidence links.
- Modify: `dpg_submission/evidence_matrix.md`
  - Keep as the implementation tracker for indicator status and unresolved review gates.
- Modify: `dpg_submission/standards_best_practices_research.md`
  - Record Indicator 8 research findings and final candidate claims.
- Modify: `dpg_submission/partner_citations.md`
  - Record validated public partner names, source links, and public-naming decisions.
- Modify: `dpg_submission/responsible_ai_assessment_followup.md`
  - Record responsible-AI assessment findings and whether model-card edits were required.

Important staging rule: do not stage `dpg_submission/` wholesale. It remains a working/internal-prep folder unless the project team explicitly decides to publish it. When committing public docs, stage only public files and any explicitly approved working notes.

## Task 1: Prepare Implementation Branch Or Worktree

**Files:**
- Read: `AGENTS.md`
- Read: `docs/superpowers/specs/2026-04-28-dpg-submission-readiness-design.md`
- Modify: none

- [ ] **Step 1: Inspect current branch and worktree state**

Run:

```bash
rtk git status --short
rtk git branch --show-current
```

Expected:

- Existing unrelated untracked files may be present.
- `dpg_submission/` may be untracked.
- No unexpected staged changes.

- [ ] **Step 2: Create an implementation branch if not already on a bounded DPG branch**

Run:

```bash
rtk git switch -c codex/dpg-submission-readiness
```

Expected:

- New branch `codex/dpg-submission-readiness` is checked out.

If the branch already exists, run:

```bash
rtk git switch codex/dpg-submission-readiness
```

Expected:

- Existing branch `codex/dpg-submission-readiness` is checked out.

- [ ] **Step 3: Confirm no unapproved working notes are staged**

Run:

```bash
rtk git diff --cached --name-only
```

Expected:

- Empty output.

## Task 2: Audit DPG Questionnaire Evidence

**Files:**
- Modify: `dpg_submission/questionnaire_draft.md`
- Modify: `dpg_submission/evidence_matrix.md`
- Read: `dpg_submission/official_resources.md`
- Read: `dpg_submission/reference_docs/official_dpga_references.md`
- Read: `README.md`
- Read: `MODELCARD.MD`
- Read: `EXTERNAL_DATASETS_AND_LICENSES.md`
- Read: `SECURITY.md`
- Read: `SUPPORT.md`
- Read: `CONTRIBUTING.md`
- Read: `CODE_OF_CONDUCT.md`
- Read: `.github/pull_request_template.md`
- Read: `docs/ARCHITECTURE.md`
- Read: `docs/DATAFLOW.md`
- Read: `docs/SOURCE_CONTRACTS.md`
- Read: `docs/RELIABILITY_AND_OPERATIONS.md`

- [ ] **Step 1: Read the official DPG questionnaire and current local draft**

Run:

```bash
rtk read dpg_submission/questionnaire_draft.md
rtk read dpg_submission/evidence_matrix.md
rtk read dpg_submission/reference_docs/official_dpga_references.md
```

Expected:

- Local draft contains all major DPG questionnaire sections.
- Evidence matrix includes every DPG indicator and current known follow-ups.

- [ ] **Step 2: Audit repository evidence for each indicator**

For each of the following indicator groups, inspect the listed files and record the strongest public evidence links in `dpg_submission/evidence_matrix.md`:

```text
1. SDG relevance: README.md, MODELCARD.MD, UNICEF blog link
2. Open licensing: LICENSE, EXTERNAL_DATASETS_AND_LICENSES.md, MODELCARD.MD
3. Ownership: README.md, MODELCARD.MD, UNICEF blog link, GitHub repo URL
4. Platform independence: README.md, Dockerfile, requirements.txt, env_template, docs/SOURCE_CONTRACTS.md
5. Documentation: README.md, DOCUMENTATION.md, docs/*.md, MODELCARD.MD
6. Non-PII data extraction: README.md, DOCUMENTATION.md, docs/DATAFLOW.md, output path docs
7. Privacy/applicable laws: SECURITY.md, SUPPORT.md, MODELCARD.MD, EXTERNAL_DATASETS_AND_LICENSES.md
8. Standards/best practices: docs, .github, model card, source contracts, tests/workflows
9. Do-no-harm: MODELCARD.MD, SECURITY.md, SUPPORT.md, CODE_OF_CONDUCT.md
Scale: README.md, MODELCARD.MD, UNICEF blog link, partner notes
```

Use this edit rule:

```text
For each row in dpg_submission/evidence_matrix.md, add concrete evidence file names or URLs and mark the status as Strong, Partial, or Needs follow-up. Keep unresolved review gates explicit.
```

- [ ] **Step 3: Update questionnaire draft with evidence links**

Edit `dpg_submission/questionnaire_draft.md` so each answer contains either:

```text
Evidence: cite a specific repository file or public URL that supports the answer.
```

or:

```text
Follow-up: describe the exact verification still needed before final submission.
```

Expected:

- No answer relies on implied evidence.
- Provisional partner, DHIS2, and responsible-AI items remain clearly marked for review.

- [ ] **Step 4: Verify the audit kept working notes internal**

Run:

```bash
rtk git status --short dpg_submission
```

Expected:

- `dpg_submission/` may appear as modified or untracked.
- No `dpg_submission/` files are staged.

## Task 3: Research Standards And Best Practices For Indicator 8

**Files:**
- Modify: `dpg_submission/standards_best_practices_research.md`
- Modify: `dpg_submission/questionnaire_draft.md`
- Modify: `dpg_submission/evidence_matrix.md`
- Read: `dpg_submission/reference_docs/similar_dpg_examples.md`
- Read: `dpg_submission/reference_docs/official_dpga_references.md`
- Read: `README.md`
- Read: `MODELCARD.MD`
- Read: `EXTERNAL_DATASETS_AND_LICENSES.md`
- Read: `.github/`
- Read: `docs/SOURCE_CONTRACTS.md`

- [ ] **Step 1: Review official DPGA standards and best-practices references**

Open these URLs in a browser or web tool and summarize only the parts relevant to Air for Tomorrow:

```text
https://new.digitalpublicgoods.net/toolkit/featured-standards
https://new.digitalpublicgoods.net/toolkit/featured-best-practices
https://new.digitalpublicgoods.net/standard
https://raw.githubusercontent.com/DPGAlliance/DPG-Standard/main/standard-questions.md
```

Expected:

- `dpg_submission/standards_best_practices_research.md` records the DPGA evidence expectation for Indicator 8.

- [ ] **Step 2: Review comparable DPG profiles**

Inspect at least these profiles:

```text
https://www.digitalpublicgoods.net/r/climweb-httpsclimtechafricaclimweb
https://www.digitalpublicgoods.net/r/dicra
https://www.digitalpublicgoods.net/r/geoprism-registry
https://www.digitalpublicgoods.net/r/ersilia-model-hub
```

For each profile, record:

```text
- category
- repository or assessed components
- standards/practices language
- privacy/do-no-harm pattern
- scale/deployment pattern
- useful lesson for Air for Tomorrow
```

Expected:

- `dpg_submission/standards_best_practices_research.md` contains a concise comparison table.

- [ ] **Step 3: Build the Air for Tomorrow Indicator 8 claim set**

In `dpg_submission/standards_best_practices_research.md`, create a final candidate claim list with four sections:

```text
Technical and data standards
Open-source governance practices
Data and AI transparency practices
Security and operational practices
```

Use only claims with evidence in the repository or official external standards pages.

Allowed evidence candidates:

```text
H3, Parquet, CSV, YAML, JSON, GeoTIFF/NetCDF/GRIB where used, Docker, Git/Git LFS, model card, dataset provenance, source contracts, CI/tests, contribution guidelines, code of conduct, security reporting.
```

Explicitly exclude unsupported claims:

```text
FAIR, UNESCO AI ethics, UNICEF Innovation Principles, OGC, ISO, DHIS2/FHIR, OpenAPI.
```

If research shows one of the excluded claims is supportable, record the exact repo evidence before adding it.

- [ ] **Step 4: Update DPG draft answer**

Replace the `RESEARCH NEEDED` text in `dpg_submission/questionnaire_draft.md` for Indicator 8 with a concise answer that follows this structure:

```markdown
Air for Tomorrow follows standards and practices in four areas:

1. Technical and data interoperability: ...
2. Open-source governance: ...
3. Data and AI transparency: ...
4. Security and operations: ...

Evidence: ...
```

Expected:

- Indicator 8 answer contains no unsupported standards.
- Any omitted but tempting frameworks are documented in research notes, not in the final answer.

## Task 4: Validate Partners, Deployment, And DHIS2 Claims

**Files:**
- Modify: `dpg_submission/partner_citations.md`
- Modify: `dpg_submission/questionnaire_draft.md`
- Modify: `dpg_submission/evidence_matrix.md`
- Read: `dpg_submission/reference_docs/partner_reference_sources.md`
- Read: repository files found by search

- [ ] **Step 1: Validate Lao PDR partner names**

Use web research and the links in `dpg_submission/reference_docs/partner_reference_sources.md` to validate these public names:

```text
UNICEF Lao PDR
UNICEF East Asia and Pacific Regional Office
Lao PDR Ministry of Education and Sports
Lao PDR Ministry of Agriculture and Environment
Natural Resources and Environment Research Institute
Environmental Laboratory
Lao PDR Ministry of Health
```

Record each result in `dpg_submission/partner_citations.md` with:

```text
recommended public name
source URL
confidence: high, medium, or low
public-use status: approved by project team, needs project-team review, or do not use publicly
```

Expected:

- No government partner name appears as final without source and confidence.

- [ ] **Step 2: Validate DHIS2 evidence**

Search the repo:

```bash
rtk grep "DHIS2|dhis2|Ministry of Health|MOH|health information" .
```

Expected:

- If no repo evidence exists, record that DHIS2 must not be cited as implemented interoperability.
- If evidence exists, record exact files and whether the integration is implemented, planned, or external to this repo.

- [ ] **Step 3: Update questionnaire wording**

In `dpg_submission/questionnaire_draft.md`, keep deployment/user language conservative:

```text
Active deployments: Laos and Thailand.
Partner wording: use only validated public names.
DHIS2: mention only if validation finds supportable evidence; otherwise keep as follow-up context outside public claims.
```

Expected:

- Questionnaire draft avoids unverified DHIS2 and partner claims.

## Task 5: Complete Responsible-AI Review Against Model Card

**Files:**
- Modify: `dpg_submission/responsible_ai_assessment_followup.md`
- Modify: `dpg_submission/evidence_matrix.md`
- Modify conditionally: `MODELCARD.MD`
- Read: `dpg_submission/reference_docs/responsible_ai_references.md`
- Read: `MODELCARD.MD`
- Read: `README.md`

- [ ] **Step 1: Read the model card sections used for responsible-AI evidence**

Run:

```bash
rtk grep "Intended Use|Out-of-Scope Use|Bias|Risks|Limitations|Recommendations|Evaluation|By Country|By Pollution Bin|Category Agreement" MODELCARD.MD
```

Expected:

- Output identifies the model card sections covering intended use, limitations, risks, recommendations, and evaluation.

- [ ] **Step 2: Review UN Global Pulse and UNICEF AI references**

Read the resources listed in `dpg_submission/reference_docs/responsible_ai_references.md`.

Record in `dpg_submission/responsible_ai_assessment_followup.md`:

```text
benefits covered by current model card
harms or misuse risks covered by current model card
child/public-health considerations covered by current model card
gaps that require model-card edits
decision: model card sufficient, or model card edits required
```

Expected:

- The follow-up note contains a clear decision and evidence.

- [ ] **Step 3: Update the model card only if gaps are found**

If the review finds gaps, edit `MODELCARD.MD` in the relevant existing sections. Prefer targeted edits under:

```text
Uses
Out-of-Scope Use
Bias, Risks, and Limitations
Recommendations
Evaluation
```

Expected:

- The model card remains the primary public responsible-AI artifact.
- No separate public responsible-AI policy document is created by default.

- [ ] **Step 4: Verify no unsupported responsible-AI claims were added**

Run:

```bash
rtk grep "UNESCO|FAIR|certified|compliant|guarantee|guaranteed" MODELCARD.MD docs/DPG_READINESS.md
```

Expected:

- Either no matches, or matches are explicitly justified and evidence-backed.

## Task 6: Draft Public DPG Evidence Page

**Files:**
- Create: `docs/DPG_READINESS.md`
- Read: `dpg_submission/questionnaire_draft.md`
- Read: `dpg_submission/evidence_matrix.md`
- Read: `README.md`
- Read: `MODELCARD.MD`
- Read: `EXTERNAL_DATASETS_AND_LICENSES.md`
- Read: `SECURITY.md`
- Read: `SUPPORT.md`
- Read: `CONTRIBUTING.md`
- Read: `CODE_OF_CONDUCT.md`
- Read: `docs/*.md`

- [ ] **Step 1: Create the DPG readiness page with this structure**

Create `docs/DPG_READINESS.md` with this exact top-level structure:

```markdown
# Digital Public Goods Readiness

Air for Tomorrow is being prepared for Digital Public Goods Alliance submission as Open Software + Open AI Model. This page summarizes public evidence for the DPG Standard and links to canonical repository documentation.

This page is descriptive and does not replace the full DPG application.

## Scope

## Evidence Summary

## 1. SDG Relevance

## 2. Open Licensing

## 3. Clear Ownership

## 4. Platform Independence

## 5. Documentation

## 6. Non-PII Data Extraction

## 7. Privacy And Applicable Laws

## 8. Standards And Best Practices

## 9. Do No Harm

## Scale And Deployment

## Review Notes
```

- [ ] **Step 2: Fill each DPG indicator with concise evidence-backed text**

For each section, include:

```markdown
**Summary:** Write one short paragraph stating the public DPG claim for this indicator.

**Evidence:**
- Link to the repository file or public source that supports the claim.

**Scope notes:** Include a short scope note only when the claim has a boundary reviewers need to understand.
```

Expected:

- Every indicator has at least one evidence link.
- Scope notes are short and specific.
- No internal-only working notes appear.

- [ ] **Step 3: Apply public-safety rules**

Before staging, inspect `docs/DPG_READINESS.md` for these terms:

```bash
rtk grep "Provisional|needs further research|future review|jhanan|unverified|RESEARCH NEEDED|working/internal|do not use publicly" docs/DPG_READINESS.md
```

Expected:

- No matches.

If a match appears, revise the page to remove internal/provisional text.

## Task 7: Add README Pointer

**Files:**
- Modify: `README.md`
- Read: `docs/DPG_READINESS.md`

- [ ] **Step 1: Add one concise pointer to the DPG readiness page**

Add this bullet under the existing public documentation or release/community section that best fits the README structure:

```markdown
- **Digital Public Goods readiness:** [DPG readiness evidence](docs/DPG_READINESS.md) summarizes how Air for Tomorrow maps to the DPG Standard.
```

Expected:

- README points to the public evidence page without duplicating the DPG application.

- [ ] **Step 2: Verify the link target exists**

Run:

```bash
rtk ls docs/DPG_READINESS.md
```

Expected:

- `docs/DPG_READINESS.md` exists.

## Task 8: Finalize Questionnaire Draft For Copy/Paste

**Files:**
- Modify: `dpg_submission/questionnaire_draft.md`
- Modify: `dpg_submission/evidence_matrix.md`
- Read: `docs/DPG_READINESS.md`
- Read: public evidence files referenced from questionnaire

- [ ] **Step 1: Align questionnaire draft with public evidence page**

For each questionnaire section, ensure the draft answer either cites:

```text
docs/DPG_READINESS.md
```

or cites a canonical evidence file directly.

Expected:

- Questionnaire draft and public evidence page do not contradict each other.

- [ ] **Step 2: Remove working markers from final-answer fields**

Run:

```bash
rtk grep "RESEARCH NEEDED|NEEDS OWNER INPUT|Draft basis|Confirm final wording|future review|needs checking" dpg_submission/questionnaire_draft.md
```

Expected:

- Matches may remain only in evidence/notes columns for unresolved items.
- Final-answer cells do not contain these markers.

- [ ] **Step 3: Update evidence matrix statuses**

In `dpg_submission/evidence_matrix.md`, set each DPG criterion status to one of:

```text
Strong
Partial
Needs follow-up
```

Expected:

- No criterion is missing a status.
- Each `Partial` or `Needs follow-up` row has a concrete next action.

## Task 9: Documentation Verification

**Files:**
- Read: `docs/DPG_READINESS.md`
- Read: `README.md`
- Read conditionally: `MODELCARD.MD`
- Read: `dpg_submission/questionnaire_draft.md`
- Read: `dpg_submission/evidence_matrix.md`

- [ ] **Step 1: Run public-doc safety scan**

Run:

```bash
rtk grep "jhanan@|NEEDS OWNER INPUT|RESEARCH NEEDED|needs further research|future review|unverified|possible DHIS2|working/internal|do not use publicly" README.md docs/DPG_READINESS.md MODELCARD.MD
```

Expected:

- No matches in public docs.

- [ ] **Step 2: Run markdown sanity checks**

Run:

```bash
rtk grep "^# " docs/DPG_READINESS.md README.md MODELCARD.MD
rtk grep "\\]\\(([^)]*)\\)" docs/DPG_READINESS.md README.md MODELCARD.MD
```

Expected:

- Headings are present.
- Links are visible for manual inspection.

- [ ] **Step 3: Run repository docs-only verification**

If only Markdown files changed, run:

```bash
rtk git diff --check
```

Expected:

- No whitespace errors.

If code, shell scripts, workflows, or tests changed, also run the relevant command from `AGENTS.md`, such as:

```bash
rtk ./scripts/run_tests.sh
```

Expected:

- Tests pass, or an unrelated blocker is documented with exact failure details.

## Task 10: Commit Public DPG Readiness Changes

**Files:**
- Stage: `docs/DPG_READINESS.md`
- Stage: `README.md`
- Stage conditionally: `MODELCARD.MD`
- Stage conditionally and only with project-team approval: selected `dpg_submission/` files

- [ ] **Step 1: Review changed files**

Run:

```bash
rtk git status --short
rtk git diff --stat
```

Expected:

- Public doc changes are visible.
- `dpg_submission/` is not staged wholesale.

- [ ] **Step 2: Stage public docs**

Run:

```bash
rtk git add docs/DPG_READINESS.md README.md
```

If `MODELCARD.MD` changed, run:

```bash
rtk git add MODELCARD.MD
```

Expected:

- Public docs are staged.
- Working notes remain unstaged unless explicitly approved.

- [ ] **Step 3: Confirm staged file list**

Run:

```bash
rtk git diff --cached --name-only
```

Expected:

- Includes `docs/DPG_READINESS.md`.
- Includes `README.md`.
- Includes `MODELCARD.MD` only if edited.
- Does not include `dpg_submission/` unless explicitly approved.

- [ ] **Step 4: Commit**

Run:

```bash
rtk git commit -m "docs: add DPG readiness evidence"
```

Expected:

- Commit succeeds.

## Task 11: Handoff Summary

**Files:**
- Read: `docs/DPG_READINESS.md`
- Read: `dpg_submission/evidence_matrix.md`
- Read: `dpg_submission/questionnaire_draft.md`
- Read: latest git commit

- [ ] **Step 1: Capture final status**

Run:

```bash
rtk git log --oneline -3
rtk git status --short
```

Expected:

- Latest commit includes public DPG readiness changes.
- Remaining untracked or modified files are either known working notes or unrelated user files.

- [ ] **Step 2: Prepare user-facing handoff**

Report:

```text
- public docs created/updated
- model card changed or confirmed sufficient
- unresolved DPG risks
- exact verification commands and results
- whether dpg_submission/ remains untracked/internal
```

Expected:

- Handoff names all remaining blockers clearly.
- No claim of completion is made without verification evidence.
