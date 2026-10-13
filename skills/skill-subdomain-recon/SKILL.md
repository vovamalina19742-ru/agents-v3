---
name: skill-subdomain-recon
description: "Sublist3r & Certificate Transparency-inspired passive subdomain intelligence, digital perimeter mapping, and CDN edge node discovery for Sentinel-OSINT, Media Downloader, and SmartphoneMonitor."
version: 1.0.0
author: Antigravity Team
tags: [sublist3r, subdomain, recon, osint, cdn, perimeter, attack-surface-management, certificate-transparency]
---

# 🌐 SKILL: Subdomain Reconnaissance & Perimeter Mapping

Модуль пассивной разведки цифрового периметра, поиска субдоменов и обнаружения скрытых CDN-узлов и теневых API, вдохновленный архитектурой `Sublist3r` и Certificate Transparency (crt.sh).

---

## 🎯 Архитектура и Возможности

1. **Zero-Traffic Passive Reconnaissance:**
   - Сбор поддоменов через Certificate Transparency Logs (`crt.sh`, `HackerTarget`) без единого сетевого запроса к целевой инфраструктуре.
2. **Многопоточный DNS & Port Probing:**
   - Высокоскоростной резолв A/CNAME записей и проверка доступности портов 80 (HTTP) и 443 (HTTPS) с замером задержки (`ms`).
3. **Автоматическая типизация активов (Asset Categorization):**
   - 🎬 **`media_cdn`**: узлы раздачи видео, CDN-эджи, стримы (`cdn.*`, `edge-01.*`, `hls.*`, `stream.*`).
   - 🌐 **`api_gateway`**: мобильные и скрытые API (`mobile-api.*`, `graphql.*`, `gateway.*`, `v2.*`).
   - 🛡️ **`internal_dev`**: тестовые и внутренние контуры (`dev.*`, `staging.*`, `admin.*`, `grafana.*`, `swagger.*`).
   - 🔑 **`auth_service`**: сервисы аутентификации и SSO (`auth.*`, `login.*`, `id.*`, `oauth.*`).
4. **Интерактивный дашборд:**
   - Экспорт в темный HTML Visual Perimeter Dashboard для мгновенного аудита.

---

## 🚀 Применение в Проектах Команды

### 1. 🛡️ `sentinel-osint` (Digital Perimeter & Attack Surface Management)
- Обнаружение забытых staging/dev серверов (`staging-api.target.com`, `admin-test.target.com`), внутренних метрик (Grafana, Swagger) и CNAME-записей до инцидента.

```bash
python "scripts/subdomain_recon.py" "target.com" --html "perimeter_report.html"
```

### 2. 🎬 `media-downloader` (Phase 0 Spike & Multi-Mirror Acceleration)
- Поиск всех региональных CDN-нод видеохостинга (`edge-01.cdn.target.com`, `ams-stream.target.com`) для выбора наименее загруженного зеркала и обхода троттлинга.

```bash
python "scripts/subdomain_recon.py" "streaming-service.net" --json
```

### 3. 📱 `SmartphoneMonitor` (Mobile & Shadow API Discovery)
- Поиск незащищенных мобильных шлюзов (`mobile-api.target.md`, `graphql.target.md`), где отсутствуют жесткие Cloudflare JS-капчи, для надежного сбора рыночных цен.

```bash
python "scripts/subdomain_recon.py" "classifieds.md" --no-probe --json
```
