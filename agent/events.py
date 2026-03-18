from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, Any

from pydantic import BaseModel, Field


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


EventType = Literal[
    "process.started",
    "process.stopped",
    "file.hash",
    "agent.heartbeat",
]


class AuditEvent(BaseModel):
    ts: str = Field(default_factory=utc_now_iso)
    host_id: str
    type: EventType
    data: dict[str, Any] = Field(default_factory=dict)

