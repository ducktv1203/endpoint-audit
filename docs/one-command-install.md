# One-command install (Windows, authorized lab)

This is a **legitimate homelab deployment** path for machines you own/administer. It assumes you have administrative rights and appropriate authorization on the target endpoints.

## Server (VM)

```powershell
python -m pip install -e ".[server]"
python -m uvicorn server.app:app --host 0.0.0.0 --port 8000
```

Open inbound TCP **8000** on the VM firewall.

Health check from another machine:

```powershell
curl http://<SERVER_IP>:8000/health
```

## Client (Windows machine)

From the repo root on the client:

```powershell
.\install\install-agent.ps1 -ServerUrl "http://<SERVER_IP>:8000" -ApiToken "change-me" -HostId "<CLIENT_NAME>"
```

By default this registers a task that runs **at logon** using `pythonw.exe` (no console window).

To see the task in Windows:

- Task Scheduler → Task Scheduler Library → `EndpointAuditAgent`

### Run at startup (requires admin)

```powershell
.\install\install-agent.ps1 -Trigger AtStartup -RunAsSystem -ServerUrl "http://<SERVER_IP>:8000" -ApiToken "change-me" -HostId "<CLIENT_NAME>"
```

## Verify data arrived

On the server machine:

- `server_storage/<CLIENT_NAME>/events.jsonl`
- `server_storage/<CLIENT_NAME>/latest.txt`

## Uninstall

```powershell
.\install\uninstall-agent.ps1
```

## Troubleshooting

- **401 / 403 from server**: the server is enforcing `AUDIT_API_TOKEN` and the client token doesn't match.
- **No data arriving**: check VM networking and firewall, and confirm `AUDIT_SERVER_URL` points to the VM IP (not `127.0.0.1`).
- **Task runs but nothing happens**: ensure Python is installed and `pythonw.exe` exists next to `python.exe`.

> **Important**: This installer is designed for lab environments and managed endpoints where you are the legitimate administrator. Do not use it to deploy agents to machines without prior consent.

