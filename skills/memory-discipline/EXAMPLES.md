# memory-discipline worked examples

## 1. Task start: Memory check before reading code

Scenario: User asks to fix race conditions in WebSocket connection handling.

Agent action (First tool call before reading 20 files):

```json
memory_smart_search {
  "query": "websocket reconnect race condition",
  "project": "telemetry-hub",
  "limit": 5
}
```

Outcome:
- Hit found: Past session resolved that exponential backoff with jitter is required, and WebSocket ping interval must stay at 15s.
- Agent saves 30 minutes of re-investigation and proceeds directly with the established pattern.

## 2. Settled decision: Save immediately with the "WHY"

Scenario: During debugging of SQLite concurrency errors in `src/db/pool.rs`, agent switches database to WAL mode.

Agent action (Immediately at resolution time, NOT at session end):

```json
memory_save {
  "content": "Switched SQLite connection pool to PRAGMA journal_mode=WAL and busy_timeout=5000 to eliminate 'database is locked' errors during concurrent multi-threaded writes.",
  "concepts": "sqlite-wal-mode, busy-timeout, connection-pool-concurrency",
  "files": "src/db/pool.rs"
}
```

Outcome:
- Exact reason and file path persisted. Future sessions know why WAL mode was chosen and will not accidentally revert it.

## 3. User correction: Lesson instead of fact

Scenario: User says: "Don't use unwrap() in Tauri IPC commands, always return Result<T, AppError>."

Agent action:

```json
memory_lesson_save {
  "content": "Never call unwrap() or expect() in Tauri command handlers; return Result<T, AppError> with typed error variants to avoid crashing the GUI webview process.",
  "context": "tauri ipc commands, rust error handling, frontend invoke handlers",
  "confidence": 0.7,
  "project": "media-downloader"
}
```

Outcome:
- Behavioral correction saved with confidence 0.7. Resurfaces automatically before future Tauri command development.
