---
name: skill-playwright-stealth
description: "Microsoft Playwright Headless Automation & Stealth WAF Bypass. Скрапинг динамических веб-страниц, обход Cloudflare/капчи, генерация PDF-отчетов и автоматизация досок объявлений."
---

# 🌐 SKILL: Playwright Stealth Automation

## 📌 Назначение
Управление headless-браузером для парсинга современных динамических SPA-сайтов, досок объявлений (999.md, Avito), каталогов товаров (светильники One Light) и обхода защит от ботов.

---

## ⚡ 1. Анти-детект и стелс-режим (Stealth Patterns)
* **Аппаратные фингерпринты:** Использование нативных генераторов отпечатков (`browserforge`, `camoufox`) вместо примитивной подмены User-Agent.
* **Маскировка флагов:** Скрытие `navigator.webdriver`, подделка WebGL вендора/рендерера, синхронизация таймзон и языков (`ru-RU, en-US`).
* **Рандомизация задержек (Jitter):** Паузы между кликами и скроллом $400 \pm 150$ мс, кривые Безье для движений мыши.
* **Селекторы данных:** Использовать устойчивые атрибуты (`data-testid`, `role`, точные CSS/XPath селекторы) вместо хрупких сгенерированных классов.

---

## 🧪 2. Полигоны проверки стелс-профиля (Detection Testbeds)
Перед запуском боевого скрапера на целевые сайты — обязательная верификация на тестовых полигонах (из реестра `untidetect-tools`):
1. **CreepJS (`https://abrahamjuliot.github.io/creepjs/`):** Проверка на несоответствия в прототипах и JS-инжектах. Рейтинг лжи должен быть 0%.
2. **Rebrowser Bot Detector (`https://bot-detector.rebrowser.net/`):** Проверка Runtime-патчей CDP (Chrome DevTools Protocol) и утечек автоматизации.
3. **BrowserLeaks (`https://browserleaks.com/canvas`):** Проверка уникальности Canvas, WebRTC (утечки реального IP) и аудио-хэшей.
4. **Sannysoft Bot Test (`https://bot.sannysoft.com/`):** Быстрый аудит ключевых флагов Chrome/Firefox.

---

## 📄 3. Экспорт документов и снимков
* Генерация скриншотов высокого разрешения (`--window-size=1280,800`, `fullPage: true`).
* Экспорт веб-страниц и каталогов в PDF с сохранением стилей печати `@media print`.

