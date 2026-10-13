---
name: skill-supply-chain-manifest
description: Deterministic SHA-256 Chain-Hash generator & supply chain integrity verifier for sidecars, plugins, and compiled binaries.
version: 1.0.0
last_verified_date: 2026-09-08
success_rate: 100%
---

# 🛡 Supply Chain Integrity & Manifest Validator

Обеспечивает сквозной аудит целостности скомпилированных Sidecar-бинарников (Nuitka/PyInstaller), WASM-плагинов и внешних инструментов в соответствии с принципами безопасности `AGENTS.md` v2.7.1 и шаблонами `agent-supply-chain`.

---

## 🔬 Как это работает

```
Каталог плагина/Sidecar → Вычисление SHA-256 каждого файла → Сортировка → Конкатенация → Итоговый Chain-Hash
                                                                                               ↓
Верификация: Текущее состояние файлов → Пересчет Chain-Hash ⟷ Сверка с manifest_hash → [MATCH / TAMPERED]
```

---

## 🛠 Запуск инструмента

### 1. Генерация манифеста целостности:
```bash
python "d:\Создание программ\scripts\verify_sidecars.py" "<путь_к_папке>"
```

### 2. Программное использование в Python:
```python
from scripts.verify_sidecars import SupplyChainVerifier

verifier = SupplyChainVerifier("media-downloader/sidecars")
manifest = verifier.generate_manifest(output_manifest_path="media-downloader/sidecars/sidecar.manifest.json")

# Проверка
result = verifier.verify_manifest("media-downloader/sidecars/sidecar.manifest.json")
if not result["valid"]:
    raise SecurityError(f"Обнаружена подмена бинарников: {result['mismatched']}")
```

---

## 💡 Чеклист безопасности
- [ ] Все бинарники в `sidecars/` имеют зафиксированные контрольные суммы.
- [ ] При старте приложения бэкенд на Rust/Python проверяет хэш перед вызовом процесса.
- [ ] При несовпадении хэша вызывается аварийная остановка (HITL).
