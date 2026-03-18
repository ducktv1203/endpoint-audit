from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SpoolPaths:
    root: Path
    outbox: Path
    sent: Path
    dead: Path


def init_spool(root: Path) -> SpoolPaths:
    outbox = root / "outbox"
    sent = root / "sent"
    dead = root / "dead"
    outbox.mkdir(parents=True, exist_ok=True)
    sent.mkdir(parents=True, exist_ok=True)
    dead.mkdir(parents=True, exist_ok=True)
    return SpoolPaths(root=root, outbox=outbox, sent=sent, dead=dead)


def write_batch(outbox: Path, events: list[dict]) -> Path:
    ts = time.strftime("%Y-%m-%d_%H-%M-%S")
    pid = os.getpid()
    path = outbox / f"batch_{ts}_{pid}_{int(time.time() * 1000)}.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    return path


def iter_outbox_files(outbox: Path) -> list[Path]:
    files = [p for p in outbox.iterdir() if p.is_file() and p.suffix.lower() == ".jsonl"]
    files.sort(key=lambda p: p.stat().st_mtime)  # oldest first
    return files


def move_file(src: Path, dst_dir: Path) -> Path:
    dst = dst_dir / src.name
    try:
        return src.replace(dst)
    except OSError:
        # If replace fails (e.g., cross-device), fall back to copy+unlink
        data = src.read_bytes()
        dst.write_bytes(data)
        src.unlink(missing_ok=True)
        return dst

