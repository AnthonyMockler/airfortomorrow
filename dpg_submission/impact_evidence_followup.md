# Impact Evidence Follow-Up

Status: Follow-up needed
Last updated: 2026-04-28

The DPG application does not need to prove causal health outcomes, but it should provide credible, verifiable evidence of SDG relevance, deployment, users/adopters, and public highlights. Quantified impact evidence will strengthen the application.

Positioning note: do not over-emphasise the sensor installation component. Sensors are supporting data infrastructure and training/validation data for the Air for Tomorrow AI model. The core DPG submission should focus on the open-source software, pretrained AI model, documentation, reproducible workflow, and PM2.5 nearcasting outputs.

## Evidence To Collect

| Evidence type | Data to collect | Notes |
|---|---|---|
| Deployment evidence | Countries active, deployment dates, provinces/regions, model/output coverage, operational cadence, implementing partners. | Sensor counts can be used only as supporting context where helpful; do not frame sensors as the main product. |
| Usage evidence | UNICEF offices, government teams, schools, researchers, dashboards, reports, maps, daily workflows, or briefings using the outputs. | Clarify which users may be named publicly. |
| Decision/action evidence | Examples where outputs informed awareness, advisories, planning, workshops, community engagement, or resource allocation. | Stronger than generic usage claims. |
| Outcome evidence | People reached, children/schools/communities covered, improvements in awareness, monitoring coverage, data accessibility, or response time. | Avoid claiming reduced pollution or health improvements unless directly measured. |
| Technical impact evidence | Spatial coverage, model performance metrics, prediction/map output volume, sensor-sparse coverage benefit, reproducible public workflow. | Existing model card and README provide a strong base. |

## Minimum Packet For Submission

- Countries active: Laos and Thailand.
- Implementation facts: model/output coverage, operational cadence, deployment period, partners, and only secondary context on sensors or sites where useful.
- Users/adopters: UNICEF teams, ministries, schools, researchers, or public platforms that can be named.
- Outputs: processed source parquet files, engineered silver feature tables, daily prediction parquet files, optional PNG maps, YAML configuration, CSV static/supporting assets, pretrained XGBoost model artifact, and any public reports/dashboards if available.
- Scale: children, schools, communities, or geographic areas reached, if available.
- Public links: UNICEF blog post, GitHub repository, dashboards, articles, papers, or releases.
- Model evidence: model-card metrics, intended use, limitations, and known risks.

## Open Questions

1. What are the confirmed deployment dates and operational cadence in Laos and Thailand?
2. Which Laos and Thailand government partners may be named publicly?
3. Are there public dashboards or generated maps that should be linked?
4. How many schools, provinces, communities, or children are covered by the current deployment?
5. Are there documented examples of decisions or actions informed by Air for Tomorrow outputs?
6. Are there usage logs or run counts for prediction/map generation?
7. Agent follow-up: read and analyze the repo's existing security, support, model-card, source-license, and README limitation links before deciding whether additional public privacy, AI, data-protection, or responsible-innovation policy links are needed.
