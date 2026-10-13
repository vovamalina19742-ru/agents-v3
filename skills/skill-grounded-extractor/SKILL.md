---
name: skill-grounded-extractor
description: Google LangExtract-inspired structured information extraction engine with source grounding (verbatim quotes, char offsets, zero hallucination) and interactive HTML visual audit.
version: 1.0.0
author: Antigravity Team
tags: [extraction, langextract, osint, ecommerce, classifieds, nlp, source-grounding]
---

# 📑 Google LangExtract Source-Grounded Information Extractor

Библиотека и агентный навык для прецизионного извлечения структурированных данных (JSON/схем) из длинных неструктурированных документов **со 100% привязкой к исходному тексту (Source Grounding)**.

## 🎯 Назначение и Архитектура

Традиционный LLM-парсер страдает от «тихих галлюцинаций» (модель может выдумать цену, артикул, дефект или телефон). 
`skill-grounded-extractor` решает эту проблему на корню:
1. **Source Grounding**: Каждое извлеченное поле жестко связывается с точными смещениями символов `[char_start : char_end]` и оригинальной цитатой в источнике.
2. **Auto-Verification**: Встроенный метод `verify_against_text()` сверяет срез строки и отбрасывает сущности, которых нет в исходном тексте.
3. **Interactive HTML Visualizer**: Автоматическая генерация HTML-отчета с цветовой подсветкой категорий и интерактивным инспектором доказательной базы.

## 🛠 Поддерживаемые Модули

1. **`ClassifiedsGroundedExtractor` (E-Commerce / Avito / SmartphoneMonitor)**:
   - Объем памяти (RAM/ROM в ГБ)
   - Состояние батареи (АКБ %)
   - Заявленная цена (RUB)
   - Список дефектов (экран, FaceID, замененные детали, вскрытия)
   - Триггеры мошенничества (предоплата, увод в сторонние мессенджеры, фейковые курьеры)

2. **`OsintGroundedExtractor` (Cyber Intelligence / sentinel-osint)**:
   - Номера телефонов (E.164)
   - Email-адреса
   - Telegram юзернеймы (@handle / t.me)
   - Криптокошельки (BTC, ETH/EVM, TRON/TRC20, TON)
   - Публичные IPv4 адреса

3. **`MediaTranscriptGroundedExtractor` (media-downloader / AI Summarizer)**:
   - Ключевые цитаты спикера
   - Выводы и результаты тестов
   - Упомянутые ссылки и репозитории

## 💻 Использование

```python
from grounded_extractor import ClassifiedsGroundedExtractor, OsintGroundedExtractor, MediaTranscriptGroundedExtractor

# 1. E-Commerce / Avito
extractor = ClassifiedsGroundedExtractor()
result = extractor.extract("iPhone 15 Pro Max 256гб. АКБ 89%. Есть трещина на экране. Цена 65 000 руб.", title="iPhone 15 Pro")
print(result.summary)
result.generate_html_report("audit_report.html")

# 2. OSINT
osint_ext = OsintGroundedExtractor()
osint_res = osint_ext.extract("Связь в TG @ops_sec, оплата BTC 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
print(osint_res.to_dict())
```
