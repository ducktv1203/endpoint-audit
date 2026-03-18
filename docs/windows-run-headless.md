# Windows: run the agent headless (authorized deployments only)

This project is for **authorized endpoint auditing**. Do not deploy on systems you do not own or explicitly administer.

## Option A (simple): Task Scheduler + `pythonw.exe` (no console window)

1. Install Python for all users (recommended) and ensure you can run `python` normally.
2. Install the agent dependencies in your environment:

```powershell
python -m pip install -e ".[agent]"
```

3. Create a `.env` next to the repo (or set system env vars). Start from `.env.example`.
4. Create a scheduled task:
   - **Trigger**: At startup (or at logon)
   - **Action**: Start a program
     - Program/script: `C:\Path\To\pythonw.exe`
     - Add arguments: `-m agent.run`
     - Start in: `C:\Users\...\Desktop\Projects\Keylogger`
   - **Run whether user is logged on or not** (if desired)
   - **Run with highest privileges** (only if you need it for your auditing scope)

Why this works: `pythonw.exe` runs Python without creating a console window.

## Option A2 (recommended): use the included installer script

If you just want “one command” installation, use:

- `docs/one-command-install.md`

## Option B (managed endpoints): run as a Windows Service

If you need a real service (install/start/stop, recovery, centralized config), implement a service wrapper using:
- `pywin32` (Windows-only) **or**
- package as an `.exe` and register it with `sc.exe`/Service Control Manager.

This repo does not include a service wrapper by default to keep the educational scope small and cross-platform-friendly.

> **Disclaimer**: All examples in this document are intended for environments where you have clear administrative authority (e.g., your own workstation, lab machines, or managed endpoints). They must not be used for covert monitoring or to circumvent local policies.

