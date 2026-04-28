# Standards And Best Practices Research Follow-Up

Status: Researched draft
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

The DPGA featured standards page groups standards across interoperability, data exchange, sector-specific, security, and general formats. Relevant examples for this project include REST, CSV, GeoJSON, GeoTIFF, JSON, UTF-8, XML, and YAML. The DPGA featured best-practices page groups practices across community, interoperability, lifecycle management, testing, security/privacy, system architecture, usability, and other governance frameworks.

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

## Comparable DPG Review Findings

| DPG | Category / components | Standards and practices pattern | Privacy / do-no-harm pattern | Scale pattern | Useful lesson for Air for Tomorrow |
|---|---|---|---|---|---|
| ClimWeb | Software; one assessed GitHub repository; climate/environment web platform. | Registry profile lists the assessed repository and leaves Open Standards & Best Practices as self-reported. | Privacy, security, and inappropriate-content indicators are self-reported. | Describes deployment across 30 countries, available languages, and organizations using it. | Keep a concise climate/environment description and clearly identify the assessed repository and countries. |
| DiCRA | Software; geospatial climate-resilient agriculture platform; one assessed GitHub repository. | Registry profile emphasizes open access to geospatial datasets and evidence-driven policy. | Privacy and inappropriate-content indicators are self-reported, while open licenses/docs/non-PII data extraction are verified. | Lists participating programme, available language, and organizations using it. | Describe policy-support value while keeping standards claims tied to repo evidence. |
| GeoPrism Registry | Software; geospatial registry; one assessed GitHub repository. | Profile highlights geospatial and data-collection features; Open Standards & Best Practices is self-reported. | Privacy, security, inappropriate-content, and harassment sections are self-reported. | Lists public-sector users, including Lao PDR Ministry of Health. | Cite geospatial evidence and public-sector use carefully, but avoid unsupported health interoperability claims. |
| Ersilia Model Hub | Software; open-source AI/model platform; one assessed GitHub repository. | Profile positions the product as an open-source model platform and identifies assessed components. | Governance indicators are largely self-reported except license, ownership, docs, and non-PII extraction. | Scale fields can be "N/A" where not applicable. | Be explicit that Air for Tomorrow is Open Software + Open AI Model and identify `src/models/xgboost_model.json` and `MODELCARD.MD`. |

## Final Candidate Claim Set

### Technical And Data Standards

- H3 geospatial indexing is used as the common spatial grid for ingestion, feature engineering, prediction, and map outputs.
- Parquet is used for processed source data, engineered silver feature tables, and prediction outputs.
- CSV is used for static/supporting assets and some source material.
- YAML is used for repository configuration.
- JSON is used for the pretrained XGBoost model artifact and API-style source data where applicable.
- GeoTIFF, NetCDF, and GRIB are used where applicable in satellite and meteorological processing paths.
- REST/API and FTP-style source access are used for external data collection where upstream sources expose those interfaces.

### Open-Source Governance Practices

- GPL-3.0 licensing.
- Public repository under the UNICEF GitHub organization.
- Contribution guidelines.
- Code of conduct.
- Issue templates and pull request template.
- Git/Git LFS large-artifact policy.
- Changelog and release process documentation.

### Data And AI Transparency Practices

- Model card covering intended use, out-of-scope use, limitations, bias/risks, recommendations, evaluation, feature schema, and citation.
- External dataset and license inventory with source URLs, terms, and attribution/redistribution notes.
- Source contracts documenting source-specific expectations and failure modes.
- README and documentation pages that describe architecture, dataflow, outputs, and limitations.

### Security And Operational Practices

- Runtime credentials via `.env`, with `.env` git-ignored.
- Security policy with private vulnerability reporting.
- Support routing that separates usage, bug, and security reports.
- Dockerized runtime for reproducible setup.
- CI workflows for tests and notebook hygiene.
- Scripted test and Behave harnesses documented in repository instructions.

## Final Draft Answer

Air for Tomorrow follows standards and practices in four areas:

1. Technical and data interoperability: H3 for geospatial indexing; Parquet, CSV, YAML, JSON, GeoTIFF, NetCDF, and GRIB where applicable; REST/API and FTP-style access for upstream data services.
2. Open-source governance: GPL-3.0 licensing, Git/Git LFS, contribution guidelines, code of conduct, issue and PR templates, changelog, and release documentation.
3. Data and AI transparency: model card, exact model feature schema, evaluation metrics, limitations, external dataset/license inventory, and source contracts.
4. Security and operations: Dockerized runtime, `.env` runtime credentials, private vulnerability reporting, support routing, CI workflows, and documented operations guidance.

Do not claim formal adherence to FAIR, UNESCO AI ethics, UNICEF Innovation Principles, OGC, ISO, DHIS2/FHIR, or OpenAPI in the DPG application unless supporting documentation is added.

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
