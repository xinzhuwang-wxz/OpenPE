## Session Logs

Every agent session produces a `session.log`. Not read by other agents
(artifacts are the interface), but serves as audit trail for debugging and
reproducibility.

## Knowledge Integration

OpenPE uses the memory system (L0/L1/L2) for cross-analysis knowledge. No external corpus server is required.

## Mapping to Claude Code Agent Teams

### Team Structure

The **lead agent** is the orchestrator — spawns teammates, manages
dependencies, handles gates. Does not do analysis work.

Per phase (4-bot example):
```
Lead (orchestrator)
  ├── Executor
  ├── Critical Rev
  ├── Constructive Rev
  └── Arbiter
```

For 1-bot phases, the lead spawns only Executor + Critical Rev.
For self-review phases, only Executor.

### Isolation Guarantees

- Each teammate has its **own context window**
- Communication via **shared files only**
- Critical and constructive reviewers cannot see each other's work
- The experiment log is the only shared mutable state within a phase

### Configuration

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

## Adapting to Other Agent Systems

Requirements:
- Isolated agent sessions with file read/write and code execution
- Parallel execution support
- Mechanism to pause for human review
- Git integration

The methodology spec is portable; this orchestration doc is the Claude Code
adapter.
