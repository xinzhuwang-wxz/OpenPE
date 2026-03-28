## Appendix A: Phase Dependency Graph

### Unified flow (both measurements and searches)

```
                         Experiment Corpus
                              (RAG)
                                │
                                │  queried throughout
                                ▼
Physics Prompt ──────► Phase 1: Strategy ◄──────────────────────┐
                                │                               │
                                ▼                               │
                       Phase 2: Exploration ◄───────────────┐   │
                                │                           │   │
                     ┌──────────┼──────────┐                │   │
                     │     (per channel)   │                │   │
                     ▼                     ▼                │   │
                  Phase 3a            Phase 3b ...          │   │
                  Channel A           Channel B             │   │
                     │                     │                │   │
                     └──────────┬──────────┘         phase regression
                                │                    (if fundamental
                                ▼                     issue found)
                       Phase 4a: Expected Results           │   │
                                │                           │   │
                        ★ AGENT GATE ★ (4-bot) ─────────────┘   │
                                │                               │
                       Phase 4b: 10% Data Validation            │
                                │                               │
                        ★ 4-BOT REVIEW ★ ──────────────────────┘
                                │
                        ★ HUMAN GATE ★
                        (draft note + 10% results → human)
                                │
                       Phase 4c: Full Data
                                │
                                ▼
                       Phase 5: Documentation
```

Both measurements and searches follow the same phase structure. For
searches, Phase 4b is a consistency validation (10% of data compared to
expected results). Phase 5 includes independent verification with human gate.
The human gate is between 4b and 4c in both cases. See §3 (Phase 4) for details.

---
