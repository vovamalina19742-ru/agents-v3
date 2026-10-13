---
trigger: glob
globs: "*.rs, *.ts, *.tsx, *.js, *.jsx, *.py"
description: "Codemap Driven Development: перед правкой кода сверься с docs/codemap/codemap.lock и codemap.json; после изменений обнови codemap в том же коммите."
---

# CODEMAP DRIVEN DEVELOPMENT & ARCHITECTURE RULE

## 1. PRE-CHANGE VERIFICATION CHECKLIST (Anti-Regression Guardrail)

At the start of **every code-changing task**, agents and developers MUST compare the current repository state with `docs/codemap/codemap.lock`.

Before modifying any module or function, inspect `docs/codemap/codemap.json` to answer three mandatory questions:
1. **What calls it?** (Upstream callers & dependencies)
2. **What does it affect?** (Downstream data flows & side effects)
3. **Which tests cover it?** (Test assertions & verification suites)

If the code map is stale or cannot answer those three questions, run `python scripts/generate_codemap.py` to regenerate `codemap.html`, `codemap.json`, and `codemap.lock` BEFORE making code changes.

---

## 2. ATOMIC CODEMAP SYNCHRONIZATION

Whenever module boundaries, dependencies, routes, databases, queues, or major data flows change:
* Update `docs/codemap/` (**`codemap.html`**, **`codemap.json`**, and **`codemap.lock`**) in the **same commit** as the code changes.
* Never edit only one of the three files manually. Always run `python scripts/generate_codemap.py` to keep them deterministically synchronized.

---

## 3. THREE CODEMAP ARTIFACTS SPECIFICATION

1. **`docs/codemap/codemap.html`**: Self-contained, dark-theme interactive UI with zoom, node filtering, E2E flows, and click-to-highlight dependency graph.
2. **`docs/codemap/codemap.json`**: Machine-readable JSON contract containing nodes (entrypoints, constraints, tests), edges (`imports`, `calls`, `reads`, `writes`), and E2E flows.
3. **`docs/codemap/codemap.lock`**: Deterministic SHA-256 fingerprint lockfile tracking module states and uncommitted changes.
