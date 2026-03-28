## 2. Inputs

An analysis begins with two inputs:

### 2.1 Physics Prompt

A brief natural-language description of the physics goal. Examples:

> Search for the Higgs boson produced in association with a Z boson, where the
> Higgs decays to a pair of b quarks, using ALEPH data at sqrt(s) = 200–209 GeV.

> Measure the inclusive W+W- production cross-section at LEP2 energies using
> fully hadronic final states.

The prompt need not specify methodology. It states the physics target and any
constraints (dataset, final state, energy range).

### 2.2 Experiment Context (Retrieval-Based, When Available)

The agent **may** have access to a retrieval system (SciTreeRAG over a corpus
of collaboration publications, theses, and internal notes) for the relevant
experiment(s), exposed as MCP tools. When available, this replaces
hand-curated configuration files. See `.mcp.json` for the server
configuration and orchestration §RAG Integration for the tool reference.

**When RAG is not available:** The agent proceeds using its training
knowledge and any documentation provided in the analysis directory (e.g.,
detector papers, prior analysis notes placed in a `docs/` directory by the
user). All experiment-specific claims must be marked as "based on training
knowledge — no corpus verification" and flagged for human review. The
analysis is still valid; it simply has weaker provenance for detector
parameters and prior measurements. The phase templates' "RAG queries
(mandatory)" sections become "RAG queries (if corpus available)" — the
queries are still the right questions to answer, but the agent uses whatever
sources are at hand.

The agent queries this corpus to obtain:
- Detector specifications (subsystem resolutions, angular coverage, material
  budgets)
- Standard object definitions (tracking, lepton ID, jet reconstruction) as
  published in collaboration papers
- Available MC generators, simulation samples, and their known limitations
- Measured performance (efficiencies, fake rates, energy scale uncertainties)
- Prior analyses in the same or related channels (for context, not for copying)

**Why retrieval over static files:** Experiment knowledge is vast, evolving, and
distributed across hundreds of publications. No static configuration captures it
adequately. A retrieval system over the actual literature (a) scales to any
experiment with a publication corpus, (b) provides citations naturally, (c) lets
the agent discover relevant information it wouldn't know to ask for, and (d)
stays current as new publications are indexed.

The agent must cite the source for any experiment-specific information it uses
(detector parameters, object selections, performance numbers). "Retrieved from
[reference]" is the minimum; direct quotation with section numbers is preferred.

**Retrieve, then verify.** Information from the retrieval corpus may be
incomplete, out of context, or wrong. Where the analysis has access to the
underlying data (as is the case for completed experiments like ALEPH or DELPHI
where full datasets are available), the agent must verify retrieved claims
against the data itself. If the corpus says "good tracks require ntpc >= 4",
the agent should confirm this produces the expected efficiency by applying the
cut to data and comparing. The data is the ground truth; the corpus provides
starting points and context. Discrepancies between retrieved information and
observed data behavior must be documented and resolved — typically by trusting
the data and noting the corpus inconsistency.

**When retrieval fails.** The corpus may be sparse, the query poorly matched,
or the relevant information simply not indexed. The agent should:
1. Log the failed query and what it was looking for in a retrieval log
   (`retrieval_log.md` in the phase directory)
2. Try rephrased queries or broader searches
3. If retrieval remains unhelpful, proceed using the agent's training knowledge
   and clearly mark any claim that is not corpus-backed as "unverified — based
   on general knowledge, to be confirmed"
4. Flag the gap in the artifact's open issues section

The RAG corpus is an aid, not a requirement. The agent should never block on a
failed retrieval — it does its best and documents the uncertainty.

---
