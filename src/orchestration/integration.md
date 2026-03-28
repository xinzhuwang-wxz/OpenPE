## Session Logs

Every agent session produces a `session.log`. Not read by other agents
(artifacts are the interface), but serves as audit trail for debugging and
reproducibility.

## RAG Integration

The SciTreeRAG corpus (slopcorpus) is available to all agent sessions via MCP.
The server lazy-loads its index on first tool call; subsequent calls within the
same session are fast. See `.mcp.json` for the concrete server definition.

**Usage expectations:**
- All sessions have the MCP tools available — no per-session setup needed
- Agents query as needed and cite sources in artifacts (paper ID + section)
- Failed retrievals are logged in `retrieval_log.md` per phase (see
  methodology §2.2)
- Prefer `search_lep_corpus` with `mode="hybrid"` (default) for most queries
- Use `compare_measurements` when the analysis needs to cross-check ALEPH vs
  DELPHI results on the same observable
- Use `get_paper` to drill into a specific reference found via search

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
  },
  "mcpServers": {
    "lep-corpus": {
      "type": "stdio",
      "command": "pixi",
      "args": ["run", "--manifest-path", "/path/to/slopcorpus/pixi.toml",
               "python", "mcp_servers/rag_server.py"],
      "cwd": "/path/to/slopcorpus",
      "env": { "RAG_MODEL": "small" }
    }
  }
}
```

The `lep-corpus` MCP server exposes four tools:

| Tool | Purpose |
|------|---------|
| `search_lep_corpus(query, top_k, experiment, mode)` | Hybrid (dense + BM25) retrieval over ~2,400 ALEPH/DELPHI papers; returns ranked passages with metadata |
| `get_paper(paper_id)` | Look up a specific paper by arXiv, INSPIRE, or CDS ID |
| `list_corpus_papers(experiment, category, limit)` | Browse corpus with optional experiment/category filters |
| `compare_measurements(topic, top_k_per_experiment)` | Side-by-side ALEPH vs DELPHI retrieval for cross-checking |

Agents should prefer `search_lep_corpus` for general queries and
`compare_measurements` when cross-checking results between experiments.
Use `get_paper` to drill into a specific reference. All retrieved passages
include source paper ID and similarity score — cite these in artifacts.

## Adapting to Other Agent Systems

Requirements:
- Isolated agent sessions with file read/write and code execution
- RAG corpus accessible as a tool
- Parallel execution support
- Mechanism to pause for human review
- Git integration

The methodology spec is portable; this orchestration doc is the Claude Code
adapter.
