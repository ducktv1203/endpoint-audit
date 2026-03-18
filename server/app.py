from __future__ import annotations

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from .config import ServerConfig
from .storage import host_dir, append_jsonl, write_txt_report


cfg = ServerConfig.from_env()
app = FastAPI(title="Endpoint Audit Ingest Server", version="0.1.0")


class IngestPayload(BaseModel):
    events: list[dict] = Field(default_factory=list)


def require_auth(authorization: str | None) -> None:
    if not cfg.api_token:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    if token != cfg.api_token:
        raise HTTPException(status_code=403, detail="Invalid token")


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/ingest")
def ingest(payload: IngestPayload, authorization: str | None = Header(default=None)) -> dict:
    require_auth(authorization)

    if not payload.events:
        return {"accepted": 0}

    # Expect the agent to set host_id; fall back safely.
    host_id = str(payload.events[0].get("host_id") or "unknown-host")
    d = host_dir(cfg.storage_dir, host_id)

    jsonl_path = d / "events.jsonl"
    append_jsonl(jsonl_path, payload.events)

    # Overwrite a "latest" TXT report each ingest for quick viewing
    txt_path = d / "latest.txt"
    write_txt_report(txt_path, payload.events)

    return {"accepted": len(payload.events), "host_id": host_id}

