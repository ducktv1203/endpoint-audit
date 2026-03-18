# Local-only demo (no server)

This mode is for learning/debugging: it runs the audit loop locally, prints events in real time, and writes a JSONL log file to a dedicated folder on your machine.

By default, logs are stored under:

- `C:\Users\<you>\Documents\endpoint-audit-demo\` (if `Documents` exists), otherwise
- `C:\Users\<you>\Desktop\endpoint-audit-demo\`, otherwise
- `C:\Users\<you>\endpoint-audit-demo\`

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

## Disclaimer

This demo is intended for **authorized use on your own systems** only. It does not capture keystrokes or clipboard data, but it still provides visibility into process activity and optional file integrity. Do not run it on systems you do not control or without the knowledge and consent of the system owner.

