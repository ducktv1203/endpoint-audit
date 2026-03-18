# One-command install (Windows, authorized lab)

This is a **legitimate homelab deployment** path for machines you own/administer.

## Server (VM)

```powershell
python -m pip install -e ".[server]"
python -m uvicorn server.app:app --host 0.0.0.0 --port 8000
```

Open inbound TCP **8000** on the VM firewall.

## Client (Windows machine)

From the repo root on the client:

```powershell
.\install\install-agent.ps1 -ServerUrl "http://<SERVER_IP>:8000" -ApiToken "change-me" -HostId "<CLIENT_NAME>"
```

By default this registers a task that runs **at logon** using `pythonw.exe` (no console window).

### Run at startup (requires admin)

```powershell
.\install\install-agent.ps1 -Trigger AtStartup -RunAsSystem -ServerUrl "http://<SERVER_IP>:8000" -ApiToken "change-me" -HostId "<CLIENT_NAME>"
```

## Uninstall

```powershell
.\install\uninstall-agent.ps1
```

