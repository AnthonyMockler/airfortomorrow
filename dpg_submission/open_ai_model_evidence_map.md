# Open AI Model Evidence Map

Status: Draft for DPG submission review
Last updated: 2026-04-30

This note maps Air for Tomorrow's current repository evidence against the DPGA's Open AI System / Open AI Model expectations. It separates evidence that can be cited now from items that need additional writing, legal review, or repository documentation before final submission.

## DPGA Reference Baseline

The DPGA's AI systems guidance says an AI system submission must provide three open components:

| Component | DPGA expectation | Current Air for Tomorrow status |
|---|---|---|
| Data | Dataset(s) used to train, validate, and test the system, under Open Definition-conformant licenses. | Partial. Sources and terms are inventoried, but every training/validation/test source needs a final Open Definition/conformant-license review. |
| Code | Code used for data preprocessing, training, validation, testing, inference, supporting libraries, and tools, under OSI-approved licenses. | Partial to strong. Preprocessing and inference code are in `src/` and scripts; model training/evaluation is documented in a notebook and model card, but should be treated as a submission review item. |
| Model | Model architecture/type/structure and model parameters, weights, coefficients, optimizers, or hyperparameters under acceptable open terms. | Strong for the deployed XGBoost artifact and model card; needs final confirmation that the model artifact/license wording is explicit enough for DPG review. |

DPGA also asks AI submissions to document model overview, intended use, performance metrics, limitations, data overview, technical data details, data composition, collection/preprocessing, and responsible AI considerations such as proportionality, bias/fairness, risks/harms, mitigations, and transparency.

References:
- DPGA, "AI systems as digital public goods" (21 May 2025): https://new.digitalpublicgoods.net/blog/ai-systems-as-dpgs
- DPGA, "How the DPG Standard and the Universal DPI Safeguards Framework are Charting a Safe and Inclusive Digital Future" (12 January 2026): https://new.digitalpublicgoods.net/blog/dpg-standard-universal-dpi-safeguards-safe-inclusive-digital-future

## Evidence We Can Cite Now

| DPGA AI documentation item | Current repository evidence | Assessment |
|---|---|---|
| Model overview | `MODELCARD.MD` describes the PM2.5 XGBoost regressor, countries, H3 grid, data sources, developer, funder, license, and intended operational purpose. See `MODELCARD.MD` sections "Model Details" and "Model Description". | Covered. |
| Intended use and users | `MODELCARD.MD` covers direct use, downstream use, and out-of-scope use. It names government agencies, health organizations, NGOs, researchers, UNICEF country offices, and partners as intended users. | Covered. |
| Out-of-scope applications | `MODELCARD.MD` excludes unsupported regions without retraining, other pollutants/indoor air, long-term forecasting, sole-use regulatory enforcement, and individual medical advice. | Covered. |
| Model type / architecture | `MODELCARD.MD` states that the architecture is gradient boosted decision trees using XGBoost, with `reg:squarederror` objective. | Covered. |
| Model artifact | `MODELCARD.MD` and `README.md` identify `src/models/xgboost_model.json` as the deployed pretrained model artifact. | Covered. |
| Feature schema | `MODELCARD.MD` lists the exact 21 numeric features expected by the deployed model. `README.md` and `DOCUMENTATION.md` also describe the feature families. | Covered. |
| Training data sources | `MODELCARD.MD` lists target PM2.5 from OpenAQ/AirGradient, Himawari AOD, NASA FIRMS, ERA5, WorldPop, and temporal/context features. `EXTERNAL_DATASETS_AND_LICENSES.md` is the canonical source/terms inventory. | Covered as a source inventory; license conformance still needs review. |
| Training/validation split | `MODELCARD.MD` documents a date-based split: train before 2025-01-01, validation from 2025-01-01 to 2025-10-30, with `<250 µg/m³` filtering in the baseline evaluation setup. | Covered, but wording should clarify whether this validation hold-out is the only test/evaluation split. |
| Training procedure | `MODELCARD.MD` documents `XGBRegressor(random_state=42, objective='reg:squarederror')`, `log1p(pm25_value)`, high-pollution sample weighting, and Float32 matrices. The exploration notebook contains the runnable training/evaluation workflow. | Mostly covered; consider making the notebook or a short training reproducibility note canonical for DPG review. |
| Preprocessing | `MODELCARD.MD`, `docs/DATAFLOW.md`, `docs/ARCHITECTURE.md`, `docs/SOURCE_CONTRACTS.md`, and `src/make_silver.py` document H3/date harmonization, AOD IDW interpolation, ERA5 upsampling, rolling features, source aggregation, null fire handling, and parent-H3 PM2.5 context. | Covered. |
| Performance metrics | `MODELCARD.MD` reports MAE, RMSE, R², Pearson correlation, mean bias, category agreement, country-level results, concentration-bin results, and validation row counts. `README.md` summarizes model performance. | Covered. |
| Known limitations and biases | `MODELCARD.MD` covers spatial sensor bias, temporal bias, satellite/cloud limitations, weather/seasonal shifts, fire-detection limitations, lack of prediction intervals, and misuse risk. | Covered. |
| Mitigations and recommendations | `MODELCARD.MD` recommends comparing against ground truth, communicating uncertainty, retraining regularly, cautious regional extension, bias monitoring, and transparent documentation of updates. | Covered. |
| Explainability / transparency | `MODELCARD.MD` summarizes SHAP/model examination findings and identifies AOD, fire intensity, meteorology, spatial context, month, and WorldPop as important contributors. | Covered at summary level; detailed SHAP artifacts are in the notebook workflow rather than a polished public report. |
| Open software license | `LICENSE` and `MODELCARD.MD` state GPL-3.0 for the project/model repository. | Covered. |

## Gaps That Need More Writing Or Review

These are the highest-priority items before final DPG submission:

1. **Training/validation/test data openness review.** DPGA's AI guidance says the datasets used to train, validate, and test the system must be open and available under Open Definition-conformant licenses. `EXTERNAL_DATASETS_AND_LICENSES.md` identifies the source terms, but the DPG pack still needs a source-by-source conformance review for the actual training/evaluation data. Pay particular attention to OpenAQ's per-record upstream licenses, JAXA P-Tree terms, Copernicus/ECMWF terms, and any derived/static assets.

2. **Dataset card or dataset summary.** The model card lists sources and features, but DPG review would be stronger with a compact dataset summary that names `data/training/silver_dataset.parquet`, its version/date, creator/maintainer, coverage, row/field schema, target variable, split logic, and known data-quality limitations.

3. **Clarify test/evaluation terminology.** The model card uses a train/validation date split and reports hold-out validation results. The DPG AI component language refers to train, validate, and test datasets. The final submission should say whether the validation window is the held-out test/evaluation set, or whether a separate test set exists.

4. **Training and evaluation reproducibility.** The notebook `notebooks/air_quality_pipeline_walkthrough.ipynb` contains the model training and evaluation workflow. For submission, confirm whether this notebook is the canonical training/validation/testing code, or add a short reproducibility note pointing to the exact notebook cells/configuration and the expected input artifact.

5. **Model version/date/contact details.** The model card names developer/funder/license and includes evaluation rerun date, but it does not present a compact model version, release date, and contact field in the DPGA checklist form. Add those either to `MODELCARD.MD` or to the final questionnaire answer.

6. **Responsible AI assessment record.** The model card covers risks, limitations, recommendations, and performance differences. A structured risks/harms/benefits assessment is still listed as follow-up in `dpg_submission/responsible_ai_assessment_followup.md`; completing it would strengthen the proportionality, bias/fairness, risks/harms, mitigations, and transparency evidence.

7. **Monitoring and update process.** The model card recommends retraining, bias monitoring, and documenting updates, but the repository does not yet have a concise operational policy describing who reviews model issues, when retraining is considered, and how users report model performance concerns.

## Suggested New Or Updated Documents

Minimum path before submission:

1. Add a short section to `MODELCARD.MD` titled "Version, Data, and Review Metadata" with model version/release date/contact and a pointer to the dataset summary.
2. Create `docs/TRAINING_DATASET_CARD.md` or `dpg_submission/training_dataset_summary.md` covering dataset identity, provenance, schema, splits, and license conformance.
3. Update `dpg_submission/questionnaire_draft.md` with a concise Open AI Model answer that cites this evidence map, `MODELCARD.MD`, `EXTERNAL_DATASETS_AND_LICENSES.md`, `notebooks/air_quality_pipeline_walkthrough.ipynb`, and `src/models/xgboost_model.json`.
4. Complete `dpg_submission/responsible_ai_assessment_followup.md` or convert it into a completed assessment note.

Optional but useful:

1. Add a short `docs/MODEL_GOVERNANCE.md` describing monitoring, feedback, issue triage, retraining triggers, and model update documentation.
2. Add a scripted training/evaluation entrypoint if the notebook is not considered sufficient canonical code for DPG review.
