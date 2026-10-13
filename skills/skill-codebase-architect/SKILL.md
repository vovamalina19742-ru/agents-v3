---
name: skill-codebase-architect
description: "Matt Pocock Architecture & TDD Resilience Loop. Чистая модульная архитектура, Test-Driven Development (TDD) и предотвращение регрессий в Rust, C# и TypeScript."
---

# 🏛️ SKILL: Codebase Architect & TDD Engine

## 📌 Назначение
Этот навык предотвращает «спагетти-код», разрушение существующих модулей и поломку сборки при масштабировании проектов.

---

## ⚡ 1. Принцип изоляции слоев (Clean Boundary Pattern)
* **Разделение ввода-вывода (I/O) и бизнес-логики:**
  - Бизнес-логика (расчет хэшей, скоринг, фильтрация) оформляется как **чистые детерминированные функции**, не зависящие от сети и диска.
  - Сетевые вызовы, доступ к БД и IPC изолируются в адаптерах (`plugins/`, `services/`).
* **Строгая типизация ошибок (No Raw Strings):**
  - Запрещено пробрасывать нетипизированные `String` или `any`.
  - В Rust: `Result<T, AppError>` с макросом `thiserror`.
  - В TypeScript: строгие интерфейсы ответов и кодов ошибок (`error_code`).

---

## 🧪 2. Цикл TDD (Test-Driven Development)
1. **Тест перед фичей:** Сначала пишется падающий модульный тест (`#[test]`, `it('...')`).
2. **Минимальная реализация:** Пишется минимально достаточный код для прохождения теста.
3. **Рефакторинг под защитой тестов:** Код оптимизируется и очищается с гарантией 100% прохождения теста.
4. **Регрессионный заслон:** Перед каждым коммитом обязателен запуск тестового набора (`cargo test`, `npm test`, `dotnet test`).

---

## 🗺️ 3. Семантическая Навигация по Графу Кода (Graft Pattern)
* **Запрет слепого Grep и полного вычитывания:**
  - Запрещено читать файлы >100 строк целиком для выяснения зависимостей.
  - Агент восстанавливает направленный граф: `Caller Function ➔ Interface / Type ➔ Target Service`.
* **Целевые связки по проектам:**
  - **C# (`SmartphoneMonitor`):** `Listing` ➔ `ListingClassifier` ➔ `AntiScamService` ➔ `HotDealBuilder` ➔ `QuantVerdict`.
  - **Rust / Tauri (`media-downloader`):** `Tauri Command` ➔ `specta/ts-rs Type Binding` ➔ `React Hook` ➔ `UI Component`.
  - **Python (`sentinel-osint`):** `MCP JSON-RPC Tool` ➔ `Sidecar Process` ➔ `OSINT Dossier`.
* **Эффект:** Экономия до 70% контекстного окна и исключение скрытых сайд-эффектов при правках.

