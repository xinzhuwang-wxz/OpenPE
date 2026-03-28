# Reasoning and Synthesis Verification Protocol (RSVP) Definition

## 2. Layer II: Reasoning and Synthesis Verification (RSVP)

The RSVP is the accountability layer designed to eliminate **logical hallucinations** (false causality, unsupported inferences) by mandating the explicit labeling and auditability of all complex statements that combine or interpret atomic facts.

### 2.1. Core Marker: Reasoning Marker (RM)

The RM is embedded immediately following a synthesized conclusion. It explicitly links the conclusion to the specific verified facts (premises) used to derive it.

$$\text{RM} = ( \text{RELATION\_ID} : \text{TYPE} : \text{DEP\_ID}_1, \text{DEP\_ID}_2, \ldots )$$

| Component       | Format                                               | Description                                                                                                                     |
| :-------------- | :--------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------ |
| **RELATION_ID** | `R1, R2, R3, ...`                                    | A unique, sequential identifier for the specific logical relationship or synthesis within the document.                         |
| **TYPE**        | `CAUSAL, SUMMARY, COMPARISON, INFERENCE, PREDICTION` | The defined type of logical operation performed by the AI agent.                                                                |
| **DEP_IDs**     | `C1, C2, C3`                                         | A comma-separated list of **CLAIM_IDs** (derived from the UGVP's IGMs) that serve as the verified premises for this conclusion. |

### 2.2. Verifiable Relationship Types

The RSVP mandates verification for the following core types of reasoning:

| $\text{TYPE}$  | Definition                                                                              | Verification Requirement                                                                                                                              |
| :------------- | :-------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------- |
| **CAUSAL**     | Assertion that A led to B or A influenced B.                                            | Must be supported by a verified source that explicitly states the causality, OR a highly-validated, auditable **LOGIC_MODEL** demonstrating the link. |
| **INFERENCE**  | A logical deduction (e.g., if A is true and A $\rightarrow$ B is true, then B is true). | The logical steps and the premises ($\text{DEP\_IDs}$) must be verifiable against formal logic rules.                                                 |
| **SUMMARY**    | A conclusion or generalization derived from multiple facts.                             | The conclusion must be **statistically representative** and **not contradicted** by any of the premises ($\text{DEP\_IDs}$).                          |
| **COMPARISON** | A definitive statement about differences or similarities.                               | The comparison metric must be explicitly cited or mathematically derived from the verifiable data in the $\text{DEP\_IDs}$.                           |

### 2.3. Reasoning Audit Registry (RAR) / VAR Structure

The **Reasoning Audit Registry (RAR)** is the component within the final unified **Veracity Audit Registry (VAR)** detailing the logic and rationale used for each RM.

```json
{
  "REASONING": [
    {
      "RELATION_ID": "R1",
      "TYPE": "CAUSAL",
      "DEP_CLAIMS": ["C1", "C2"],
      "SYNTHESIS_PROSE": "The consequence was therefore directly linked to...",
      "LOGIC_MODEL": "Economic_Influence_Model_v1.1",
      "AUDIT_STATUS": "VERIFIED_LOGIC",
      "TIMESTAMP": "2025-10-13T12:00:00Z"
    }
    // ... all reasoning used by Rm markers
  ]
}
```

## 3. Logical Integrity (RSVP Check) from the Compliance Standard

The RSVP check is the second phase of the overall ACG compliance audit, confirming the logical coherence of the generated output.

**Logic Verification Flow:** Every **RM-tagged synthesis** must meet two criteria:

1.  **Premise Integrity:** All its prerequisite claims ($\text{DEP\_IDs}$) must be **fully verified** by the UGVP.
2.  **Model Validation:** The stated $\text{TYPE}$ of reasoning must be validated by an external logic checker against the explicit $\text{LOGIC\_MODEL}$ documented in the VAR.

If the logic checker determines the inference is a **logical fallacy** or is **unsupported**, the synthesis is flagged as **INSUFFICIENT_LOGIC**. Any statement failing this check must be **removed or rewritten** by the Generation Agent.
