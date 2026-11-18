from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROC = ROOT / "data" / "processed"
ARTIFACTS = ROOT / "artifacts"
CONFIG_PATH = ROOT / "config" / "default.yaml"
MANIFEST_PATH = ROOT / "manifests" / "test_manifest.json"
REPORT_PATH = ROOT / "REPORT.md"