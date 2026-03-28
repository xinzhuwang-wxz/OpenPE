## 9. Multi-Channel Analyses

Many HEP analyses involve multiple channels with different final states (e.g.,
ttH with 0-lepton, 1-lepton, 2-lepton channels, or Zh with νν̄bb̄, ℓ⁺ℓ⁻bb̄,
qq̄bb̄ channels). The methodology handles this as follows:

**Phase 1 (Strategy)** defines the channel decomposition:
- Which channels are included, with physics motivation
- How channels are defined to ensure no event overlap (orthogonal selections)
- Which calibrations and systematic uncertainties are shared across channels
  (e.g., jet energy corrections, b-tagging, luminosity)
- Which are channel-specific (e.g., lepton ID for leptonic channel only)

**Phases 2–3** may proceed per-channel, potentially in parallel:
- Each channel has its own exploration, selection, and background modeling
- Shared calibrations (b-tagging efficiency, energy scales) are developed once
  and referenced by all channels
- Each channel produces its own artifact (e.g., `SELECTION_CHANNEL_A.md`,
  `SELECTION_CHANNEL_B.md`)
- A consolidation artifact documents the overlap check (no events shared
  between channels) and summarizes cross-channel consistency

**Shared sub-analyses (calibrations):** Some analysis components are not
channel-specific — they are mini-analyses in their own right that produce
calibration artifacts consumed by all channels. Examples:

- **Jet energy corrections:** derive correction factors from data, measure
  residual uncertainty → produces correction functions + systematic variations
- **b-tag calibration:** measure b-tagging efficiency in data using a tag-and-
  probe or similar method → produces scale factors + uncertainties per working
  point
- **Trigger efficiency:** measure turn-on curves in data → produces efficiency
  maps + uncertainties
- **Luminosity:** typically provided by the experiment, but may need validation

Each shared sub-analysis:
- Has its own experiment log and artifact (e.g., `CALIBRATION_<NAME>.md`)
- Follows the same structure as a phase (method, results, validation, code)
- Produces a calibration artifact with **central values + uncertainties** that
  channels consume as inputs
- The uncertainties propagate into Phase 4 as systematic terms in the fit model
- **Must demonstrate its effect.** The calibration artifact should include
  before/after comparisons showing how the calibration improves agreement with
  data (e.g., an energy calibration should show improved mass peak resolution or
  position; an efficiency calibration should show better data/MC agreement in
  the relevant observable). The specific comparison depends on what is being
  calibrated — the agent chooses the most informative demonstration.

Calibrations do not receive their own dedicated review tier. Instead, their
quality is validated through two mechanisms: (1) the calibration artifact's own
before/after plots provide self-evident validation, and (2) downstream phase
reviews (Phase 3 selection, Phase 4a inference) can flag calibration problems
through the upstream feedback or regression mechanism if results are
inconsistent. A calibration that produces suspicious scale factors or
uncertainties will surface as a data/MC disagreement or fit pathology
downstream.

Shared sub-analyses are identified in Phase 1 (strategy) or Phase 2
(exploration, when the agent discovers what calibrations are needed). They run
in parallel with or before the channel-specific Phase 2–3 work. They may be
assigned to dedicated agent sessions.

**Phase 4** combines channels in a single statistical model:
- The fit model includes all channels simultaneously
- Correlated systematic uncertainties (including shared calibrations) use
  shared nuisance parameters across channels
- The combined expected sensitivity is the primary figure of merit
- Per-channel results are also reported for diagnostic purposes

The channel structure is a strategy decision — the agent proposes it in Phase 1
and the strategy review evaluates whether it makes sense.

---
