from __future__ import annotations

from pathlib import Path


def cleanup_logs_by_size(directory: Path, max_size_mb: int = 50) -> None:
    if max_size_mb <= 0:
        return

    if not directory.exists():
        return

    max_size_bytes = max_size_mb * 1024 * 1024

    files = [p for p in directory.iterdir() if p.is_file()]
    files.sort(key=lambda p: p.stat().st_mtime)  # oldest first

    total = sum(p.stat().st_size for p in files)
    for p in files:
        if total <= max_size_bytes:
            break
        try:
            size = p.stat().st_size
            p.unlink(missing_ok=True)
            total -= size
        except OSError:
            # Best-effort cleanup
            continue

