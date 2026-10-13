---
name: skill-osint-ai
description: Advanced OSINT & AI Cyber Intelligence Workflow for open-source data gathering, footprinting, username/email verification, and privacy hygiene.
---

# OSINT & AI Cyber Intelligence Workflow (`skill-osint-ai`)

## Overview
This skill provides structured, ethical Open-Source Intelligence (OSINT) and AI-assisted investigation playbooks derived from industry references (*«Бизнес-разведка 3.0 + OSINT и AI»*, *«OSINT. Руководство по сбору и анализу открытой информации»*).

---

## 🗺 1. Investigation Methodology (Pivoting Pipeline)

### Phase 1: Name Transliteration & Hypothesis Generation
When starting with a name or target handle:
1. Generate standard transliterations (Cyrillic <-> Latin).
2. Produce standard email/username permutation matrices:
   - `first.last`, `f.last`, `last.f`, `first_last`, `firstlast99`

### Phase 2: Autonomous Registration Verification (Non-Attributable)
- Use **`Holehe`** to check email registrations across 120+ platforms without password attempts.
- Use **`user-scanner`** / **`Maigret`** for username footprinting across 225+ social and technical networks.
- Use **`Robin`** for dark web threat intelligence querying.

### Phase 3: Search Dorks & Public Registries
- Domain WHOIS & DNS records.
- Search engine dorks: `site:github.com "target_username"`, `site:t.me "target"`.

---

## 🛡 2. Digital Hygiene & Privacy Protection Rules

1. **Log Scrubbing:** Never commit raw API session logs or signed `thinking` signature blocks containing credentials or PII to public git repositories.
2. **Context Separation:** Keep target investigation data isolated within sandbox environments (REMnux VM at `192.168.100.22`).
3. **Data Protection:** Securely delete intermediate investigation outputs after summarizing findings.
