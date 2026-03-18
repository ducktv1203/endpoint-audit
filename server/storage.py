from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def host_dir(root: Path, host_id: str) -> Path:
    safe = "".join(ch for ch in host_id if ch.isalnum() or ch in ("-", "_", ".")).strip() or "unknown-host"
    d = root / safe
    ensure_dir(d)
    return d


def append_jsonl(path: Path, events: Iterable[dict]) -> None:
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")


def write_txt_report(path: Path, events: Iterable[dict]) -> None:
    """
    Very simple TXT report for quick human scanning.
    (The canonical, machine-friendly log is JSONL.)
    """
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        for e in events:
            ts = e.get("ts", "")
            typ = e.get("type", "")
            data = e.get("data", {})
            f.write(f"{ts} {typ} {data}\n")

