# lesson worked examples

## 1. Saving a user correction as an imperative rule

User: "Never run cargo test without --locked, otherwise Cargo updates the lockfile and breaks CI."

Invocation:

```json
memory_lesson_save {
  "content": "Always run cargo test with --locked; omitting it modifies Cargo.lock and breaks deterministic CI builds.",
  "context": "running cargo test, local test suites, or CI pipelines",
  "confidence": 0.7,
  "project": "core-engine"
}
```

Response:

```json
{ "id": "les_9a41b2", "saved": true, "confidence": 0.7 }
```

Present:

> Lesson saved with confidence 0.7: "Always run cargo test with --locked; omitting it modifies Cargo.lock and breaks deterministic CI builds." Fires on cargo test / CI work.

## 2. Distilling a self-observed bug into a behavioral rule

Observation during session: Agent tried to use relative paths with symlinks in Rust, hitting permission and canonicalization issues.

Invocation:

```json
memory_lesson_save {
  "content": "Canonicalize file paths with std::fs::canonicalize and verify resolved_path.starts_with(allowed_root) before reading or writing files.",
  "context": "filesystem operations, file reading, path traversal protection",
  "confidence": 0.5
}
```

Response:

```json
{ "id": "les_c184ef", "saved": true, "confidence": 0.5 }
```

Present:

> Recorded behavioral lesson (confidence 0.5): Canonicalize paths and verify `starts_with(allowed_root)` to prevent traversal and symlink escapes.

## 3. Strengthening an existing lesson upon repeat correction

User: "I told you earlier, always use --run with vitest!"

Invocation (reusing exact prior content to increase confidence):

```json
memory_lesson_save {
  "content": "Run vitest with --run in CI contexts; bare vitest enters watch mode and hangs the pipeline.",
  "context": "any script or CI step that invokes vitest",
  "confidence": 0.7,
  "project": "frontend"
}
```

Response:

```json
{ "id": "les_vitest_01", "saved": true, "confidence": 0.85, "strengthened": true }
```

Present:

> Re-applied rule: Vitest must be run with `--run`. Confidence strengthened to 0.85.
