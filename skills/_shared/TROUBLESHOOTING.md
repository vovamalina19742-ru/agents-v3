# agentmemory troubleshooting (shared)

Referenced by the agentmemory skills. If a memory tool is missing or a search
returns nothing, walk this list from top to bottom before giving up.

## 1. Tools are not available at all

The host is not wired to the memory server. Wire it and restart the host:

- Antigravity 2.0 / IDE: `agentmemory connect antigravity --with-hooks`
- Antigravity CLI (agy):  `agentmemory connect antigravity-cli --with-hooks`

Verify that `~/.gemini/config/mcp_config.json` (global) or `.agents/mcp_config.json`
(workspace) contains the `agentmemory` entry, and that other servers were preserved.

## 2. Only a few tools, or "shim cannot reach server"

The MCP shim is running but the daemon is not. Start it:

- `agentmemory` (or `npx -y @agentmemory/agentmemory@latest`)
- Check: `agentmemory status` and `curl http://localhost:3111/agentmemory/health`
- Viewer: http://localhost:3113

## 3. Recall finds nothing

- Keyless mode is BM25-only. For semantic recall set `EMBEDDING_PROVIDER=local`
  in `~/.agentmemory/.env` and restart the daemon (the first request downloads
  the local MiniLM embedding model).
- Confirm the active mode: `agentmemory status` prints provider/embedding mode.

## 4. Nothing is captured automatically

- Check `~/.gemini/config/hooks.json` (global) or `.agents/hooks.json` (workspace).
  Re-run connect with `--with-hooks` and restart the host.
- Native Windows hook execution is not fully verified; WSL2 or Docker Desktop are
  the supported paths. Keep the installed package path free of spaces.

## 5. Stale or duplicated config

- Older connectors wrote IDE config into an app-support directory; after upgrades
  re-run `agentmemory connect antigravity --force` and remove stale entries.
  Other servers and hook bundles are preserved; re-apply custom values afterwards.

## 6. Still broken

- `agentmemory doctor` (interactive fixer; `--all` for unattended runs)
- Run the daemon with `--verbose` for engine logs.
