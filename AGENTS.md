# СВОД ПРАВИЛ И АРХИТЕКТУРА КОМАНДЫ АГЕНТОВ (AGENTS_v3.0)
## Проект: Универсальный комплекс системных решений и медиа-комбайн
### Версия: 3.0 (PRODUCTION PLATINUM: Eco-Orchestrator Zero-Cost, Core-Engineer Fusion, Fork-Join Subgraphs, Fallback & Reflect Resilience, Rich IPC AppError, E2E UI Gate, Minimal CAD Takeoff)
### Стек: Tauri v2 (Rust) + TypeScript/React (Tailwind CSS) | Удаленный узел: Linux Mint 22.3 (192.168.100.22)

---

### 0. ФУНДАМЕНТАЛЬНЫЕ ЗАКОНЫ И РЕЖИМ ECO-ORCHESTRATOR (ZERO-COST)

| Принцип | Правило реализации |
| :--- | :--- |
| **Режим Нулевых Затрат (Zero-Cost Tokens)** | **Категорически запрещено сжигать бесплатные лимиты.** (1) Навигация по графу кода (Code Graph-First by AST Call Tree) вместо чтения целых файлов (срез до 70% контекста); (2) Обязательная фильтрация консольного вывода через `rtk.exe` / silent flags (срез 90% мусора); (3) Локальный поиск по базе 362 книг через SQLite FTS5 `book_search` (0 токенов, <50 мс); (4) Запрет скармливания нейросети сырых PDF/DWG чертежей целиком (парсинг локальными скриптами $\to$ передача только компактного JSON); (5) Автономный ИИ и локальный семантический RAG на сервере Linux `192.168.100.22` и локальной Ollama (0 токенов): генерация кода и саммари через `qwen2.5-coder`, векторные эмбеддинги кода и ссылок через `nomic-embed-text`. |
| **Делегирование в AI_Agent Bridge (Zero-Cost Dispatcher)** | **Antigravity выступает Руководителем / Диспетчером и ОБЯЗАН использовать мост `ai-agent-bridge` (`D:\AI_Agent`) для всей рутинной и исполнительной работы:** (1) Итеративная исполнительская работа (веб-скрапинг, анализ внешних ссылок, поиск по книгам, сетевые проверки, правки кода) делегируется через `task_assign` локальным моделям Ollama (qwen2.5-coder:7b / deepseek-r1:8b / qwen2.5:3b / 1.5b) за 0 токенов; (2) В свой контекст Antigravity забирает СТРОГО сухой `result_summary` через `task_result` (запрещено тянуть сырые страницы и дампы); (3) Быстрый поиск по библиотеке книг — строго через FTS5 `book_search` (<50 мс); (4) Поиск по накопленным знаниям — через гибридный семантический RRF-слой `memory` / `search_saved_links`; (5) Antigravity оставляет себе стратегическое планирование, сложный код и финальный синтез для пользователя. |
| **Аппаратный профиль и разгрузка ноутбука** | **Ноутбук — мобильный командный пункт с ограниченными ресурсами.** Запрещено нагружать локальную систему тяжелыми Electron-пакетами, бесконтрольными контейнерами или фоновыми процессами (RAM < 80%, защита SSD от износа). Все тяжелые сборки, тесты, видео-пайплайны и 24/7 сервисы сгружаются на удаленный узел Linux (`192.168.100.22`, раздел `/DATA`, 395 ГБ свободно) через `scripts/remote_worker.py`. |
| **Энергогигиена старого ПК (Energy Hygiene)** | Старый ПК (`192.168.100.22`) в активном режиме потребляет 80–120 Вт. **Запрещен холостой ход.** Запуск строго по необходимости через Wake-on-LAN (`python scripts/wake_old_pc.py`). По завершении задачи — немедленный перевод в спящий режим S3 Suspend (< 1 Вт) командой `python scripts/sleep_old_pc.py`. |
| **Регламент чертежей: Только Подсчет (Minimal CAD Takeoff)** | **При получении чертежей (PDF/CAD) главная и единственная задача — точный подсчет оборудования.** Итоговый отчет формируется строго в минималистичном формате: только «№», «Наименование» и «Количество шт./м», итоговая строка. **Запрещено включать цены, сметную стоимость и избыточные описания.** Форматы выдачи: лаконичный PDF (для быстрой визуальной сверки) и XLSX/CSV (для импорта в CRM). |
| **Безопасность ПК и Guardrails** | Запрещены деструктивные команды в терминале. Файловые операции ограничены каталогом проекта, папкой `downloads/` и сетевым кэшем `\\192.168.100.22\cache`. **Обязательна строгая каноникализация путей (`std::fs::canonicalize()` в Rust) с проверкой `resolved_path.starts_with(&allowed_root)` (защита от Path Traversal, NTFS Alternate Data Streams `file:stream`, коротких имен `PROGRA~1` и `../../`).** |
| **Подход Rust-First и типизация IPC** | Чистый Rust (`reqwest`, `scraper`, `lol_html`) для 90% логики. Python допускается исключительно как Sidecar при наличии сложных WAF (Cloudflare/капча). **Строгая автогенерация TypeScript-типов из Rust-структур через `specta` / `ts-rs` при `cargo test/build` — ручное дублирование типов запрещено.** |
| **Защита Секретов & Supply Chain** | Секреты (Cookie, токены, пароли) хранятся через `keyring` в Rust (с fallback KDF Argon2id от `machine-id` + DMI UUID в headless Linux). Запрещен plaintext. Проверка хэшей SHA-256 по `sidecar.manifest.json`. Аудит зависимостей (`cargo audit`, `npm audit`). |
| **Политика «Skill-First»** | Перед проектированием и R&D обязателен поиск готового навыка в каталоге `/skills/` (отбор решений с `success_rate >= 70%`). Запрещено писать код без доказанного рабочего PoC. |
| **Политика DRM** | При `DrmType::StreamEncrypted` $\to$ мгновенное отклонение с ошибкой `DRM_PROTECTED`. При `DrmType::MetadataOnly` $\to$ извлечение метаданных. Попытки взлома DRM **категорически запрещены**. |

---

### 1. СТРУКТУРА РОЛЕЙ (CORE-ENGINEER FUSION)

Для устранения задержек передачи контекста и экономии токенов исключено избыточное дробление ролей:

1. **Генеральный Директор, Оркестратор (CGO):**
   * Ментальный центр. Координирует этапы, управляет бюджетом токенов, форкает подграфы состояния и валидирует финальный релиз.
2. **Core-инженер (Rust Systems & Contracts Lead):**
   * **Объединение Системного Аналитика (CSA) и Бэкендера (BE).**
   * Тот, кто проектирует контракты данных, сам реализует их на Rust (`#[derive(specta::Type, Serialize)]`).
   * Реализует асинхронное ядро, WASM/Sidecar плагины, адаптивный Backpressure 2.0, FFmpeg-конвейеры и автогенерацию TS-деклараций.
3. **Инженер Интерфейса (FE Lead):**
   * Разработка отзывчивого GUI на React/TypeScript (Tailwind CSS, i18next, a11y, тёмная тема).
   * Потребление автогенерированных типов `specta`, поддержка 4 состояний элементов × 2 темы = 8 вариантов, нулевой визуальный мусор.
4. **QA Chaos & E2E Tester (QA Lead):**
   * Стресс-тесты, фаззинг путей (`proptest`), аудит безопасности зависимостей.
   * **Обязательное E2E-тестирование интерфейса:** физическое прокликивание сгенерированных React-компонентов через Playwright / Tauri WebDriver, контроль чистоты консоли (`console.error === 0`).
5. **Хранитель Активов и Памяти (AssetGuardian):**
   * Непрерывный учет оборудования по `INVENTORY.md`, контроль энергогигиены (сон сервера), капитализация решений в `/skills/` (`manifest.json` с метриками `success_rate` и `last_verified_date`).

---

### 2. ГРАФ СОСТОЯНИЯ (FORK-JOIN SUBGRAPHS ДЛЯ ПАРАЛЛЕЛИЗМА)

Для предотвращения состояния гонки (Race Condition) монолитный `GraphState` разделен на изолированные подграфы:

```typescript
interface TaskGraphState {
  task_id: string;
  phase: 'retrieval' | 'spike' | 'design' | 'dev' | 'qa' | 'capitalization';
  target_url?: string;
  
  // Изолированное подсостояние Core-инженера (Rust/IPC):
  core_state: {
    contracts_ready: boolean;
    types_generated: boolean;
    backpressure_active: boolean;
    history: string[]; // локальный кольцевой буфер ядра (max 20)
    errors: string[];
  };

  // Изолированное подсостояние Фронтендера (React/UI):
  ui_state: {
    components_ready: boolean;
    theme_support: boolean;
    history: string[]; // локальный кольцевой буфер UI (max 20)
    errors: string[];
  };

  // Слияние Оркестратором на этапе QA:
  qa_verdict?: {
    e2e_ui_passed: boolean;
    security_audit_passed: boolean;
    status: 'APPROVED' | 'REJECTED';
  };
}
```

---

### 3. СТРАТЕГИЯ ОТСТУПЛЕНИЯ (FALLBACK & REFLECT CIRCUIT BREAKER)

Вместо глухой парализующей остановки при ошибках компиляции/тестов агент действует по 3-ступенчатому протоколу:

1. **Итерация 1–2 (Локальная правка):** Анализ вывода `cargo check` / `cargo test` и точечное исправление типов или времен жизни.
2. **Итерация 3 (Откат и Рефлексия):**
   * Автоматический откат к последнему стабильному состоянию (`git stash` / `git checkout`).
   * **Reflect:** Смена архитектурного паттерна (упрощение структур, замена сложных ссылок на клонирование/`Arc<Mutex>`, обращение к 424 книгам по архитектуре через `search_books.py`).
3. **Эскалация (HITL):** Если альтернативная стратегия также дала сбой — формирование краткого отчета Оркестратору и вызов Пользователя с конкретными вариантами выбора.

---

### 4. БОГАТАЯ ИЕРАРХИЯ ОШИБОК IPC (RICH APPERROR)

Запрещен плоский `Result<T, String>`. Ошибки возвращаются как вложенные типизированные структуры:

```rust
#[derive(Serialize, Deserialize, specta::Type, Debug)]
#[serde(tag = "type", content = "details")]
pub enum AppError {
    Network(NetworkErrorDetails),
    Storage(StorageErrorDetails),
    Drm(DrmErrorDetails),
    Parser(ParserErrorDetails),
}

#[derive(Serialize, Deserialize, specta::Type, Debug)]
pub struct NetworkErrorDetails {
    pub code: u16,
    pub retry_after_secs: Option<u64>,
    pub domain: String,
    pub is_rate_limited: bool,
    pub is_captcha_challenge: bool,
}

#[derive(Serialize, Deserialize, specta::Type, Debug)]
pub struct StorageErrorDetails {
    pub kind: StorageErrorKind, // DiskFull, PermissionDenied, PathEscape
    pub path: String,
    pub available_bytes: u64,
}

#[derive(Serialize, Deserialize, specta::Type, Debug)]
pub struct DrmErrorDetails {
    pub drm_type: String, // "Widevine", "PlayReady", "FairPlay"
    pub manifest_url: String,
}
```
*Эффект:* React-фронтенд при `is_rate_limited` автоматически включает таймер обратного отсчета (`retry_after_secs`), не дергая ядро бэкенда.

---

### 5. АДАПТИВНЫЙ BACKPRESSURE 2.0 & РЕСУРСЫ

* **Порог памяти:** Автоматическая пауза сетевых загрузок и рендера при свободном RAM < `max(500MB, total_ram * 0.15)`.
* **Дисковая очередь:** Динамический порог кэша с автодетектом типа накопителя (NVMe/SSD vs HDD через `sysfs` / `DeviceIoControl`).
* **Сетевые интервалы:** Базовый интервал между запросами к одному домену — **500 мс** (Jitter $\pm 200$ мс) с адаптивным экспоненциальным Backoff ($2^n \times \text{base}$) при `Retry-After`. Максимум 3 параллельных соединения на один хост.

---

### 6. МАТРИЦА ПРИНЯТИЯ РЕШЕНИЙ В R&D (Troubleshooting Matrix)

| Симптом | Первичная гипотеза | Вторичная гипотеза | Действие агента |
| :--- | :--- | :--- | :--- |
| **403 Forbidden** | Блокировка WAF (Cloudflare) | Невалидный фингерпринт TLS | Сменить JA3-фингерпринт $\to$ Сменить IP $\to$ Мобильный API |
| **429 Too Many Requests** | Превышен лимит частоты | Отсутствует Backoff | Считать `Retry-After` $\to$ Включить экспоненциальный Backoff $\to$ Пауза |
| **Капча (Turnstile / reCAPTCHA)** | WAF Challenge | Блокировка IP-подсети | **Остановка (HITL).** Запрос токена/куки `cf_clearance` у пользователя |
| **Белый экран в UI (E2E FAIL)** | Отвал React-хука / TypeError | Конфликт CSS / z-index | Снять лог `console.error` через Playwright $\to$ изолировать компонент |
| **Borrow Checker Loop (Rust)** | Запутанные времена жизни (`'a`) | Циклические ссылки | Применить Fallback: переход на `Arc<Mutex<T>>` или передачу владения (`move`) |
| **NTFS Traversal Warning** | ADS (`file:stream`) или `PROGRA~1` | Относительный путь `../../` | Применить `std::fs::canonicalize()` с валидацией `starts_with(&allowed_root)` |

---

## ПАМЯТКА ПО КОМПЛЕКТУ `.agents/`

- `rules/*.md` — системные правила, загружаемые по триггерам. **Обязателен YAML-frontmatter** (`trigger: always_on | model_decision | glob | manual`), иначе среда Antigravity молча отбрасывает правило.
- `skills/` — библиотека модульных навыков (progressive disclosure по описанию); общий траблшутинг памяти находится в `skills/_shared/TROUBLESHOOTING.md`.
- `TEMPLATES.md` — автономный справочник шаблонов проектирования и промптов.
- **Примечание о `graphify-out/`:** Каталог `graphify-out/` (и `graph.json`) является **runtime-артефактом**, который строится в целевой кодовой базе при вызове команды `graphify update .` (на базе AST-анализа), а не статическим файлом репозитория правил.
