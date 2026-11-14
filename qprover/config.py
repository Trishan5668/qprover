from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class Settings(BaseModel):
    backend: str | None = None
    min_qubits: int = Field(default=127, ge=127)
    problem_qubits: int = Field(default=20, ge=1)
    p: int = Field(default=1, ge=1, le=2)
    shots: int = Field(default=4096, ge=1)
    budget_cap_seconds: float = Field(default=540.0, gt=0, le=600)
    job_mode: bool = True
    hardware_confirm_required: bool = True
    depth_limit: int = Field(default=150, gt=0)
    lean_timeout_seconds: float = Field(default=30.0, gt=0)
    seed: int = 7
    llm_endpoint: str | None = None

    @classmethod
    def from_yaml(cls, path: Path = Path("config.yaml")) -> "Settings":
        if not path.exists():
            return cls()
        with path.open(encoding="utf-8") as handle:
            data: dict[str, Any] = yaml.safe_load(handle) or {}
        return cls.model_validate(data)

