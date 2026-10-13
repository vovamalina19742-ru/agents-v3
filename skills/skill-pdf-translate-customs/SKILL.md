---
name: pdf-translate-customs
description: Автоматический перевод коммерческих инвойсов и спецификаций европейских фабрик на румынский язык для молдавской таможни (Vama Chișinău). Генерация официальной Factură Proformă в PDF и спецификации с кодами ТН ВЭД (Cod Tarifar Vamal / HS Codes: 9405, 8504, 7604) в Excel.
---

# PDF Translate Customs — Молдавский таможенный шлюз (Vama Chișinău)

Специализированный навык для внешнеэкономической деятельности и логистики Smart Light (Молдова):
- Автоматический перевод итальянской, английской и немецкой светотехнической номенклатуры (Lombardo, NEKO, Nova Luce, Louis Poulsen) на официальный румынский язык.
- Интеллектуальное присвоение кодов ТН ВЭД (Cod Tarifar Vamal / HS Codes conform Nomenclaturii Combinate a Marfurilor RM):
  - `9405 11 00 00`: Светильники LED потолочные, споты для шины, подвесы.
  - `9405 42 39 00`: Светодиодные ленты flex 24V.
  - `9405 99 00 00`: Магнитные шинопроводы 48V и аксессуары (коннекторы, заглушки).
  - `8504 40 83 90`: Электронные блоки питания (драйверы LED 24V / 700mA).
  - `7604 29 90 00`: Алюминиевые профили с поликарбонатным рассеивателем.
- Генерация юридически чистых документов:
  - **`Factură Proformă` (PDF):** Двуязычный бланк с реквизитами Smart Light SRL, фабрики-поставщика, номерами CMR и автотранспорта, разбивкой нетто/брутто и блоком подписей/печатей.
  - **`Specificație Vamală` (XLSX):** Официальное приложение к таможенной декларации для брокеров (Vama Centru / Poșta / Terminal Petricani).

---

## 🚀 Быстрый запуск

```bash
python .agents/skills/skill-pdf-translate-customs/scripts/customs_translator.py \
  --input projects/apartament_chisinau_89m2/BOM_v3.json \
  --out-xlsx projects/apartament_chisinau_89m2/Specificatie_Vamala_Andreea.xlsx \
  --out-pdf projects/apartament_chisinau_89m2/Factura_Proforma_Andreea.pdf
```
