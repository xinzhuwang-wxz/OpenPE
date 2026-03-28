# Orchestration Layer

Operational implementation of the methodology spec for Claude Code agent
systems. The methodology (`../methodology/`) defines *why* and *what*; this
directory defines *how* to execute it with agents.

## Files

| File | Purpose |
|------|---------|
| `agents.md` | Literal prompt templates for each agent role (executor, reviewers, arbiter) — the orchestrator copies these when spawning subagents |
| `automation.md` | Pseudocode for the orchestration loop (review tiers, regression handling, main pipeline example) |
| `sessions.md` | Session naming, directory layout (ASCII tree), isolation model, concurrency |
| `integration.md` | RAG corpus setup (MCP tools), Claude Code team mapping, adaptation to other systems |

## Relationship to other layers

- **Methodology** (`../methodology/`) — authoritative principles and
  requirements. This directory implements them; it does not redefine them.
- **Templates** (`../templates/`) — CLAUDE.md files copied into analyses.
  Templates are what agents read at runtime. This directory defines how the
  orchestrator assembles context and spawns agents that read those templates.
- **Conventions** (`../conventions/`) — domain knowledge symlinked into
  analyses. Orchestration defines when conventions are consulted (Phases 1,
  4a, 5); conventions define what to check.
