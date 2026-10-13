---
name: invoice-scanner-organizer
description: Автоматическая сверка и организация счетов-фактур (Invoices) и упаковочных листов (Packing Lists) европейских фабрик (Lombardo, NEKO, Nova Luce, KRAAB) с внутренней спецификацией проекта. Контроль расхождений цен (Δ EUR), количества, веса (нетто/брутто), номеров коробок (Carton No) и шлюза CMR/T1 для молдавской таможни.
---

# Invoice Scanner & Organizer — Контроль фабричных поставок Smart Light

Специализированный навык для отдела закупок и логистики (Project Lighting Manager):
- **Сверка цен и номенклатуры (Order vs Invoice):** Мгновенное выявление завышения фабричных цен, недопоставок, лишних артикулов или самовольной замены модификаций (например, оптики 24° вместо 36°).
- **Сверка упаковочных листов (Packing List vs Invoice):** Привязка каждого артикула к физической коробке (`Carton No` / `Colli`) для быстрой разгрузки на складе в Кишиневе и таможенного досмотра.
- **Шлюз логистической безопасности (Logistics Cross-Check Gate):**
  $$\text{Коробок в CMR} == \text{Коробок в T1} == \text{Коробок в Packing List} == \text{Коробок по инвойсам}$$
- **Форматы отчетов:**
  - `Reconciliation_Report.md`: Управленческая записка с вердиктом (APROBAT / STOP).
  - `Reconciliation_Report.json`: Машиночитаемые данные для ERP/CRM.
  - `Reconciliation_Matrix.xlsx`: Цветная матрица сверки (зеленый / желтый / красный) с живыми расчетами дельт.

---

## 🚀 Быстрый запуск

```bash
python .agents/skills/skill-invoice-scanner-organizer/scripts/invoice_scanner.py \
  --order projects/apartament_chisinau_89m2/BOM_v3.json \
  --invoice .agents/skills/skill-invoice-scanner-organizer/examples/sample_factory_invoice.json \
  --out-json projects/apartament_chisinau_89m2/Reconciliation_Report.json \
  --out-xlsx projects/apartament_chisinau_89m2/Reconciliation_Matrix.xlsx \
  --out-md projects/apartament_chisinau_89m2/Reconciliation_Report.md
```
