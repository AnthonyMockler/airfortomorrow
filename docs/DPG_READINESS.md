# Digital Public Goods Readiness

Air for Tomorrow is being prepared for Digital Public Goods Alliance submission as Open Software + Open AI Model. This page summarizes public evidence for the DPG Standard and links to canonical repository documentation.

This page is descriptive and does not replace the full DPG application.

## Scope

Air for Tomorrow is an open-source AI toolkit for PM2.5 nearcasting. The repository includes a runnable data engineering and prediction pipeline, a pretrained XGBoost model for Laos and Thailand, source-specific collection and processing workflows, documentation, and model governance material.

The data engineering workflow is designed for broader geographic adaptation where suitable source data are available. The pretrained model is scoped to Laos and Thailand; use in other regions requires local data, calibration or retraining, and validation.

## Evidence Summary

| DPG area | Current evidence |
|---|---|
| Category | Open Software + Open AI Model |
| Owner | UNICEF |
| Primary repository | https://github.com/unicef/airfortomorrow |
| License | GPL-3.0 for project code; third-party datasets governed by documented upstream terms |
| Model scope | Pretrained model for Laos and Thailand |
| Documentation language | English |
| PII / UGC | No PII collection and no user-generated content surface in the core pipeline |

## 1. SDG Relevance

**Summary:** Air for Tomorrow supports SDG 3, SDG 11, and SDG 13 by improving PM2.5 situational awareness where monitoring coverage is sparse. It helps public-health, education, environment, and research actors understand air-pollution exposure, support planning, and improve climate-informed preparedness.

**Evidence:**
- [README](../README.md)
- [Model card](../MODELCARD.MD)
- [UNICEF Office of Innovation story](https://www.unicef.org/innovation/stories/addressing-air-pollution-artificial-intelligence)
- [UNICEF East Asia and Pacific article](https://www.unicef.org/eap/protecting-children-air-pollution-open-source-air-quality-machine-learning-se-asia)

**Scope notes:** The strongest SDG target links are expected to be SDG 3.9, SDG 11.6, and SDG 13.1.

## 2. Open Licensing

**Summary:** Project code is licensed under GPL-3.0. External datasets are governed by their original licenses or terms, which are documented in the repository's dataset inventory.

**Evidence:**
- [LICENSE](../LICENSE)
- [External datasets and licenses](../EXTERNAL_DATASETS_AND_LICENSES.md)
- [Model card](../MODELCARD.MD)

**Scope notes:** The repository does not claim ownership of upstream datasets. Operators must follow source-specific attribution, credential, access, and redistribution terms.

## 3. Clear Ownership

**Summary:** Air for Tomorrow is owned by UNICEF. The repository is hosted under the UNICEF GitHub organization, and the README and model card identify UNICEF teams and collaborators.

**Evidence:**
- [Repository](https://github.com/unicef/airfortomorrow)
- [README](../README.md)
- [Model card](../MODELCARD.MD)
- [UNICEF Office of Innovation story](https://www.unicef.org/innovation/stories/addressing-air-pollution-artificial-intelligence)

**Scope notes:** Public partner wording should use approved names and public sources in the final DPG application.

## 4. Platform Independence

**Summary:** The core workflow has no mandatory closed-source software dependency. It uses Docker, Python, open-source Python libraries, shell entrypoints, file-based artifacts, and documented source contracts. Some live data collection paths require external data-service accounts or credentials, such as Himawari/JAXA, Copernicus CDS, and OpenAQ; these are data-access dependencies rather than closed-source software components.

**Evidence:**
- [README quick start](../README.md#-quick-start)
- [Dockerfile](../Dockerfile)
- [requirements.txt](../requirements.txt)
- [env_template](../env_template)
- [Source contracts](SOURCE_CONTRACTS.md)
- [Reliability and operations](RELIABILITY_AND_OPERATIONS.md)
- [External datasets and licenses](../EXTERNAL_DATASETS_AND_LICENSES.md)

**Scope notes:** The source-specific collector design and H3/date contracts support replacement or adaptation of upstream data sources when equivalent open or licensed inputs are available.

## 5. Documentation

**Summary:** The repository includes installation, configuration, workflow, architecture, dataflow, source-contract, operations, contribution, support, security, licensing, and model-card documentation.

**Evidence:**
- [README](../README.md)
- [Documentation](../DOCUMENTATION.md)
- [Architecture](ARCHITECTURE.md)
- [Dataflow](DATAFLOW.md)
- [Source contracts](SOURCE_CONTRACTS.md)
- [Reliability and operations](RELIABILITY_AND_OPERATIONS.md)
- [Model card](../MODELCARD.MD)
- [External datasets and licenses](../EXTERNAL_DATASETS_AND_LICENSES.md)
- [Contributing](../CONTRIBUTING.md)
- [Support](../SUPPORT.md)
- [Security](../SECURITY.md)
- [Code of conduct](../CODE_OF_CONDUCT.md)

**Scope notes:** Documentation is provided in English.

## 6. Non-PII Data Extraction

**Summary:** The solution imports environmental and geospatial data, harmonizes those sources into H3/date engineered feature tables, and writes the artifacts used by the model. Current artifacts include processed source parquet files, engineered silver feature tables, prediction parquet files, optional PNG maps, YAML configuration, CSV static/supporting assets, and the pretrained XGBoost model artifact.

**Evidence:**
- [README expected outputs](../README.md#5-verify-expected-outputs)
- [Project structure](../README.md#-project-structure)
- [Dataflow](DATAFLOW.md)
- [Documentation](../DOCUMENTATION.md)
- [Model card feature schema](../MODELCARD.MD)

**Scope notes:** The core artifacts are model and pipeline artifacts, not personal or user-generated records.

## 7. Privacy And Applicable Laws

**Summary:** The core Air for Tomorrow pipeline does not collect, store, or distribute PII. It processes environmental sensor readings, satellite observations, fire detections, meteorological inputs, static geospatial features, engineered datasets, prediction outputs, maps, and model artifacts. Credentials are supplied by operators at runtime and `.env` files are excluded from source control.

**Evidence:**
- [Security policy](../SECURITY.md)
- [Support routing](../SUPPORT.md)
- [External datasets and licenses](../EXTERNAL_DATASETS_AND_LICENSES.md)
- [Model card limitations and recommendations](../MODELCARD.MD)
- [README intended use and limitations](../README.md#-intended-use-and-limitations)

**Scope notes:** Raw sensor inputs from OpenAQ and AirGradient are environmental readings, not PII or user-generated content.

## 8. Standards And Best Practices

**Summary:** Air for Tomorrow uses a focused set of open standards and practices that are visible in the repository. These include H3 for geospatial indexing, open data/file formats such as Parquet, CSV, YAML, JSON, GeoTIFF, NetCDF, and GRIB where applicable, Docker containerization, Git/Git LFS, source contracts, open-source community governance files, security reporting, CI/test workflows, dataset provenance documentation, and a model card.

**Evidence:**
- [README architecture and outputs](../README.md)
- [Dockerfile](../Dockerfile)
- [requirements.txt](../requirements.txt)
- [Git attributes](../.gitattributes)
- [Source contracts](SOURCE_CONTRACTS.md)
- [GitHub workflows](../.github/workflows)
- [Contributing](../CONTRIBUTING.md)
- [Code of conduct](../CODE_OF_CONDUCT.md)
- [Security policy](../SECURITY.md)
- [Model card](../MODELCARD.MD)
- [External datasets and licenses](../EXTERNAL_DATASETS_AND_LICENSES.md)
- [DPGA featured standards](https://new.digitalpublicgoods.net/toolkit/featured-standards)
- [DPGA featured best practices](https://new.digitalpublicgoods.net/toolkit/featured-best-practices)

**Scope notes:** The project should not claim formal adherence to FAIR, UNESCO AI ethics, UNICEF Innovation Principles, OGC, ISO, DHIS2/FHIR, or OpenAPI unless repository evidence is added for those claims.

## 9. Do No Harm

**Summary:** Air for Tomorrow does not provide a user-generated content platform. Misleading or harmful use risks are addressed primarily through the model card, which documents intended use, out-of-scope use, risks, limitations, evaluation caveats, and recommendations. Repository interaction is governed through contribution, support, security, and code-of-conduct processes.

**Evidence:**
- [Model card](../MODELCARD.MD)
- [README intended use and limitations](../README.md#-intended-use-and-limitations)
- [Support](../SUPPORT.md)
- [Security](../SECURITY.md)
- [Code of conduct](../CODE_OF_CONDUCT.md)
- [Contributing](../CONTRIBUTING.md)

**Scope notes:** Outputs are model-based estimates and should be combined with local monitoring and official advisories for high-stakes decisions.

## Scale And Deployment

**Summary:** Air for Tomorrow is active for Laos and Thailand. The current pretrained model covers those countries, and the wider Air for Tomorrow programme is documented by UNICEF public communications.

**Evidence:**
- [README coverage](../README.md#-performance-metrics)
- [Model card](../MODELCARD.MD)
- [UNICEF Office of Innovation story](https://www.unicef.org/innovation/stories/addressing-air-pollution-artificial-intelligence)
- [UNICEF East Asia and Pacific article](https://www.unicef.org/eap/protecting-children-air-pollution-open-source-air-quality-machine-learning-se-asia)

**Scope notes:** Sensors are supporting data infrastructure and training/validation data for the AI model; they are not the core DPG product.

## Review Notes

Before final submission, confirm final public wording for government partners, deployment dates and operational cadence, and any health-system integration claims. Do not cite DHIS2 interoperability unless repository or public deployment evidence supports the claim.
