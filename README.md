# Endpoint Audit Demo (Authorized Use)

This repo contains **educational, consent-based** examples for endpoint telemetry on systems you **own or are explicitly authorized to manage**.

It **does not** capture keystrokes or clipboard data and is **not** intended for stealth collection.

## What's included

- **`agent/`**: Headless auditing agent (process start/stop + optional file integrity hashes).
  - Spools events to `.spool/outbox/*.jsonl` and retries shipping.
- **`server/`**: FastAPI ingestion server.
  - Writes `server_storage/<host_id>/events.jsonl` (append-only) and `latest.txt` (quick view).
- **`install/`**: Windows installer scripts that register a Scheduled Task using `pythonw.exe` (no console window).
- **`main.py`**: Separate in-app (focused-window-only) input event demo (not required for the agent/server).

## Requirements

- **Python**: 3.11+
- **Network**: client must reach server TCP port (default **8000**)

## Quickstart (server)

```bash
python -m pip install -e ".[server]"
python -m uvicorn server.app:app --host 0.0.0.0 --port 8000
```

Verify:

```bash
curl http://127.0.0.1:8000/health
```

## Quickstart (agent)

Create a `.env` based on `.env.example`, then:

```bash
python -m pip install -e ".[agent]"
python -m agent.run
```

Confirm data arrived on server:

- `server_storage/<AUDIT_HOST_ID>/events.jsonl`
- `server_storage/<AUDIT_HOST_ID>/latest.txt`

## Windows headless run

See `docs/windows-run-headless.md`.

## One-command install (Windows)

See `docs/one-command-install.md`.

## Configuration

Agent reads environment variables (from `.env` if present):

- **`AUDIT_SERVER_URL`**: base URL (e.g. `http://192.168.1.50:8000`)
- **`AUDIT_API_TOKEN`**: shared token (optional, but recommended)
- **`AUDIT_HOST_ID`**: the host label used for server storage folder
- **`AUDIT_POLL_INTERVAL_SECONDS`**: polling interval
- **`AUDIT_FILE_HASH_PATHS`**: optional `;`-separated file paths to hash every ~60s

Server uses:

- **`AUDIT_SERVER_STORAGE_DIR`**: storage root (default `server_storage`)
- **`AUDIT_API_TOKEN`**: if set, server enforces Bearer auth

## Safety / Ethics

This repo is intentionally scoped to **authorized endpoint auditing and in-app demos**.

If your goal is “run hidden on a target and exfiltrate data”, do not use this project.

