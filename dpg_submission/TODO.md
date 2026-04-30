# DPG Submission TODO

Status: Working checklist
Last updated: 2026-04-30

This is the single checklist for remaining work before submitting Air for Tomorrow to the Digital Public Goods Alliance. It consolidates follow-ups from the interview notes, DPG working docs, evidence matrix, Open AI Model evidence map, impact notes, partner citations, responsible-AI notes, and implementation plan.

Use this file as the first stop for future agents. Detailed evidence and research notes remain in the referenced files.

## Priority 0: Final Submission Decision

- [ ] Decide whether `dpg_submission/` remains an internal working folder or whether selected files should be promoted into public repository documentation before submission.
- [ ] Confirm who is authorised to submit the DPG application on behalf of UNICEF.
- [ ] Confirm the final monitored contact email. Current placeholder: `jhanan@unicef.org`; marked for review.
- [ ] Confirm preferred aliases for the solution: Air for Tomorrow, Air4Tomorrow, A4T.
- [ ] Confirm final portal organisation type/owner details for UNICEF and owner office location, currently drafted as Bangkok, Thailand.

## Priority 1: Open AI Model Evidence

Source: `dpg_submission/open_ai_model_evidence_map.md`

- [ ] Review every training, validation, and test/evaluation dataset for Open Definition-conformant licensing and availability.
- [ ] Pay special attention to OpenAQ per-record upstream licenses, AirGradient CC BY-SA obligations, JAXA P-Tree terms, Copernicus/ECMWF terms, WorldPop, Dynamic World/Sentinel, NASA FIRMS, NASA SRTM, and geoBoundaries.
- [ ] Create a dataset-card-style summary for `data/training/silver_dataset.parquet`, including dataset identity, version/date, maintainer, geographic/temporal coverage, row/field schema, target variable, split logic, known limitations, and source/license provenance.
- [ ] Clarify whether the 2025 hold-out validation window is the final test/evaluation set or whether a separate test set exists.
- [ ] Confirm whether `notebooks/air_quality_pipeline_walkthrough.ipynb` is the canonical training/validation/testing workflow for DPG review.
- [ ] If the notebook is canonical, add a short reproducibility note that identifies the expected input artifact, configuration, split, model settings, and expected metrics.
- [ ] Decide whether a scripted training/evaluation entrypoint is needed, or whether the notebook plus model card are enough.
- [ ] Add compact model version, release date, and contact metadata to `MODELCARD.MD` or the final questionnaire answer.
- [ ] Confirm the GPL-3.0 wording is explicit enough for the pretrained model artifact `src/models/xgboost_model.json`.
- [ ] Add or improve monitoring/update process wording: who reviews model issues, retraining triggers, model update documentation, and how users report performance concerns.

## Priority 1: Privacy, Security, And Legal Evidence

Sources: `dpg_submission/evidence_matrix.md`, `dpg_submission/questionnaire_draft.md`, `docs/DPG_READINESS.md`

- [ ] Identify applicable UNICEF privacy, data-protection, security, and AI policy evidence, or get owner-approved wording explaining why the no-PII environmental-data posture satisfies the DPG privacy question.
- [ ] Strengthen the DPG privacy answer beyond "no PII" by addressing non-PII/group-data risks, environmental/geospatial data flows, data minimization, data access, retention/deletion, and credential handling.
- [ ] Read and analyze `SECURITY.md`, `SUPPORT.md`, `MODELCARD.MD`, `EXTERNAL_DATASETS_AND_LICENSES.md`, and relevant README limitations before finalizing the privacy/security answer.
- [ ] Decide whether to add an explicit public privacy/security/do-no-harm note, or keep the evidence in `docs/DPG_READINESS.md`, `MODELCARD.MD`, and the questionnaire.
- [ ] Run a lightweight secret scan before final submission and record the result.
- [ ] Run a license/provenance spot check against `EXTERNAL_DATASETS_AND_LICENSES.md`.

## Priority 1: Do No Harm And Responsible AI

Sources: `dpg_submission/responsible_ai_assessment_followup.md`, `dpg_submission/reference_docs/responsible_ai_references.md`, `MODELCARD.MD`

- [ ] Complete or adapt a UN Global Pulse risks/harms/benefits assessment for the Air for Tomorrow model and pipeline.
- [ ] Check whether UNICEF-specific AI guidance applies, especially UNICEF guidance on AI and children.
- [ ] Decide whether the completed assessment requires updates to `MODELCARD.MD`; improve the model card first if public-facing gaps are found.
- [ ] Sharpen the inappropriate/misleading/illegal content answer: state that Air for Tomorrow is not a content-hosting product, then describe the reporting/triage route and expected response time.
- [ ] Explicitly state that the core software/model has no child accounts, no UGC, and no end-user interaction surface.
- [ ] Explain that GitHub issues/PRs are the only contributor interaction surface and are governed by the code of conduct, support, security, maintainer review, and GitHub moderation.
- [ ] Add response-process wording for harmful model use, misleading claims, security issues, and documentation/model-card corrections.
- [ ] Keep high-stakes warnings clear: model outputs are estimates and should be combined with local monitoring and official advisories for regulatory, medical, or emergency decisions.

## Priority 1: Deployment, Impact, And Scale

Sources: `dpg_submission/impact_evidence_followup.md`, `docs/DPG_READINESS.md`, UNICEF public stories

- [ ] Confirm deployment dates for Laos and Thailand.
- [ ] Confirm operational cadence: how often the pipeline/model is run, by whom, and for what operational workflow.
- [ ] Collect named operational users/adopters that may be cited publicly.
- [ ] Gather Thailand-specific public evidence if available; current public evidence is stronger for Lao PDR.
- [ ] Identify public dashboards, generated maps, releases, papers, manuscripts, or example outputs that should be linked.
- [ ] Collect technical impact evidence: model/output coverage, prediction/map output volume, performance metrics, sensor-sparse coverage benefit, reproducible workflow evidence.
- [ ] Collect usage or adoption evidence: users, partner workflows, policy/planning touchpoints, workshops, trainings, requests, repository usage, or deployments.
- [ ] Collect outcome evidence if available: improved monitoring, awareness, decision support, public-health or education planning, or operational response examples.
- [ ] Keep sensors in supporting context only. The DPG product is the open-source software, pretrained AI model, documentation, reproducible workflow, and PM2.5 nearcasting outputs.

## Priority 1: Partners, Government Names, And DHIS2

Sources: `dpg_submission/partner_citations.md`, `dpg_submission/reference_docs/partner_reference_sources.md`

- [ ] Confirm final public wording for UNICEF Lao PDR.
- [ ] Confirm final public wording for UNICEF East Asia and Pacific Regional Office / EAPRO Frontier Data Lab.
- [ ] Confirm final public wording for Lao PDR Ministry of Education and Sports.
- [ ] Confirm current official name and public wording for the Lao environment/agriculture partner, including MAE/NRERI/Environmental Lab naming.
- [ ] Confirm whether the Ministry of Health should be named publicly.
- [ ] Validate whether DHIS2 integration exists in code, docs, or public deployment evidence.
- [ ] Do not cite DHIS2 interoperability unless supporting evidence is added.
- [ ] Mark every government partner name with source link, confidence, and public-use status before final submission.

## Priority 2: Questionnaire And Evidence Pack

Sources: `dpg_submission/questionnaire_draft.md`, `dpg_submission/evidence_matrix.md`, `dpg_submission/official_resources.md`

- [ ] Update `questionnaire_draft.md` with final Open AI Model wording after the AI evidence gaps above are resolved.
- [ ] Replace internal notes in final answer fields with polished portal-ready text.
- [ ] Confirm all `main` branch GitHub links resolve after the DPG branch is merged or after final publication path is chosen.
- [ ] Compile a final evidence-link index if useful. The proposed file is `dpg_submission/evidence_links.md`.
- [ ] Decide whether to create separate SDG, ownership/licensing, platform independence, privacy/do-no-harm, or data extraction notes, or keep those topics in `docs/DPG_READINESS.md` and the questionnaire.
- [ ] Confirm final English-only documentation wording: documentation is provided in English.
- [ ] Confirm SDG target mapping and keep it concise: likely SDG 3.9, 11.6, and 13.1.
- [ ] Add example maps, paper/manuscript, release URLs, or public highlights if available before submission.

## Priority 2: Standards And Claims Discipline

Sources: `dpg_submission/standards_best_practices_research.md`, `docs/DPG_READINESS.md`

- [ ] Keep standards/best-practices claims specific to actual documented implementation: H3, Parquet, CSV, YAML, JSON, GeoTIFF/NetCDF/GRIB where used, Docker, Git/Git LFS, source contracts, CI/tests, community files, model card, security reporting, and dataset provenance.
- [ ] Do not claim formal adherence to FAIR, UNESCO AI ethics, UNICEF Innovation Principles, OGC, ISO, DHIS2/FHIR, or OpenAPI unless supporting documentation is added.
- [ ] If UNICEF AI guidance is used, cite it as a responsible-AI review reference only after mapping it to actual Air for Tomorrow documentation.

## Priority 3: Public Docs And Release Hygiene

Sources: `docs/DPG_READINESS.md`, `README.md`, implementation plan

- [ ] Decide whether to add public docs such as `docs/TRAINING_DATASET_CARD.md`, `docs/MODEL_GOVERNANCE.md`, or a privacy/do-no-harm page.
- [ ] If public docs are added, ensure they are evidence-backed and do not include internal review notes, provisional contacts, or unapproved partner wording.
- [ ] Run a public-doc safety scan for terms such as `jhanan@`, `NEEDS OWNER INPUT`, `RESEARCH NEEDED`, `future review`, `unverified`, `possible DHIS2`, `working/internal`, and `do not use publicly`.
- [ ] Run a link sanity check for public docs and questionnaire evidence links.
- [ ] Confirm no sensitive draft owner/contact information is committed into public-facing docs.
- [ ] Confirm final changed-file list before staging.
- [ ] For docs-only changes, record verification commands and skip Behave/tests unless code or workflow behavior changes.

## Done / Strong Enough For Draft Submission

These areas appear strong, but should still receive a final link/proofread pass:

- [x] Basic SDG relevance draft for SDG 3, 11, and 13.
- [x] GPL-3.0 software license identified.
- [x] UNICEF ownership identified.
- [x] Platform-independence framing drafted, including distinction between open software dependencies and external data-service credentials.
- [x] Core documentation inventory drafted.
- [x] Non-PII data extraction/output answer drafted.
- [x] Standards/best-practices research notes drafted.
- [x] Public DPG readiness page drafted.
- [x] Open AI Model evidence map drafted.
