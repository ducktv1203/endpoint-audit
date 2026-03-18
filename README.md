# Endpoint Audit Demo (Authorized Use)

This repo contains **educational, consent-based** examples for endpoint telemetry on systems you **own or are explicitly authorized to manage**.

It **does not** capture keystrokes or clipboard data and is **not** intended for stealth collection.

## What's included

- **`agent/`**: Headless auditing agent (process start/stop + optional file integrity hashes) that spools events locally and ships them to a server over HTTP(S).
- **`server/`**: FastAPI ingestion server that stores per-host `events.jsonl` and a quick `latest.txt` report.
- **`main.py`**: A separate in-app (focused-window-only) input event demo.

## Quickstart (server)

```bash
python -m pip install -e ".[server]"
python -m uvicorn server.app:app --host 0.0.0.0 --port 8000
```

## Quickstart (agent)

Create a `.env` based on `.env.example`, then:

```bash
python -m pip install -e ".[agent]"
python -m agent.run
```

## Windows headless run

See `docs/windows-run-headless.md`.

## One-command install (Windows)

See `docs/one-command-install.md`.

## Safety / Ethics

This repo is intentionally scoped to **authorized endpoint auditing and in-app demos**.

