---
name: skill-prompt-master
description: Advanced System Prompt Engineering, Chain-of-Thought (CoT) Verification, and Anti-Hallucination Guardrails.
---

# Advanced System Prompt Engineering & Guardrails (`skill-prompt-master`)

## Overview
This skill encapsulates systematic prompt engineering principles, Chain-of-Thought (CoT) verification, and anti-hallucination guardrails derived from *«Мастер запросов для ИИ: Основы написания промптов»* and *«Генеративный ИИ с обучением больших языковых моделей (LLM)»*.

---

## 🎯 1. Core System Prompt Anatomy

Every enterprise agent prompt must follow a 4-part modular structure:
1. **Identity & Role Scope:** Unambiguous assignment of domain expertise and boundaries.
2. **Context & Technical Stack Constraints:** Explicit versioning, OS, and framework rules.
3. **Execution Pipeline (Step-by-Step Flow):** Strict sequential workflow rules.
4. **Output Schema Specification:** Typed JSON schemas or structured Markdown blocks.

---

## 🛡 2. Anti-Hallucination & Verification Techniques

### Rule 1: Ground-Truth Verification Over Generation
- Never trust LLM text summaries for exact numeric or code calculations.
- Enforce deterministic code execution (e.g. PyMuPDF vector extraction, unit tests) before declaring success.

### Rule 2: Few-Shot In-Context Demonstrations
- Provide 2-3 input/output pairs containing edge cases (e.g. empty results, network timeouts, special characters).

### Rule 3: Defensive Refusal Prompts
- Require the model to output explicit error codes (`DRM_PROTECTED`, `PATH_TRAVERSAL_DENIED`) when encountering out-of-bounds operations.
