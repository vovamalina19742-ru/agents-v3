# agentmemory-architecture reference

## 1. Engine & Port Topology

| Service | Default Port | Formula | Purpose |
| :--- | :--- | :--- | :--- |
| **REST API** | `3111` | `Base (3111)` | HTTP endpoints for memory capture, search, and recall |
| **SSE Streams** | `3112` | `Base + 1` | Real-time observation events & live streaming updates |
| **Web Viewer** | `3113` | `Base + 2` | Interactive visual dashboard showing sessions & memory graph |
| **iii Engine Core** | `49134` | `Base + 46023` | Underlying RPC worker engine routing function triggers |

*Instance shifting:* Passing `--instance N` shifts the whole port block by `N * 100` (e.g., instance 1 runs REST on 3211, Viewer on 3213).

## 2. Storage & Hybrid Retrieval Architecture

```
                    ┌───────────────────────────────┐
                    │  User Prompt / Task Context   │
                    └───────────────┬───────────────┘
                                    │
                         Hybrid Search Pipeline
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
             ┌────────────┐  ┌─────────────┐  ┌────────────┐
             │ BM25 FTS   │  │ Dense Vector│  │ Graph Ring │
             │ Exact Lex  │  │ Embeddings  │  │ Concepts   │
             └──────┬─────┘  └──────┬──────┘  └─────┬──────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    ▼
                         RRF Score Fusion & Rank
                                    ▼
                    ┌───────────────────────────────┐
                    │ Ranked Relevant Memory Context│
                    └───────────────────────────────┘
```

## 3. Function & Trigger Namespaces

All operations are registered directly into the `iii` engine runtime:

- `mem::save` / `api::save`: Ingestion of observations and decisions.
- `mem::recall` / `api::recall`: Hybrid search over concepts and content.
- `mem::lesson_save`: Confidence-weighted behavioral rule storage.
- `mem::consolidate`: Periodic compaction and graph node clustering.
- `mem::audit`: Verification of integrity and storage bounds.
