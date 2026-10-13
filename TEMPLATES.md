# ШАБЛОНЫ СПЕЦИФИКАЦИЙ И КОНТРАКТОВ (TEMPLATES)
## Проект: Универсальный комбайн для медиа-загрузок (Media Downloader Desktop)

---

### 1. ШАБЛОН IPC-КОНТРАКТА (`ipc_contracts_TECH.md`)

```markdown
# IPC Контракт — <module_name>

## 1. Строгая типизация ошибок (AppError)
Все IPC-команды возвращают строго типизированное и сериализуемое перечисление `AppError`:

```rust
use serde::Serialize;

#[derive(Debug, Serialize, thiserror::Error)]
#[serde(tag = "error_code", content = "message")]
pub enum AppError {
    #[error("Невалидный URL: {0}")]
    InvalidUrl(String),
    #[error("Недостаточно места на диске")]
    DiskFull,
    #[error("Таймаут сетевого соединения")]
    NetworkTimeout,
    #[error("Контент защищен DRM (Widevine/PlayReady)")]
    DrmProtected,
    #[error("Попытка выхода за пределы разрешенной директории")]
    PathTraversalDenied,
    #[error("Неавторизованная команда")]
    UnauthorizedCommand,
    #[error("Ошибка базы данных: {0}")]
    DatabaseError(String),
}
```

---

## 2. Команда: `<command_name>`
**Описание:** <краткое описание назначения функции>

**Входные данные (TypeScript):**
```typescript
interface <CommandName>Input {
  url: string;
  save_path: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  speed_limit?: number; // KB/s, 0 = без ограничений
}
```

**Выходные данные (TypeScript):**
```typescript
interface <CommandName>Output {
  file_path: string;
  metadata?: {
    duration: number;
    size: number;
    format: string;
  };
}

// Тип ошибки, получаемый на фронтенде в catch(err)
interface AppError {
  error_code: 'InvalidUrl' | 'DiskFull' | 'NetworkTimeout' | 'DrmProtected' | 'PathTraversalDenied' | 'UnauthorizedCommand' | 'DatabaseError';
  message?: string;
}
```

**Rust-соответствие (Tauri v2 Command):**
```rust
#[derive(Serialize, Deserialize)]
pub struct <CommandName>Input {
    pub url: String,
    pub save_path: String,
    pub priority: Priority,
    pub speed_limit: Option<u64>,
}

#[tauri::command]
pub async fn <command_name>(input: <CommandName>Input) -> Result<<CommandName>Output, AppError> {
    // Валидация входных данных
    if input.url.is_empty() {
        return Err(AppError::InvalidUrl("URL не может быть пустым".into()));
    }
    
    // Выполнение логики команды
    Ok(<CommandName>Output {
        file_path: input.save_path,
        metadata: None,
    })
}
```

**Вызов и обработка на Фронтенде (React / TypeScript):**
```typescript
import { invoke } from '@tauri-apps/api/core';

try {
  const result = await invoke<<CommandName>Output>('<command_name>', { input });
  console.log('Успешная загрузка:', result.file_path);
} catch (error) {
  // Фронтенд сразу получает структурированный объект { error_code: "...", message?: "..." }
  const appError = error as AppError;
  switch (appError.error_code) {
    case 'DrmProtected':
      showNotification('Загрузка невозможна: контент защищен DRM', 'warning');
      break;
    case 'DiskFull':
      showNotification('Недостаточно свободного места на диске', 'error');
      break;
    case 'PathTraversalDenied':
      showNotification('Ошибка безопасности: запрещенный путь сохранения', 'error');
      break;
    default:
      showNotification(appError.message || 'Произошла ошибка при выполнении', 'error');
  }
}
```
```

---

### 2. ШАБЛОН СХЕМЫ БАЗЫ ДАННЫХ (`db_schema_TECH.md`)

```markdown
# Схема Базы Данных SQLite — <module_name>

## Таблица: `downloads`
```sql
CREATE TABLE IF NOT EXISTS downloads (
    id TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    title TEXT,
    save_path TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('queued', 'downloading', 'paused', 'completed', 'error')),
    progress REAL DEFAULT 0.0,
    total_bytes INTEGER DEFAULT 0,
    downloaded_bytes INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_downloads_status ON downloads(status);
```

## Миграции (rusqlite_migration):
```rust
let migrations = Migrations::new(vec![
    M::up(
        "CREATE TABLE downloads (id TEXT PRIMARY KEY, url TEXT NOT NULL, save_path TEXT NOT NULL, status TEXT NOT NULL);"
    ),
    M::up(
        "ALTER TABLE downloads ADD COLUMN total_bytes INTEGER DEFAULT 0;"
    ),
]);
```
```

---

### 3. ШАБЛОН МОДЕЛИ ОЧЕРЕДИ (`queue_model_TECH.md`)

```markdown
# Модель Приоритетной Очереди Загрузок

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub enum Priority {
    Low = 0,
    Medium = 1,
    High = 2,
    Critical = 3,
}

pub struct DownloadTask {
    pub id: String,
    pub url: String,
    pub save_path: PathBuf,
    pub priority: Priority,
    pub created_at: Instant,
}
```
```
