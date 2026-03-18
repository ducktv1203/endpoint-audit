from __future__ import annotations

import os
from pathlib import Path
from typing import Self

from dotenv import load_dotenv
from pydantic import BaseModel, Field


load_dotenv()


class ServerConfig(BaseModel):
    storage_dir: Path = Field(default=Path("server_storage"), validation_alias="AUDIT_SERVER_STORAGE_DIR")
    api_token: str = Field(default="", validation_alias="AUDIT_API_TOKEN")

    @classmethod
    def from_env(cls) -> Self:
        data = {
            "AUDIT_SERVER_STORAGE_DIR": os.getenv("AUDIT_SERVER_STORAGE_DIR", "server_storage"),
            "AUDIT_API_TOKEN": os.getenv("AUDIT_API_TOKEN", ""),
        }
        return cls.model_validate(data)

