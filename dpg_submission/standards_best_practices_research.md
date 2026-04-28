# Standards And Best Practices Research Follow-Up

Status: Research needed
Last updated: 2026-04-28

The DPG application asks for a list of open standards, best practices, and principles the solution adheres to, with links wherever possible. This should not be answered by listing every technology in the repository. It should be a curated, evidence-backed answer that connects Air for Tomorrow's actual design to relevant DPG expectations.

## What DPGA Appears To Look For

Based on the official questionnaire, submission guide, toolkit, and registry examples, the answer should include:

1. Standards or practices that are actually used by the solution.
2. Short explanations of how each one is used.
3. Public evidence links: repository files, docs, specifications, model card, source contracts, security/support docs, CI, or external standard pages.
4. No broad claims unless the repo documents adherence.
5. Clear separation between:
   - technical/interoperability standards,
   - open-source project governance practices,
   - data/AI transparency practices,
   - security/privacy practices.

## Likely Candidates For Air For Tomorrow

These need agent verification against the repo before final submission.

| Candidate | Type | Why it may fit | Evidence to verify |
|---|---|---|---|
| H3 | Geospatial indexing standard / open-source grid system | Core spatial index for ingestion, feature engineering, prediction, and maps. | README, docs, source code, H3 docs. |
| Parquet | Open columnar data format | Processed source data, silver features, and predictions are parquet artifacts. | README, docs, pipeline output paths. |
| CSV | Open tabular data format | Static/supporting assets and some source inputs use CSV. | assets/docs/source contracts. |
| YAML | Open configuration format | Main config is YAML. | `config/config.yaml`. |
| JSON | Open data/model format | XGBoost model artifact is JSON; APIs may return JSON. | `src/models/xgboost_model.json`, docs. |
| GeoTIFF / NetCDF / GRIB | Geospatial/scientific data formats | Used in satellite/weather processing paths where applicable. | Himawari/ERA5 docs and code. |
| Docker / containerization | Deployment/reproducibility best practice | Expected execution environment and reproducible dependency setup. | README, Dockerfile, docs. |
| Git / Git LFS | Version-control and large-artifact management practice | Source control and large-data artifact policy. | README, CONTRIBUTING, `.gitattributes`. |
| Model card | AI transparency / responsible-use practice | Documents model purpose, intended use, limitations, evaluation, bias/risks, and citation. | `MODELCARD.MD`. |
| Dataset provenance/license inventory | Data governance practice | Documents third-party source URLs, terms, and attribution constraints. | `EXTERNAL_DATASETS_AND_LICENSES.md`. |
| Security reporting | Open-source security practice | Private vulnerability reporting and runtime credential guidance. | `SECURITY.md`, `SUPPORT.md`. |
| Contribution guidelines / code of conduct / PR templates | Community governance practice | Supports safe and maintainable public collaboration. | `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/`. |
| CI / automated tests | Quality practice | Evidence of regression checks and reproducibility. | `.github/workflows/`, scripts, tests/features. |
| Source contracts | Data engineering best practice | Documents source-specific contracts and failure modes. | `docs/SOURCE_CONTRACTS.md`. |

## Candidate Claims To Avoid Unless Added Or Verified

- Do not claim formal FAIR Data Principles adherence unless the repo explicitly maps to FAIR.
- Do not claim UNESCO AI ethics adherence unless the model card/docs explicitly map to those principles.
- Do not claim UNICEF Innovation Principles adherence unless we add a clear mapping or cite a project document.
- Do not claim ISO/OGC compliance unless code/docs show actual compliance.
- Do not claim DHIS2/FHIR/OpenAPI interoperability unless an implemented integration or documented interface exists. DHIS2 itself is well documented, but Air for Tomorrow's integration needs checking/validation before it is used as an interoperability claim.

## Comparable DPG Examples To Review

Use these as examples of how similar projects are described, not as copy sources:

| DPG | Why relevant | Notes |
|---|---|---|
| ClimWeb | Climate/environment software, data visualization, satellite imagery, CAP alerts, deployed across many countries. | Registry profile shows climate/environment positioning, languages, organizations using it, and that Open Standards & Best Practices is self-reported. |
| DiCRA | Climate-resilient agriculture, geospatial, data visualization, open datasets. | Useful comparison for geospatial climate data and policy-use framing. |
| GeoPrism Registry | Geospatial registry for health, education, agriculture, infrastructure, and services. | Useful comparison for geospatial standards, sharing, and public-sector users. |
| Ersilia Model Hub | Open-source AI/model platform. | Useful comparison for AI-system framing, model access, and model governance expectations. |
| Android FHIR SDK / Open Health Stack / DHIS2 | Health-sector interoperability examples. | Only relevant if DHIS2 or health-system integration is documented for Air for Tomorrow. |

## Sources Checked

- DPG Standard: https://new.digitalpublicgoods.net/standard
- DPG Standard questionnaire: https://raw.githubusercontent.com/DPGAlliance/DPG-Standard/main/standard-questions.md
- DPG Submission Guide: https://digitalpublicgoods.net/digital-public-goods/submission-guide/
- Featured Standards: https://new.digitalpublicgoods.net/toolkit/featured-standards
- Featured Best Practices: https://new.digitalpublicgoods.net/toolkit/featured-best-practices
- DPG Registry: https://www.digitalpublicgoods.net/registry
- ClimWeb profile: https://www.digitalpublicgoods.net/r/climweb-httpsclimtechafricaclimweb
- DiCRA profile: https://www.digitalpublicgoods.net/r/dicra
- GeoPrism Registry profile: https://www.digitalpublicgoods.net/r/geoprism-registry
- Ersilia Model Hub profile: https://www.digitalpublicgoods.net/r/ersilia-model-hub

## Implementation Plan Implication

Before finalizing the DPG answer, assign an agent to:

1. Read the official DPGA standards/best-practices resources.
2. Inspect 3-5 comparable DPG profiles and their linked repositories/docs.
3. Audit Air for Tomorrow docs/code for evidence of each candidate standard/practice.
4. Produce a short final answer with links and no unsupported claims.
5. Recommend small documentation improvements only where they close a clear DPG evidence gap.
