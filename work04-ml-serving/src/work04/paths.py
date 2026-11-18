from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"
ARTIFACTS = ROOT / "artifacts"
CONFIG = ROOT / "config" / "default.yaml"
MANIFEST = ROOT / "manifests" / "test_manifest.json"
REPORT = ROOT / "REPORT.md"