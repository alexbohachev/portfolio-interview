from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORPUS_DIR = ROOT / "corpus" / "bundled"
ARTIFACTS = ROOT / "artifacts"
CONFIG = ROOT / "config" / "default.yaml"
GOLDEN = ROOT / "data" / "golden" / "questions.json"
MANIFEST = ROOT / "manifests" / "test_manifest.json"
REPORT = ROOT / "REPORT.md"