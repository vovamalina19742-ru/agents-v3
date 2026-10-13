---
name: skill-js-ast-analyzer
description: "BishopFox/jsluice-inspired JavaScript & TypeScript AST static analyzer for automated endpoint discovery, shadow API mapping, media stream (.m3u8/.mpd) extraction, and high-entropy secret detection."
version: 1.0.0
author: Antigravity Team
tags: [jsluice, ast, security, reverse-engineering, osint, media-downloader, shadow-api, secrets]
---

# 🔍 SKILL: JavaScript AST Endpoint & Secret Analyzer

Статический синтаксический анализатор (AST / Lexical Parser) для JavaScript/TypeScript веб-бандлов, SPAs и клиентских скриптов, вдохновленный архитектурой `BishopFox/jsluice`.

---

## 🎯 Архитектура и Принципы

1. **AST-Based Reconstruction (Склейка составных URL):**
   - Автоматически склеивает конкатенированные строки: `'https://cdn.host/' + id + '/master.m3u8'` ➔ `https://cdn.host/{id}/master.m3u8`.
   - Разворачивает ES6 шаблонные строки: `` `${API_BASE}/api/v2/items/${id}` `` ➔ `{API_BASE}/api/v2/items/{id}`.
2. **Анализ вызовов и маршрутов:**
   - Извлекает эндпоинты из `fetch()`, `axios()`, `$.ajax()`, `XMLHttpRequest`, и конфигураций роутеров (`routes: [...]`).
3. **Обнаружение секретов с энтропийной фильтрацией:**
   - Поиск AWS ключей, Google API, JWT токенов, GitHub PAT, Telegram бот-токенов, Stripe ключей.
   - Расчет энтропии Шеннона ($H \ge 3.8$) с отсечением ложных срабатываний (CSS-цвета, Webpack-идентификаторы).
4. **Интерактивный HTML Visual Audit Dashboard:**
   - Генерация отчета с поиском, фильтрацией по категориям (Media, REST, Internal, Secrets) и цветовой подсветкой.

---

## 🚀 Применение в Проектах Команды

### 1. 🎬 `media-downloader` (Фаза 0: Spike & Reverse Engineering)
- Реверс-инжиниринг обфусцированных Webpack-бандлов веб-плееров онлайн-кинотеатров.
- Мгновенное извлечение CDN-доменов, скрытых путей манифестов `.m3u8` / `.mpd` и эндпоинтов DRM-лицензирования (`/widevine/license`).

```bash
python "scripts/js_ast_analyzer.py" "path/to/player.bundle.js" --mode media
```

### 2. 🛡️ `sentinel-osint` (Client Bundle Auditing & Threat Intelligence)
- Автоматический аудит веб-сервисов и SPA-приложений.
- Обнаружение недокументированных shadow-API, скрытых админских панелей (`/admin/internal/...`) и утекших токенов разработчиков.

```bash
python "scripts/js_ast_analyzer.py" "target_app.js" --mode secrets --html "audit_report.html"
```

### 3. 📱 `SmartphoneMonitor` (Direct API Discovery)
- Поиск прямых JSON REST/GraphQL эндпоинтов в скриптах досок объявлений (999.md, Avito) для создания надежных прямых API-клиентов вместо ломкого парсинга HTML DOM.

```bash
python "scripts/js_ast_analyzer.py" "classifieds_app.js" --mode urls --json
```

---

## 💻 Программный интерфейс (Python API)

```python
from js_ast_analyzer import JsAstAnalyzer, generate_html_audit_report

analyzer = JsAstAnalyzer()
result = analyzer.analyze_file("bundle.js")

# Извлеченные медиа-потоки для плеера
for stream in result.media_streams:
    print(f"Stream: {stream.url} ({stream.source_type})")

# Найденные секреты
for sec in result.secrets:
    print(f"Secret: {sec.secret_type} -> {sec.value_preview} (Entropy: {sec.entropy})")

# Генерация HTML-дашборда
generate_html_audit_report(result, "audit_dashboard.html")
```
