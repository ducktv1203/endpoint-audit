from __future__ import annotations

import json
import time
from pathlib import Path

import httpx

from .spool import move_file


def read_jsonl(path: Path) -> list[dict]:
    events: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            events.append(json.loads(line))
    return events


def ship_file(
    *,
    path: Path,
    server_url: str,
    api_token: str,
    sent_dir: Path,
    dead_dir: Path,
    timeout_seconds: float = 10.0,
    max_retries: int = 5,
) -> bool:
    url = server_url.rstrip("/") + "/ingest"
    payload = {"events": read_jsonl(path)}
    headers = {"Authorization": f"Bearer {api_token}"} if api_token else {}

    backoff = 1.0
    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=timeout_seconds) as client:
                r = client.post(url, json=payload, headers=headers)
            if 200 <= r.status_code < 300:
                move_file(path, sent_dir)
                return True

            # Unauthorized / forbidden: don't retry forever
            if r.status_code in (401, 403):
                move_file(path, dead_dir)
                return False

        except httpx.HTTPError:
            pass

        time.sleep(backoff)
        backoff = min(backoff * 2.0, 30.0)

    # After repeated failures, keep it in outbox for next run (do not drop)
    return False

