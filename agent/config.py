from __future__ import annotations

import os
from pathlib import Path
from typing import Self

from dotenv import load_dotenv
from pydantic import BaseModel, Field


load_dotenv()


class AgentConfig(BaseModel):
    host_id: str = Field(default="unknown-host", validation_alias="AUDIT_HOST_ID")
    server_url: str = Field(default="http://127.0.0.1:8000", validation_alias="AUDIT_SERVER_URL")
    api_token: str = Field(default="", validation_alias="AUDIT_API_TOKEN")
    spool_dir: Path = Field(default=Path(".spool"), validation_alias="AUDIT_SPOOL_DIR")
    poll_interval_seconds: float = Field(default=2.0, validation_alias="AUDIT_POLL_INTERVAL_SECONDS")
    file_hash_paths: list[Path] = Field(default_factory=list)

    @classmethod
    def from_env(cls) -> Self:
        raw_paths = os.getenv("AUDIT_FILE_HASH_PATHS", "").strip()
        file_hash_paths: list[Path] = []
        if raw_paths:
            file_hash_paths = [Path(p.strip()) for p in raw_paths.split(";") if p.strip()]

        data = {
            "AUDIT_HOST_ID": os.getenv("AUDIT_HOST_ID", "unknown-host"),
            "AUDIT_SERVER_URL": os.getenv("AUDIT_SERVER_URL", "http://127.0.0.1:8000"),
            "AUDIT_API_TOKEN": os.getenv("AUDIT_API_TOKEN", ""),
            "AUDIT_SPOOL_DIR": os.getenv("AUDIT_SPOOL_DIR", ".spool"),
            "AUDIT_POLL_INTERVAL_SECONDS": os.getenv("AUDIT_POLL_INTERVAL_SECONDS", "2"),
            "file_hash_paths": file_hash_paths,
        }
        return cls.model_validate(data)

