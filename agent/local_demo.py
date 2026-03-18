from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from .config import AgentConfig
from .events import AuditEvent
from .integrity import sha256_path
from .process_watch import snapshot_processes, diff_processes


def default_output_dir() -> Path:
    home = Path.home()
    # Prefer Documents, fall back to Desktop, then home
    for name in ("Documents", "Desktop"):
        p = home / name
        if p.exists():
            return p
    return home


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Local-only audit demo: prints events in real time and writes JSONL locally (no server)."
    )
    p.add_argument(
        "--out-dir",
        default=str(default_output_dir()),
        help="Directory to write logs into (default: Documents/Desktop).",
    )
    p.add_argument(
        "--host-id",
        default=os.getenv("AUDIT_HOST_ID", "local-demo"),
        help="Host label used in the output filename.",
    )
    p.add_argument(
        "--interval",
        type=float,
        default=float(os.getenv("AUDIT_POLL_INTERVAL_SECONDS", "2")),
        help="Polling interval seconds.",
    )
    p.add_argument(
        "--duration",
        type=float,
        default=0.0,
        help="Optional duration seconds to run (0 = run forever).",
    )
    return p.parse_args()


def write_event(f, event: dict) -> None:
    line = json.dumps(event, ensure_ascii=False)
    print(line, flush=True)
    f.write(line + "\n")
    f.flush()


def main() -> None:
    args = parse_args()
    cfg = AgentConfig.from_env().model_copy(
        update={"host_id": str(args.host_id), "poll_interval_seconds": float(args.interval)}
    )

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"endpoint_audit_{cfg.host_id}_{time.strftime('%Y-%m-%d_%H-%M-%S')}.jsonl"

    print(f"Local demo running. Writing to: {out_path}")
    print("Open another terminal to follow the file (PowerShell):")
    print(f'  Get-Content -Wait -Tail 50 "{out_path}"')

    prev = snapshot_processes()
    last_integrity_at = 0.0
    start = time.time()

    with out_path.open("a", encoding="utf-8") as f:
        write_event(f, AuditEvent(host_id=cfg.host_id, type="agent.heartbeat", data={"mode": "local"}).model_dump())

        while True:
            events: list[dict] = []

            curr = snapshot_processes()
            started, stopped = diff_processes(prev, curr)
            prev = curr

            for pinfo in started:
                events.append(
                    AuditEvent(
                        host_id=cfg.host_id,
                        type="process.started",
                        data={"pid": pinfo.pid, "name": pinfo.name, "exe": pinfo.exe},
                    ).model_dump()
                )
            for pinfo in stopped:
                events.append(
                    AuditEvent(
                        host_id=cfg.host_id,
                        type="process.stopped",
                        data={"pid": pinfo.pid, "name": pinfo.name, "exe": pinfo.exe},
                    ).model_dump()
                )

            now = time.time()
            if cfg.file_hash_paths and (now - last_integrity_at) >= 60.0:
                last_integrity_at = now
                for path in cfg.file_hash_paths:
                    digest = sha256_path(path)
                    if digest:
                        events.append(
                            AuditEvent(
                                host_id=cfg.host_id,
                                type="file.hash",
                                data={"path": str(Path(path)), "sha256": digest},
                            ).model_dump()
                        )

            if not events:
                events.append(AuditEvent(host_id=cfg.host_id, type="agent.heartbeat", data={}).model_dump())

            for e in events:
                write_event(f, e)

            if args.duration and (time.time() - start) >= float(args.duration):
                write_event(
                    f,
                    AuditEvent(
                        host_id=cfg.host_id,
                        type="agent.heartbeat",
                        data={"stopped": True, "reason": "duration elapsed"},
                    ).model_dump(),
                )
                break

            time.sleep(max(cfg.poll_interval_seconds, 0.2))


if __name__ == "__main__":
    main()

