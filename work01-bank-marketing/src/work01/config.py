from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


def load_config(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def config_fingerprint(cfg: dict[str, Any]) -> str:
    payload = json.dumps(cfg, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]