# Audited Context Generation (ACG) Protocol: A Dual-Layer Standard for Veracity Assurance

## Abstract

The Audited Context Generation (ACG) Protocol eliminates both factual and logical hallucinations by combining the **Universal Grounding and Verification Protocol (UGVP)** for source integrity and the **Reasoning and Synthesis Verification Protocol (RSVP)** for logical integrity. It mandates explicit, machine-auditable metadata for every claim and synthesis step.

---

## 1. Core Principles and Components

The ACG requires the agent to produce three interlocking components: **Citation Markers**, **Source Hash Identity (SHI)**, and the **Veracity Audit Registry (VAR)**.

| Component                                  | Layer          | Purpose                                                                                   | Syntax/Mechanism            |
| :----------------------------------------- | :------------- | :---------------------------------------------------------------------------------------- | :-------------------------- |
| **Claim Marker** ($\text{C}_n$)            | UGVP (Layer 1) | **Atomic Fact Grounding**. Links a single statement to a source location.                 | `[C{N}:SHI_P:{LOC}]`        |
| **Relationship Marker** ($\text{R}_m$)     | RSVP (Layer 2) | **Logical Synthesis Verification**. Links a conclusion to the $\text{C}_n$ it depends on. | `(R{M}:TYPE:C{1},C{2},...)` |
| **Source Hash Identity** ($\text{SHI}$)    | Both           | **Source Immutability**. A cryptographic fingerprint of the source document.              | `SHA256(URI \| Version)`    |
| **Veracity Audit Registry** ($\text{VAR}$) | Both           | **Unified Audit Trail**. Machine-readable JSON combining SSR and RAR data.                | Single JSON block           |

---

## 2. Layer I: Universal Grounding and Verification (UGVP)

This layer establishes the auditable premises for the output.

### 2.1. Source Hash Identity (SHI)

The $\text{SHI}$ is a **non-negotiable immutable identifier**. The full $\text{SHI}$ must be stored in the $\text{VAR}$, but only a short prefix ($\text{SHI}_P$) is used in the in-line marker for brevity.

### 2.2. Claim Marker Syntax (`[C{N}:SHI_P:{LOC}]`)

| Field          | Definition and Details                                                                                       | Example Value                     |
| :------------- | :----------------------------------------------------------------------------------------------------------- | :-------------------------------- |
| $\text{C}_N$   | **Claim ID:** A unique, sequential identifier ($\text{C}1, \text{C}2, \dots$) within the document.           | `C1`                              |
| $\text{SHI}_P$ | **SHI Prefix:** The first 8-10 characters of the $\text{SHI}$. Used for compact look-up in the $\text{VAR}$. | `8b1c4d9a`                        |
| $\text{LOC}$   | **Location Selector:** The precise, canonical structural selector for the claim.                             | `css=#section-A > p:nth-child(2)` |

---

## 3. Layer II: Reasoning and Synthesis Verification (RSVP)

This layer establishes the accountability for complex claims that combine or interpret atomic facts.

### 3.1. Relationship Marker Syntax (`(R{M}:TYPE:DEP_IDs)`)

The $\text{R}_M$ is triggered whenever the agent generates a statement that is not a direct quotation or restatement of a single source claim.

| Field             | Definition and Details                                                                                              | Example Value |
| :---------------- | :------------------------------------------------------------------------------------------------------------------ | :------------ |
| $\text{R}_M$      | **Relationship ID:** A unique, sequential identifier ($\text{R}1, \text{R}2, \dots$) for the synthesized statement. | `R1`          |
| $\text{TYPE}$     | **Relationship Type:** Must be one of the defined verifiable logical operations.                                    | `CAUSAL`      |
| $\text{DEP\_IDs}$ | **Dependency Claims:** A comma-separated list of **Claim IDs** ($\text{C}_n$) used as premises for this synthesis.  | `C1,C2,C3`    |

### 3.2. Verifiable Relationship Types

The ACG mandates verification for the following types of reasoning:

| $\text{TYPE}$  | Definition                                                                              | Verification Requirement                                                                                                                              |
| :------------- | :-------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------- |
| **CAUSAL**     | Assertion that A led to B or A influenced B.                                            | Must be supported by a verified source that explicitly states the causality, OR a highly-validated, auditable **LOGIC_MODEL** demonstrating the link. |
| **INFERENCE**  | A logical deduction (e.g., if A is true and A $\rightarrow$ B is true, then B is true). | The logical steps and the premises ($\text{DEP\_IDs}$) must be verifiable against formal logic rules.                                                 |
| **SUMMARY**    | A conclusion or generalization derived from multiple facts.                             | The conclusion must be **statistically representative** and **not contradicted** by any of the premises ($\text{DEP\_IDs}$).                          |
| **COMPARISON** | A definitive statement about differences or similarities.                               | The comparison metric must be explicitly cited or mathematically derived from the verifiable data in the $\text{DEP\_IDs}$.                           |

### 3.3. Veracity Audit Registry (VAR) Structure

The VAR is the unified, final JSON block. It consolidates the $\text{SSR}$ (source metadata) and $\text{RAR}$ (reasoning data) for machine audit.

```json
{
  "SOURCES": [
    {
      "SHI": "8b1c4d9ae03b...",
      "Type": "WebArticle",
      "Canonical_URI": "https://doi.org/10.1234/temp_data_v1",
      "Verification_Status": "VERIFIED"
    }
    // ... all sources used by Cn markers
  ],
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

## 4. ACG Verification Workflow (The ACG Guarantee)

The independent Verifier Agent's mandatory two-phase process that enforces the "never lies" principle of the Audited Context Generation (ACG) Protocol.

1.  **Phase 1: Atomic Fact Verification (UGVP)**

    - **Action:** For all $\text{C}_n$ markers: Retrieve source via $\text{SHI}_P$, fetch content, and use $\text{LOC}$ to confirm the exact claim text.
    - **Outcome:** Claims are marked **VERIFIED** or **FAILED** in the $\text{VAR}$. Any sentence containing a **FAILED** claim is removed from the final output.

2.  **Phase 2: Synthesis Verification (RSVP)**
    - **Condition Check:** An $\text{R}_M$ can only be audited if **ALL** of its $\text{DEP\_IDs}$ (premises) were **VERIFIED** in Phase 1.
    - **Action:** If the condition is met, the Verifier Agent validates the $\text{TYPE}$ of relationship against the explicit $\text{LOGIC\_MODEL}$ cited in the $\text{VAR}$.
    - **Outcome:** The relationship is marked **VERIFIED_LOGIC** or **INSUFFICIENT_LOGIC**. If marked **INSUFFICIENT_LOGIC**, the synthesized sentence is removed or flagged.

This combined ACG workflow ensures that the final output is composed only of **verifiable claims** supported by **validated reasoning**.
