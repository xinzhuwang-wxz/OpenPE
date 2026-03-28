# OpenPE Sprint 5: Memory System + Self-Evolution

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans.

**Goal:** Implement the cross-analysis memory system that enables OpenPE to learn from experience — L0/L1/L2 tiered memory, session commit, confidence-scored memories with decay, causal knowledge graph, and domain pack auto-growth.

**Tech Stack:** Python 3.11+, pyyaml, json (for causal graph)

---

## Task 1: Memory Store (L0/L1/L2)

Create `src/templates/scripts/memory_store.py` + tests.

Core memory store with tiered loading:
- `MemoryEntry`: dataclass with content, domain, type, confidence, source_analysis, corroborated_by, contradicted_by, decay_rate
- `MemoryStore`: manages L0/L1/L2 directories, loads entries by tier, saves new entries
- Confidence evolution: corroborate (+0.15, cap 0.95), contradict (-0.25, floor 0.05), decay (-0.01/analysis)
- Loading rules: conf≥0.2 normal, 0.1≤conf<0.2 WARNING prefix, conf<0.1 quarantined

## Task 2: Causal Knowledge Graph

Create `src/templates/scripts/causal_knowledge_graph.py` + tests.

Persistent graph of established causal relationships across analyses:
- `CausalKnowledgeGraph`: load/save from graph.json, add_relationship, query, corroborate/contradict
- Reuse policy: conf≥0.8 skip re-test, 0.5≤conf<0.8 lightweight verify, conf<0.5 must re-test
- Contradiction detection: new analysis finding vs stored finding

## Task 3: Session Commit

Create `src/templates/scripts/session_commit.py` + tests.

Post-analysis experience extraction:
- `extract_experiences()`: parse phase artifacts, extract domain/method/data_source/failure experiences
- `commit_session()`: write extracted experiences to memory store, update causal graph
- `grow_domain_pack()`: create/update L1 domain YAML from extracted experiences

## Task 4: Integration Test

Full cycle: run session commit → memories stored → load in new analysis → verify domain pack auto-growth.

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | Memory Store (L0/L1/L2) | 2 |
| 2 | Causal Knowledge Graph | 2 |
| 3 | Session Commit | 2 |
| 4 | Integration test | 1 |
| **Total** | | **7 files** |
