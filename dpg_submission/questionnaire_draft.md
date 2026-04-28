# Air for Tomorrow DPG Questionnaire Draft

Status: Draft for review
Last updated: 2026-04-28

This draft is mapped to the DPGA application questionnaire and uses repository evidence where available. Items marked `NEEDS OWNER INPUT` should be answered by someone authorised to represent the solution owner.

## General Information

| Field | Draft answer | Evidence / notes |
|---|---|---|
| Solution name | Air for Tomorrow | Confirmed as both the repository/software name and the wider programme name. |
| Aliases | Air for Tomorrow, Air4Tomorrow, A4T | Confirm preferred aliases before submission. |
| Solution category | Open Software + Open AI Model | Confirmed scope. The repository includes runnable software plus an XGBoost model artifact and model card. |
| Short description | Open-source AI toolkit for nearcasting PM2.5 air pollution at sub-1 km resolution, with a pretrained model for Laos and Thailand. | Based on README headline and model card. Tighten to match portal length limits. |
| Website | https://github.com/unicef/airfortomorrow | Project repository and documentation. |
| Alternate email address | jhanan@unicef.org | Provisional. Marked for review/follow-up before submission. |
| Source hosting | https://github.com/unicef/airfortomorrow | Public repository URL. |

## 1. SDG Relevance

| Question | Draft answer | Evidence / notes |
|---|---|---|
| Which SDGs are most relevant? | SDG 3: Good Health and Well-being; SDG 11: Sustainable Cities and Communities; SDG 13: Climate Action. | Confirmed: link the application to all three SDGs. |
| How is the solution relevant to each selected SDG? | Air for Tomorrow supports PM2.5 situational awareness where monitoring coverage is sparse. It helps governments, UNICEF offices, researchers, and partners anticipate air pollution episodes, communicate public-health risk, and plan mitigation. For SDG 3, it supports action on health risks from air pollution. For SDG 11, it supports monitoring and response to urban and regional air quality. For SDG 13, it helps observe fire, meteorological, and pollution patterns connected to climate and environmental shocks, supporting climate-informed preparedness and resilience. | Need map to exact SDG targets before final answer. Likely targets: 3.9, 11.6, 13.1. |

## 2. Open Licensing

| Question | Draft answer | Evidence / notes |
|---|---|---|
| Which open licenses are used? | GPL-3.0 for the software repository. Third-party datasets have separate source licenses and terms documented in the dataset inventory. | `LICENSE`, `README.md`, `EXTERNAL_DATASETS_AND_LICENSES.md`, `MODELCARD.MD`. |
| Evidence of selected licenses | Repository license file: https://github.com/unicef/airfortomorrow/blob/main/LICENSE. External data inventory: https://github.com/unicef/airfortomorrow/blob/main/EXTERNAL_DATASETS_AND_LICENSES.md. | Confirm branch/path before submission. |

## 3. Clear Ownership

| Question | Draft answer | Evidence / notes |
|---|---|---|
| Who owns this solution? | UNICEF. | Confirmed by project owner. |
| Evidence of ownership | Repository under UNICEF GitHub organisation; README/model card identify UNICEF teams and collaborators. Supporting impact/ownership context: UNICEF Office of Innovation story, "Addressing Air Pollution with Artificial Intelligence" (23 May 2025), https://www.unicef.org/innovation/stories/addressing-air-pollution-artificial-intelligence. Project repository and documentation: https://github.com/unicef/airfortomorrow. | Use both links in the final application evidence field where space allows. |
| Type of organisation | International organisation / UN agency. | Confirm exact option available in portal. |
| Owner location | Bangkok, Thailand. | Confirmed for this solution's owner office. |
| Do you own all code, content, and/or data? | UNICEF owns or has rights to redistribute the repository code and model artifacts. All project code is GPL-3.0 licensed. Third-party input datasets remain governed by their original licenses and terms, as documented in `EXTERNAL_DATASETS_AND_LICENSES.md`; the repository does not claim ownership of upstream datasets. | Confirm final wording before submission. |
| If not, right to redistribute? | Third-party dataset redistribution rights and attribution constraints are documented in `EXTERNAL_DATASETS_AND_LICENSES.md`; some sources are fetched at runtime using user credentials instead of being redistributed. | Final plan should include a link/provenance check against `EXTERNAL_DATASETS_AND_LICENSES.md`. |

## 4. Platform Independence

| Question | Draft answer | Evidence / notes |
|---|---|---|
| Core technologies | Python 3.10, Docker, XGBoost, Polars, NumPy, H3, GDAL/rasterio, SciPy, shell scripts, Git LFS, external public data APIs/feeds. | `README.md`, `Dockerfile`, `requirements.txt`. |
| Closed proprietary dependency? | No mandatory closed-source software dependency is required for the core Air for Tomorrow workflow. The repository is intended to be 100% open: it uses Docker, Python, open-source libraries, shell entrypoints, file-based artifacts, and documented source contracts. Live data collection depends on external data services/accounts for some sources, such as Himawari/JAXA, Copernicus CDS, and OpenAQ API credentials, but these are data-access dependencies rather than closed-source software components. | Confirmed from README, Dockerfile, requirements, `env_template`, `config/config.yaml`, docs, and external dataset inventory. |
| Replacement of closed components | The core workflow is organized around source-specific collectors and H3/date file contracts. Where an upstream live data service is unavailable or replaced, comparable open or licensed datasets can be integrated through source-specific adapters that produce the same processed/engineered artifacts. Intermediate and output artifacts are file-based, including processed source parquet, engineered silver feature tables, prediction parquet, map PNGs, YAML configuration, CSV supporting assets, and the pretrained model artifact. | This answer should emphasize intended open architecture while being transparent about external data-service accounts. |

## 5. Documentation

| Question | Draft answer | Evidence / notes |
|---|---|---|
| Where is documentation? | README, DOCUMENTATION, architecture/dataflow/source contracts docs, model card, external data license inventory, contributing/support/security files. | `README.md`, `DOCUMENTATION.md`, `docs/ARCHITECTURE.md`, `docs/DATAFLOW.md`, `docs/SOURCE_CONTRACTS.md`, `docs/RELIABILITY_AND_OPERATIONS.md`, `MODELCARD.MD`, `EXTERNAL_DATASETS_AND_LICENSES.md`. |
| Description of documentation | The repository documents installation with Docker, credentials, pipeline workflows, model features and limitations, source data contracts, architecture, dataflow, operations, contribution process, support, security reporting, and third-party data terms. | Need final public links after branch is published. |

## 6. Mechanism For Extracting Non-PII Data

| Question | Draft answer | Evidence / notes |
|---|---|---|
| Does the solution use or generate non-PII data/content? | Yes. | PM2.5 observations, satellite AOD, fire detections, weather, static geospatial features, predictions, maps. |
| Import/export mechanism | Air for Tomorrow imports source data from APIs, archives, FTP, and local files, harmonises them into H3/date engineered feature tables, and writes the actual working artifacts used by the model. Current outputs include processed source parquet files under `data/processed/`, engineered silver feature tables under `data/silver/`, daily prediction parquet files under `data/predictions/data/`, optional map PNG files under `data/predictions/map/`, YAML configuration, CSV static/supporting assets, and the pretrained XGBoost model artifact at `src/models/xgboost_model.json`. | Describe the current repo/model artifacts as-is. Do not add or imply a new export feature unless separately implemented. |

## 7. Privacy And Applicable Laws

| Question | Draft answer | Evidence / notes |
|---|---|---|
| Relevant laws | Draft basis: The repository is designed for environmental/geospatial data and does not collect personal data from end users. It should comply with applicable privacy requirements by avoiding PII collection and by using upstream public/environmental datasets under their governing terms. | Existing repo links may be sufficient, but this answer needs agent review before final submission. |
| Evidence of adherence | Candidate evidence: repository `SECURITY.md`, `SUPPORT.md`, `EXTERNAL_DATASETS_AND_LICENSES.md`, model card limitations/out-of-scope use, and README intended-use guidance. | Some guidance is already in the model card. Agent follow-up: read/analyze these links before deciding whether to cite additional UNICEF privacy, AI, data protection, or responsible-innovation policy links. |

## 8. Standards And Best Practices

| Question | Draft answer | Evidence / notes |
|---|---|---|
| Open standards adhered to | RESEARCH NEEDED. Candidate standards include H3, Parquet, CSV, YAML, JSON, GeoTIFF/NetCDF/GRIB where applicable, Docker/containerization, Git/Git LFS, and REST/API-based source access where applicable. | See `dpg_submission/standards_best_practices_research.md`. Final answer must be evidence-backed and should compare similar DPG profiles before submission. |
| Best practices adhered to | RESEARCH NEEDED. Candidate practices include open-source repository governance, code of conduct, contribution guidelines, issue and PR templates, vulnerability reporting, dependency management, reproducible Docker runtime, CI/test workflows, source contracts, model card, external data license inventory, and clear intended-use/limitations. | Do not claim FAIR, UNESCO AI ethics, UNICEF Innovation Principles, ISO, OGC, DHIS2/FHIR, or other frameworks unless repository evidence supports them or docs are updated. |

## 9A. Data Privacy And Security

| Question | Draft answer | Evidence / notes |
|---|---|---|
| Does the solution allow PII collection/storage/distribution? | PII is not collected, stored, or distributed by the core Air for Tomorrow pipeline. | Confirmed by project owner. |
| Types of PII | Not applicable. | No PII collected. |
| Privacy and security measures | The system uses environmental and geospatial data rather than individual records; credentials are provided at runtime via environment configuration; `.env` files are git-ignored; public security reporting is documented; third-party source terms are inventoried. | Need decide whether to include recent secret-scan evidence in pack. |

## 9B. Inappropriate, Misleading, And Illegal Content

| Question | Draft answer | Evidence / notes |
|---|---|---|
| Does the solution collect/store/distribute content? | The core pipeline does not collect, host, or distribute user-generated content. It stores environmental data, model outputs, engineered datasets, generated maps, documentation, and model artifacts. Raw sensor inputs are environmental sensor readings from OpenAQ and AirGradient, not personal data or user-generated content. | Confirmed: no PII and no UGC. |
| Types of content | Project documentation, generated maps/charts, engineered datasets, prediction outputs, and model artifacts. Raw sensor data are environmental readings from OpenAQ and AirGradient. No user-generated social/content moderation surface is included. | Confirm final wording before submission. |
| Handling inappropriate/misleading/illegal content | The repository does not provide an interaction or content-hosting platform. Misleading use is addressed primarily through `MODELCARD.MD`, including intended use, out-of-scope use, risks, limitations, and recommendations. Support and security channels provide reporting routes for issues. | Refer to the model card for this answer. Also complete a responsible-AI risks/harms/benefits follow-up before final submission. If review finds a gap, improve the model card rather than creating a separate policy artifact by default. |

## 9C. Protection From Harassment

| Question | Draft answer | Evidence / notes |
|---|---|---|
| Does the solution enable user/contributor interaction? | Yes, through open-source contribution channels such as GitHub issues and pull requests. The core software itself does not include end-user interaction features. | Repository community surface only. |
| Protection mechanisms | The repository includes a code of conduct, contribution guidelines, issue templates, PR template, support guidance, and security reporting instructions. GitHub moderation and UNICEF maintainer review apply to repository interactions. | Evidence: `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SUPPORT.md`, `SECURITY.md`, `.github/ISSUE_TEMPLATE/`, `.github/pull_request_template.md`. |

## Scale Of Solution

| Question | Draft answer | Evidence / notes |
|---|---|---|
| Active deployments | Laos and Thailand. The current pretrained model is designed and implemented for PM2.5 nearcasting across Laos and Thailand. The underlying data engineering workflows are designed for broader adaptation where suitable source data are available, but use outside Laos and Thailand requires local data, calibration/retraining, and validation. The UNICEF Office of Innovation story provides supporting context for the broader Lao PDR air-quality initiative and AI-supported pollution analysis. | Confirm exact deployment dates, operational cadence, and public naming of partners before final submission. Follow the model card and documentation. Do not over-emphasise sensors; they are supporting data infrastructure/training data for the AI model, not the core product. |
| Other users | UNICEF Lao PDR; UNICEF East Asia and Pacific Regional Office; Lao PDR Ministry of Education and Sports; Lao PDR Ministry of Agriculture and Environment (MAE), including the Natural Resources and Environment Research Institute (NRERI) / Environmental Laboratory; Lao PDR Ministry of Health for possible DHIS2 integration context. | Partner list supplied by project owner. All government partner names and descriptions need further research / future review before submission. DHIS2 integration details need checking/validation before citation. MAE/NRERI naming should be reviewed against `dpg_submission/partner_citations.md`. |
| Multilingual/regional support | The data engineering workflows are designed for broader geographic adaptation where suitable source data are available. The existing pretrained model is for Laos and Thailand only; use in other regions requires local data, calibration/retraining, and validation. Documentation is provided in English only. | Confirm final wording against `MODELCARD.MD` and repository documentation before submission. |
| Available languages | English. | Documentation is provided in English only. |
| Programs/initiatives | Air for Tomorrow is both the repository/software name and the wider programme name. The UNICEF Office of Innovation story provides public context for how the programme is being used in the broader air-quality initiative. | Use the UNICEF blog post as the primary public reference; do not invent a separate programme label unless a specific portal option requires it. |
| Highlights / learn more | UNICEF Office of Innovation story: https://www.unicef.org/innovation/stories/addressing-air-pollution-artificial-intelligence. Project repository and documentation: https://github.com/unicef/airfortomorrow. Partner naming notes: `dpg_submission/partner_citations.md`. | Add example maps, paper/manuscript, or release URLs if public before submission. |
