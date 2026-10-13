---
trigger: always_on
description: "RTK (Rust Token Killer): все shell-команды выполнять через префикс rtk — сжатие вывода до контекста, экономия 60–90% токенов."
---

# RTK - Rust Token Killer (Google Antigravity)

**Usage**: Token-optimized CLI proxy for shell commands.

## Rule

Always prefix shell commands with `rtk` to minimize token consumption.

Examples:

```bash
rtk git status
rtk cargo test
rtk ls src/
rtk grep "pattern" src/
rtk find "*.rs" .
rtk docker ps
rtk gh pr list
```

## Meta Commands

```bash
rtk gain              # Show token savings
rtk gain --history    # Command history with savings
rtk discover          # Find missed RTK opportunities
rtk proxy <cmd>       # Run raw (no filtering, for debugging)
```

## Why

RTK filters and compresses command output before it reaches the LLM context, saving 60-90% tokens on common operations. Always use `rtk <cmd>` instead of raw commands.

## Исключения (PowerShell & Raw CLI)

* **Встроенные командлеты PowerShell**: Префикс `rtk` предназначен для внешних исполняемых утилит (`git`, `cargo`, `pytest`, `ruff`, `python`, `docker`, `gh`, `npm`, `grep`, `find`). **НЕ используйте `rtk`** перед встроенными командлетами PowerShell (`Select-String`, `Get-ChildItem`, `Get-Content`, `Test-Path`, `Set-Content`), так как PowerShell не сможет передать их внешнему процессу.
* **Неискажённый вывод (Raw Data)**: Если требуется точный дамп без сжатия строк (JSON-контракты, сырые diff), используйте `rtk proxy <cmd>`.
