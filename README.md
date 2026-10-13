# AGENTS v3.0: Production Platinum Multi-Agent Ecosystem

[![Status: Production](https://img.shields.io/badge/status-production--platinum-brightgreen.svg)]()
[![Skills: 35](https://img.shields.io/badge/skills-35%20modular%20skills-blue.svg)](skills/CATALOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Портативный, автономный манифест правил, ролей и модульных навыков команды ИИ-агентов.**  
> Полностью совместим со средами **Google Antigravity**, **AgentMemory**, **Tauri v2 (Rust)**, **Ollama** и **Claude Desktop**.

---

## 🏛 Архитектурные принципы (Zero-Cost Tokens)

1. **Режим нулевых затрат:** Навигация по AST-графу кода вместо чтения целых файлов; локальный RAG по 424 книгам (FTS5); делегирование рутины локальным моделям Ollama (0 токенов).
2. **Core-Engineer Fusion:** Объединение ролей системного аналитика и бэкендера в связке с Rust-контрактами (`specta::Type`).
3. **Fork-Join Subgraphs:** Изолированные подграфы состояний для ядра (Rust/IPC) и интерфейса (React/UI) для предотвращения гонок.
4. **Fallback & Reflect:** Трехступенчатый протокол устойчивости (локальная правка $\to$ откат и рефлексия $\to$ эскалация человеку).
5. **Rich IPC AppError:** Строго типизированные иерархические ошибки вместо плоских строк.

Полный канонический регламент зафиксирован в [**AGENTS.md**](AGENTS.md).

---

## 📦 Каталог навыков (35 Skills)

Все навыки разделены на два прозрачных домена (подробнее в [**skills/CATALOG.md**](skills/CATALOG.md)):

### 1. Домен Ядра Памяти (AgentMemory Core Standard — 15 навыков)
- `remember`, `recall`, `recap`, `forget`, `handoff`, `lesson`, `memory-discipline`, `session-history`, `commit-context`, `commit-history`.
- `agentmemory-architecture`, `agentmemory-config`, `agentmemory-hooks`, `agentmemory-mcp-tools`, `agentmemory-rest-api`, `agentmemory-agents`.

### 2. Домен Прикладных Модулей (Production Engineering — 20 навыков `skill-*`)
- **Светотехника и CAD:** `skill-lighting-estimator-pro`, `skill-pdf-translate-customs`, `skill-invoice-scanner-organizer`.
- **Безопасность и разведка:** `skill-cloudflare-security-audit`, `skill-osint-ai`, `skill-subdomain-recon`, `skill-apk-reverse`.
- **Архитектура и код:** `skill-codebase-architect`, `skill-js-ast-analyzer`, `skill-ebpf-linux`, `skill-frontend-master`.
- **Автоматизация и медиа:** `skill-playwright-stealth`, `skill-video-workflow-automator`, `skill-diagram-design`.
- **Когнитивные перспективы:** `skill-nuwa-perspectives` (ментальные модели Маска, Карпати, Мангера, Талеба, Фейнмана, Джобса).

---

## 🚀 Быстрый старт

### Для Antigravity / Claude Desktop:
Поместите папку `.agents/` в корень вашего проекта или домашней директории:
```bash
git clone https://github.com/vovamalina19742-ru/agents-v3.git .agents
```

Среда автоматически подхватит:
- Системные правила из `rules/*.md` (на базе триггеров);
- Модульные навыки из `skills/` (по описаниям в промптах);
- Канонический свод из `AGENTS.md`.

---

## 📄 Лицензия
Распространяется под лицензией MIT.
