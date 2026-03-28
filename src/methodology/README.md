# OpenPE Methodology

OpenPE's methodology is defined in the phase templates (`src/templates/phase*_claude.md`)
and the orchestrator template (`src/templates/root_claude.md`).

Key methodology documents:
- Phase templates define what each phase does
- Agent profiles (`.claude/agents/`) define how each agent operates
- The EP engine (`src/templates/scripts/ep_engine.py`) defines the core metric
- The causal pipeline (`src/templates/scripts/causal_pipeline.py`) defines the testing protocol
