from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config" / "default.yaml"
ARTIFACTS = ROOT / "artifacts"
DATA = ROOT / "data"