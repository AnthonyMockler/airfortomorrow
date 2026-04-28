# DPG Submission Readiness Design

- Status: Approved for implementation planning
- Owner: Codex / UNICEF project team
- Last Updated: 2026-04-28

## Goal

Prepare Air for Tomorrow for Digital Public Goods Alliance submission as Open Software + Open AI Model by producing a full public-facing DPG readiness package, while keeping working drafts and unresolved review notes separate until final approval.

## Chosen Approach

Use a full DPG readiness publication approach.

The project will maintain `dpg_submission/` as the local coordination workspace for drafts, research notes, unresolved questions, reference links, and provisional evidence. In parallel, the implementation will promote polished, submission-safe outputs into public repository documentation so reviewers have stable public evidence links.

This approach was chosen over an evidence-pack-only approach because the DPG review benefits from public, durable evidence. It was chosen over ad hoc documentation edits because unresolved items such as partner names, DHIS2 integration, responsible-AI review, and Indicator 8 standards claims need explicit gates before public text is published.

## Scope

The readiness work covers:

- DPG questionnaire evidence for all nine indicators.
- Draft final application answers for Air for Tomorrow.
- A public DPG evidence page in the repository.
- Model card review and targeted improvements if responsible-AI gaps are found.
- Standards and best-practices research using comparable DPG examples.
- Public partner, deployment, and integration validation.
- Verification instructions for documentation-only versus code/workflow changes.

The readiness work does not include:

- Building new prediction features.
- Changing the core pipeline unless a DPG evidence gap cannot be solved through documentation.
- Claiming DHIS2 interoperability until the integration is verified in code, docs, or public deployment evidence.
- Publishing provisional contacts, unapproved partner names, or internal review notes.

## Primary Public Artifacts

### `docs/DPG_READINESS.md`

Create one central reviewer-facing evidence page. It should map each DPG indicator to:

- concise answer,
- public evidence links,
- caveats or scope notes,
- related repository files.

This page should avoid duplicating full content from canonical documents. It should point reviewers to the README, model card, external dataset inventory, security/support docs, contribution docs, and source contracts.

### `MODELCARD.MD`

Keep the model card as the primary responsible-AI artifact. Review it against the UN Global Pulse risks/harms/benefits approach and UNICEF AI guidance. If gaps are found, update the model card rather than creating a separate public responsible-AI policy artifact by default.

The model card should remain the source of truth for:

- model purpose,
- intended use,
- out-of-scope use,
- bias, risks, and limitations,
- recommendations,
- evaluation metrics,
- Laos/Thailand model scope,
- requirements for calibration, retraining, and validation outside Laos and Thailand.

### `README.md`

Add only a small pointer to `docs/DPG_READINESS.md` if the public evidence page is ready for reviewers. Avoid turning the README into the DPG application itself.

### Existing Canonical Docs

Use existing docs as primary evidence where possible:

- `README.md`
- `DOCUMENTATION.md`
- `MODELCARD.MD`
- `EXTERNAL_DATASETS_AND_LICENSES.md`
- `SECURITY.md`
- `SUPPORT.md`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `.github/`
- `docs/ARCHITECTURE.md`
- `docs/DATAFLOW.md`
- `docs/SOURCE_CONTRACTS.md`
- `docs/RELIABILITY_AND_OPERATIONS.md`

### `dpg_submission/`

Keep this as the working/internal-prep folder for now. It may include draft questionnaire answers, research notes, reference links, evidence matrices, and unresolved review questions. Do not treat it as final public documentation until the project team decides what to commit or publish.

## Workstreams

### 1. Evidence Audit

Audit current repository evidence against the DPG questionnaire and the local evidence matrix.

Inputs:

- `dpg_submission/questionnaire_draft.md`
- `dpg_submission/evidence_matrix.md`
- official DPGA references under `dpg_submission/reference_docs/`
- existing public repo docs and governance files.

Outputs:

- updated questionnaire draft with public evidence links,
- updated evidence matrix with status per indicator,
- list of public documentation changes needed before submission.

### 2. Public Documentation Publication

Promote reviewer-safe material into public docs.

Expected output:

- `docs/DPG_READINESS.md`
- optional README pointer to the DPG readiness page.

Rules:

- Public docs must not include provisional contact details.
- Public docs must not include unapproved partner wording.
- Public docs must not claim unverified DHIS2 integration.
- Public docs must not over-emphasise sensors; sensors are supporting data infrastructure and training/validation data for the AI model, not the core product.

### 3. Responsible AI And Harm Review

Review Air for Tomorrow as an Open AI Model submission.

Inputs:

- `MODELCARD.MD`
- `dpg_submission/responsible_ai_assessment_followup.md`
- UN Global Pulse risks/harms/benefits assessment reference
- UNICEF AI guidance references.

Outputs:

- either a finding that the model card is sufficient,
- or targeted edits to `MODELCARD.MD`.

Review focus:

- no PII,
- no user-generated content,
- PM2.5 prediction misuse risks,
- sensor-sparse performance limitations,
- underprediction at high pollution concentrations,
- child/public-health context,
- human oversight for high-stakes decisions,
- clear Laos/Thailand scope for the pretrained model.

### 4. Standards And Best Practices Research

Research DPG Indicator 8 using official DPGA references and comparable DPG registry examples.

Inputs:

- `dpg_submission/standards_best_practices_research.md`
- `dpg_submission/reference_docs/similar_dpg_examples.md`
- DPG registry examples such as ClimWeb, DiCRA, GeoPrism Registry, and Ersilia Model Hub.

Outputs:

- a curated standards and best-practices answer,
- evidence links for each claim,
- documentation edits only where needed to close a real evidence gap.

Allowed candidate areas include H3, Parquet, CSV, YAML, JSON, GeoTIFF/NetCDF/GRIB where applicable, Docker, Git/Git LFS, model card transparency, dataset provenance, source contracts, CI/tests, contribution guidelines, code of conduct, and security reporting.

Do not claim FAIR, UNESCO AI ethics, UNICEF Innovation Principles, OGC, ISO, DHIS2/FHIR, or OpenAPI adherence unless repository evidence supports the claim or the documentation is updated to support it accurately.

### 5. Partner, Deployment, And Integration Validation

Validate public names and deployment/integration claims before they appear in public docs or final application text.

Inputs:

- `dpg_submission/partner_citations.md`
- `dpg_submission/reference_docs/partner_reference_sources.md`
- UNICEF blog post on Air for Tomorrow
- public ministry/partner sources
- repository search for DHIS2 references.

Outputs:

- approved public partner wording,
- clear deployment statement for Laos and Thailand,
- decision on whether DHIS2 can be cited,
- updated questionnaire draft and public DPG evidence page.

Known current constraints:

- Owner is UNICEF.
- Owner location is Bangkok, Thailand.
- Air for Tomorrow is both the software/repository name and the wider programme name.
- Active deployments are Laos and Thailand.
- Government partner wording needs research and public naming review.
- DHIS2 integration needs checking and validation before any interoperability claim.

## DPG Positioning Decisions

- Submit as Open Software + Open AI Model.
- Link SDG relevance to SDG 3, SDG 11, and SDG 13.
- State that documentation is provided in English only.
- State that all project code is GPL-3.0 licensed.
- State that external datasets are governed by `EXTERNAL_DATASETS_AND_LICENSES.md`.
- State that no PII is collected, stored, or distributed by the core pipeline.
- State that the project does not collect, host, or distribute user-generated content.
- State that raw sensor inputs are environmental readings from OpenAQ and AirGradient.
- State that the core workflow is intended to be 100% open, while some live data collection paths require external data-service accounts or credentials.
- State that current artifacts include processed source parquet files, engineered silver feature tables, daily prediction parquet files, optional map PNG files, YAML configuration, CSV static/supporting assets, and the pretrained XGBoost model artifact.
- State that the pretrained model is for Laos and Thailand only; use elsewhere requires local data, calibration/retraining, and validation.

## Review Gates

### Evidence Gate

Every DPG claim in public docs and final questionnaire answers must link to repository evidence, official DPGA guidance, or approved public partner sources.

### Public-Safety Gate

Remove or avoid provisional contact details, unapproved partner claims, uncertain DHIS2 claims, and internal notes from public docs.

### Responsible-AI Gate

Read `MODELCARD.MD` against UN Global Pulse and UNICEF AI guidance. If gaps exist, update the model card before relying on it in the DPG answer.

### Partner/Deployment Gate

Confirm public names and deployment facts before publishing them outside `dpg_submission/`.

### Verification Gate

For docs-only changes, run lightweight markdown/link checks where practical. If code or workflow changes are made, run the relevant repository verification commands from `AGENTS.md`.

## Implementation Planning Notes

The implementation plan should decompose this into separately verifiable documentation and research tasks. Tasks that only update documentation should not require full pipeline tests. Tasks that alter code, workflow behavior, or submission-support scripts should include the relevant repo verification command.

The plan should not publish or stage `dpg_submission/` wholesale unless the project team explicitly decides that the working folder should become part of the public repository.

