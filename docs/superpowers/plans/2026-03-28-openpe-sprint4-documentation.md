# OpenPE Sprint 4: Documentation + Review Runtime

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans.

**Goal:** Build report generation, audit trail, and review orchestration utilities. After Sprint 4, the full Phase 0→6 pipeline has runtime support.

**Tech Stack:** Python 3.11+, pyyaml, jinja2-style string templates, matplotlib

---

## Task 1: Report Generator

Create `src/templates/scripts/report_generator.py` + tests.

Generates REPORT.md from phase artifacts following the spec's 6-section structure. Collects findings from DISCOVERY.md, STRATEGY.md, ANALYSIS.md, PROJECTION.md, VERIFICATION.md into a unified report.

## Task 2: Audit Trail Generator

Create `src/templates/scripts/audit_trail.py` + tests.

Generates machine-readable `claims.yaml` linking every factual claim to its data source and every inferential step to its methodology. Also generates `methodology.yaml` documenting choices made.

## Task 3: Integration Test — Full Report

Test that builds a mock analysis directory with phase artifacts, generates a report, verifies structure.

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | Report generator | 2 |
| 2 | Audit trail | 2 |
| 3 | Integration test | 1 |
| **Total** | | **5 files** |
