# OpenPE Orchestration

Orchestration is defined in the root template (`src/templates/root_claude.md`).

The orchestrator loop runs phases [0, 1, 2, 3, 4, 5, 6] with:
- Phase-specific executor agents
- Multi-tier review (4-bot, 1-bot, 5-bot, self)
- Human gate at Phase 5 (Verification)
- Phase regression protocol for Category A issues
