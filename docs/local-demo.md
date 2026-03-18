# Local-only demo (no server)

This mode is for learning/debugging: it runs the audit loop locally, prints events in real time, and writes a JSONL log file to a folder you choose (default: **Documents**).

## Run

```powershell
python -m pip install -e ".[agent]"
python -m agent.local_demo
```

## Follow logs in a second terminal

When the demo starts it prints the output file path. In another terminal:

```powershell
Get-Content -Wait -Tail 50 "C:\path\to\endpoint_audit_<host>_<timestamp>.jsonl"
```

## Choose output folder + host id

```powershell
python -m agent.local_demo --out-dir "$env:USERPROFILE\Desktop" --host-id my-pc
```

## Optional: stop after N seconds

```powershell
python -m agent.local_demo --duration 30
```

