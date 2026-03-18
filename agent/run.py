from __future__ import annotations

import time
from pathlib import Path

from .config import AgentConfig
from .events import AuditEvent
from .integrity import sha256_path
from .process_watch import snapshot_processes, diff_processes
from .spool import init_spool, write_batch, iter_outbox_files
from .shipper import ship_file


def build_heartbeat(cfg: AgentConfig) -> dict:
    return AuditEvent(host_id=cfg.host_id, type="agent.heartbeat", data={}).model_dump()


def main() -> None:
    cfg = AgentConfig.from_env()
    spool = init_spool(cfg.spool_dir)

    prev = snapshot_processes()
    last_integrity_at = 0.0

    while True:
        events: list[dict] = []

        curr = snapshot_processes()
        started, stopped = diff_processes(prev, curr)
        prev = curr

        for p in started:
            events.append(
                AuditEvent(
                    host_id=cfg.host_id,
                    type="process.started",
                    data={"pid": p.pid, "name": p.name, "exe": p.exe},
                ).model_dump()
            )
        for p in stopped:
            events.append(
                AuditEvent(
                    host_id=cfg.host_id,
                    type="process.stopped",
                    data={"pid": p.pid, "name": p.name, "exe": p.exe},
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

        # Always emit a heartbeat periodically (even if no process changes)
        if not events:
            events.append(build_heartbeat(cfg))

        batch_path = write_batch(spool.outbox, events)

        # Try to drain outbox each loop (best-effort)
        for f in iter_outbox_files(spool.outbox):
            ship_file(
                path=f,
                server_url=cfg.server_url,
                api_token=cfg.api_token,
                sent_dir=spool.sent,
                dead_dir=spool.dead,
            )

        time.sleep(max(cfg.poll_interval_seconds, 0.2))


if __name__ == "__main__":
    main()

