---
name: diagram-design
description: Создание презентационных визуальных диаграмм журнального качества (Editorial Diagrams) в формате чистого HTML/SVG без сторонних библиотек и без "Mermaid-slop". 41 тип диаграмм (архитектура, электрические потоки, логистические цепочки, временные шкалы, ER-модели) с поддержкой фирменного стиля Smart Light.
---

# Diagram Design — Стандарт журнальной визуализации Smart Light

Создание презентационных векторных диаграмм и схем в формате автономных `.html` и `.svg` файлов.
Никаких кривых стрелок Mermaid, перегруженных рамок и тяжелых зависимостей. Чистый HTML + встроенный SVG.

---

## 🎨 1. Цветовая палитра Smart Light (Design System Tokens)

Диаграммы оформляются в фирменном стиле компании:
* **Background (Фон):** `#F8FAFC` (Slate Light) или `#0F172A` (Dark Mode);
* **Borders & Shapes (Контуры и карточки):** `#E2E8F0` / `#1E293B`;
* **Primary Ink (Основной текст):** `#0F172A` / `#F1F5F9`;
* **Secondary Ink (Пояснения, артикулы):** `#64748B` / `#94A3B8`;
* **Accent Coral / Orange (Главный фокус):** `#EA580C` (Smart Light Orange) — выделяет только 1–2 ключевых узла.

---

## 📐 2. Основные типы диаграмм для наших задач:

1. **Электротехническая схема (Architecture / Data Flow):**
   * Распределение питания: `Щит 230V ➔ Кабель ВВГнг-LS 3x2.5 ➔ Драйвер 48V/200W ➔ Магнитный трек Insight ➔ Споты 15W / Ленты LED`.
   * Падение напряжения $\Delta U\% \le 3.0\%$.
2. **Логистическая цепочка (Process / Swimlane):**
   * Маршрут поставки: `Фабрика (Италия, EXW) ➔ Перевозчик ➔ Оформление T1/CMR ➔ Таможня (Vama Chișinău) ➔ Склад Smart Light (str. Pajurii 11)`.
3. **Архитектура вычислительного кластера (Deployment / Infrastructure):**
   * Взаимодействие: `Ноутбук координатора ⟷ Сетевой кэш (SMB) ⟷ Linux Mint Server 24/7 (192.168.100.22) ⟷ Клиентские агенты`.
4. **Временная шкала проекта (Timeline / Gantt):**
   * Этапы реализации: `Согласование сметы (3 дня) ➔ Размещение заказа на фабрике (2 дня) ➔ Производство и логистика (20 дней) ➔ Таможенная очистка (1 день) ➔ Монтаж и пусконаладка (2 дня)`.

---

## 🛠️ 3. Пример минимального автономного HTML/SVG шаблона:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #F8FAFC; margin: 0; padding: 24px; display: flex; justify-content: center; }
  .diagram-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); padding: 24px; max-width: 900px; width: 100%; }
  .title { font-size: 18px; font-weight: 700; color: #1E293B; margin-bottom: 4px; }
  .subtitle { font-size: 13px; color: #64748B; margin-bottom: 20px; }
  svg text { font-family: inherit; }
</style>
</head>
<body>
<div class="diagram-card">
  <div class="title">Схема питания магнитной трековой системы 48V</div>
  <div class="subtitle">Smart Light — Проект квартиры 89 м² (Andreea)</div>
  <svg viewBox="0 0 800 240" width="100%" height="auto">
    <!-- Блок Щит -->
    <rect x="20" y="70" width="160" height="90" rx="8" fill="#F1F5F9" stroke="#CBD5E1" stroke-width="1.5"/>
    <text x="100" y="105" text-anchor="middle" font-size="13" font-weight="700" fill="#1E293B">Электрощит 230V</text>
    <text x="100" y="125" text-anchor="middle" font-size="11" fill="#64748B">Автомат 16A (C)</text>

    <!-- Стрелка 1 -->
    <path d="M 180 115 L 260 115" stroke="#94A3B8" stroke-width="2" marker-end="url(#arrow)"/>
    <text x="220" y="105" text-anchor="middle" font-size="9" fill="#EA580C" font-weight="600">3x2.5 mm²</text>

    <!-- Блок Драйвер -->
    <rect x="260" y="60" width="180" height="110" rx="8" fill="#1E293B" stroke="#0F172A" stroke-width="1.5"/>
    <text x="350" y="95" text-anchor="middle" font-size="13" font-weight="700" fill="#FFFFFF">Блок питания 48V</text>
    <text x="350" y="115" text-anchor="middle" font-size="11" fill="#CBD5E1">MeanWell / 200W</text>
    <text x="350" y="135" text-anchor="middle" font-size="10" fill="#EA580C" font-weight="600">ΔU = 1.2% (OK)</text>

    <!-- Стрелка 2 -->
    <path d="M 440 115 L 520 115" stroke="#94A3B8" stroke-width="2" marker-end="url(#arrow)"/>
    <text x="480" y="105" text-anchor="middle" font-size="9" fill="#64748B">DC 48V</text>

    <!-- Блок Трек -->
    <rect x="520" y="70" width="240" height="90" rx="8" fill="#F1F5F9" stroke="#CBD5E1" stroke-width="1.5"/>
    <text x="640" y="105" text-anchor="middle" font-size="13" font-weight="700" fill="#1E293B">Шина Insight 48V</text>
    <text x="640" y="125" text-anchor="middle" font-size="11" fill="#64748B">9 спотов 15W (L=8.0м)</text>

    <defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 10 5 L 0 9 z" fill="#94A3B8"/>
      </marker>
    </defs>
  </svg>
</div>
</body>
</html>
```
