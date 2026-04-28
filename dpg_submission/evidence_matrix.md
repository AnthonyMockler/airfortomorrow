# DPG Evidence Matrix And Gap Backlog

Status: Draft for planning
Last updated: 2026-04-28

## Summary

Air for Tomorrow has a strong starting position for DPG submission because the repository already includes open-source licensing, technical documentation, a model card, dataset provenance, community files, Docker-based setup, and operational limitations. The main remaining risks are submission evidence quality, legal/ownership wording, platform/data-license nuance, and clear do-no-harm/privacy documentation.

`dpg_submission/` is a working/internal-prep folder for now. Promotion of selected polished outputs into public repo docs is deferred until final review/submission.

## Criteria Matrix

| DPG criterion | Current evidence | Status | Gap / planning note |
|---|---|---:|---|
| 1. SDG relevance | `README.md`, `MODELCARD.MD`, public-health use case, PM2.5 focus for Laos/Thailand. User confirmed application should link to SDG 3, SDG 11, and SDG 13. | Partial | Need exact SDG target mapping and concise application text. |
| 2. Open licensing | `LICENSE` is GPL-3.0; project owner confirmed all code is GPL licensed; external datasets are governed as described in `EXTERNAL_DATASETS_AND_LICENSES.md`. | Strong | Final plan should include an evidence-link/provenance check before submission. |
| 3. Clear ownership | Repository is under `unicef`; README/model card cite UNICEF teams and collaborators; owner confirmed as UNICEF with owner office location Bangkok, Thailand; supporting public UNICEF story identified. | Strong | Final answer should cite both the UNICEF story and repository documentation. |
| 4. Platform independence | Docker, Python, open-source dependencies, file-based artifacts, source-specific collectors, source contracts, and runtime `.env` credentials for some external live data services. | Strong | Final answer should emphasize intended 100% open architecture while distinguishing external data-service accounts from closed-source software dependencies. |
| 5. Documentation | README, DOCUMENTATION, architecture/dataflow/source-contract docs, model card, operations docs. | Strong | Need reviewer-oriented documentation index with stable public links. |
| 6. Non-PII data extraction | Current repo artifacts include processed source parquet files, engineered silver feature tables, daily prediction parquet files, optional PNG maps, YAML configuration, CSV static/supporting assets, and pretrained XGBoost model artifact. | Strong | Final answer should explain current outputs as-is; do not plan a new export feature unless separately requested. |
| 7. Privacy and applicable laws | Project owner confirmed no PII is collected; `SECURITY.md`, `SUPPORT.md`, `MODELCARD.MD`, and `EXTERNAL_DATASETS_AND_LICENSES.md` provide relevant security, support, intended-use, limitation, and source-terms evidence. | Partial | Some responsible-use guidance already lives in the model card. An implementation agent must read/analyze those files and decide whether an explicit privacy/do-no-harm page is still needed before final submission. |
| 8. Standards and best practices | Candidate evidence includes H3, Parquet, CSV, YAML, JSON, GeoTIFF/NetCDF/GRIB where applicable, Docker, Git/Git LFS, source contracts, CI/tests, community files, model card, security reporting, and dataset provenance. | Partial | More research needed. See `dpg_submission/standards_best_practices_research.md`; final answer must compare similar DPG submissions and avoid unsupported claims. |
| 9A. Data privacy and security | Project owner confirmed no PII is collected. Evidence includes environmental data pipeline, runtime credentials, `.env` git-ignored, security reporting, support routing, and model-card limitations. | Strong | Need verify with secret scan and have an agent analyze existing repo links before deciding whether to add an explicit PII/security statement. |
| 9B. Inappropriate/misleading/illegal content | Project owner confirmed no UGC and no PII; raw sensor inputs are environmental readings from OpenAQ/AirGradient; no user-generated content platform; model card has intended use, out-of-scope uses, risks, limitations, and recommendations. | Strong | Use `MODELCARD.MD` as the primary evidence source. Also complete a responsible-AI risks/harms/benefits follow-up; if an agent finds a gap, improve the model card rather than creating a separate policy artifact by default. |
| 9C. Harassment protection | CODE_OF_CONDUCT, CONTRIBUTING, SUPPORT, SECURITY, issue/PR templates. | Strong | Need cite exact links and mention GitHub interaction surface. |
| Scale of solution | Active deployment confirmed for Laos and Thailand; Air for Tomorrow confirmed as both software/repo name and wider programme name; model card says the current pretrained model is for Laos/Thailand, while workflows are designed for broader adaptation with local data, calibration/retraining, and validation; UNICEF story provides supporting context for how the programme is being used; partner list supplied and NRERI/MAE naming citation note added. | Partial | Need deployment dates, operational cadence, and final public naming permissions. Keep positioning focused on AI model/software; sensors are supporting data infrastructure/training data, not the core product. |

## Proposed Evidence Pack Deliverables

| Deliverable | Purpose | Likely file/path |
|---|---|---|
| DPG questionnaire draft | Submission-ready answer sheet for portal copy/paste. | `dpg_submission/questionnaire_draft.md` |
| Evidence matrix | Tracks each criterion, current evidence, gaps, owner input, and implementation tasks. | `dpg_submission/evidence_matrix.md` |
| Public evidence link index | One-stop map of stable repository URLs for reviewers. | `dpg_submission/evidence_links.md` |
| SDG relevance note | Exact SDG targets and concise justification. | `dpg_submission/sdg_relevance.md` or repository docs if public-facing. |
| Ownership and licensing note | Clarifies UNICEF ownership, upstream data rights, and redistributed artifacts. | `dpg_submission/ownership_and_licensing.md` initially; public doc if needed. |
| Platform independence note | Explains open runtime, external data dependencies, and adapter/file-contract design. | `docs/PLATFORM_INDEPENDENCE.md` or `dpg_submission/platform_independence.md` |
| Privacy and do-no-harm note | Explicit no-PII posture, credential handling, model misuse risks, and reporting paths. | `docs/PRIVACY_AND_DO_NO_HARM.md` or `dpg_submission/privacy_and_do_no_harm.md` |
| Data extraction note | Explains import/export formats and, if needed, adds CSV/GeoJSON export path. | `docs/DATA_EXPORTS.md` or `dpg_submission/data_extraction.md` |

## Candidate Implementation Workstreams

1. Evidence collection and questionnaire completion.
   - Fill owner-controlled fields.
   - Convert repository evidence into public links.
   - Draft concise copy for every portal question.

2. Public-facing documentation hardening.
   - Add or update docs for platform independence, privacy/do-no-harm, and data extraction.
   - Ensure each new page points to existing source contracts, model card, and dataset license inventory.

3. Verification and release readiness.
   - Run repository tests/Behave tiers appropriate to docs and any utility changes.
   - Run secret scan and license/provenance spot checks.
   - Confirm no sensitive draft owner/contact information is committed.

4. Final submission support.
   - Prepare final portal copy.
   - Compile reviewer evidence links.
   - Record unresolved owner/legal questions separately from public submission text.

## Open Owner Questions

1. Confirm `jhanan@unicef.org` is the correct monitored alternate email before submission.
2. What are the confirmed deployment dates and operational cadence in Laos and Thailand?
3. Research and confirm all government partner names and final public wording in `dpg_submission/partner_citations.md`.
4. Agent follow-up: validate whether DHIS2 integration exists in code/docs/public deployment context, how it works, and whether it can be cited. Do not claim DHIS2 interoperability until verified.
5. Agent follow-up: read and analyze existing repo privacy/security/responsible-use evidence links (`SECURITY.md`, `SUPPORT.md`, `MODELCARD.MD`, `EXTERNAL_DATASETS_AND_LICENSES.md`, relevant README sections). For harm/misleading-use gaps, improve `MODELCARD.MD` first.
6. Agent follow-up: complete or adapt a UN Global Pulse risks/harms/benefits assessment, and check whether UNICEF-specific AI guidance applies. See `dpg_submission/responsible_ai_assessment_followup.md`.
7. Confirm final wording for English-only documentation availability before submission.
