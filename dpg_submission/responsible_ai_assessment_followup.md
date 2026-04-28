# Responsible AI Assessment Follow-Up

Status: Follow-up needed
Last updated: 2026-04-28

Air for Tomorrow is being submitted as Open Software + Open AI Model. Before final DPG submission, complete a structured risks/harms/benefits review and reconcile the findings with the existing model card.

## Recommended Assessment Path

1. Review the existing `MODELCARD.MD`.
   - Intended use
   - Out-of-scope use
   - Bias, risks, and limitations
   - Recommendations
   - Evaluation and performance caveats

2. Complete or adapt a risks/harms/benefits assessment.
   - Start with UN Global Pulse's Risks, Harms and Benefits Assessment Tool if it is still the right UN template.
   - If UNICEF has a more specific required template for AI systems, use that instead or in addition.

3. Review UNICEF AI guidance.
   - UNICEF Innocenti's "Guidance on AI and children" should be checked because Air for Tomorrow is child/public-health oriented, even though it does not collect PII or interact directly with children.
   - The assessment should identify whether child-rights considerations are already covered by the model card or need additional wording.

4. Update the evidence.
   - If the model card already covers the assessment outcomes, cite the model card in the DPG answer.
   - If gaps are found, improve `MODELCARD.MD` first rather than creating a separate policy artifact by default.
   - Keep any internal worksheet in `dpg_submission/` if it is useful for application preparation.

## Official Resources To Check

| Resource | Why it matters | URL |
|---|---|---|
| UN Global Pulse Risks, Harms and Benefits Assessment Tool | Structured privacy/ethics/data-protection review for data innovation projects. | https://www.unglobalpulse.org/wp-content/uploads/2023/12/UN-Global-Pulse_PrivacyAssessmentTool_2020.pdf |
| UNICEF Innocenti Guidance on AI and Children | UNICEF-specific child-centred AI policy guidance, including safety, privacy, fairness, transparency, accountability, inclusion, and child rights. | https://www.unicef.org/innocenti/reports/policy-guidance-ai-children |
| UNICEF AI for Children project | UNICEF project page on placing child rights at the heart of AI governance and practice. | https://www.unicef.org/innocenti/projects/ai-for-children |
| UNICEF Digital Impact AI for children page | Public UNICEF overview of responsible AI for children and young people. | https://www.unicef.org/digitalimpact/what-we-do/artificial-intelligence-children |

## Assessment Questions To Answer

1. What benefits does the AI model create for children, communities, policymakers, and public-health/environmental actors?
2. What foreseeable harms could result from incorrect, stale, overconfident, or out-of-scope PM2.5 predictions?
3. How does the model card communicate uncertainty, limitations, and out-of-scope use?
4. What bias risks exist due to sensor distribution, seasonality, geography, satellite gaps, or fire/weather inputs?
5. What human oversight or validation is recommended before high-stakes decisions?
6. Does the system avoid PII and user-generated content as currently documented?
7. Does deployment require any special safeguards when outputs are used by child-facing programmes, schools, or government partners?
8. Are the current documentation and model-card warnings enough for DPG review, or should the model card be improved?
