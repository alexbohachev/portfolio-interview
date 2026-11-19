import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


@pytest.fixture(scope="session", autouse=True)
def ensure_models_available():
    art = ROOT / "artifacts"
    pt_path = art / "model_point.joblib"
    qt_path = art / "model_quantile.joblib"
    if not pt_path.is_file() or not qt_path.is_file():
        from scripts.run_pipeline import main as run_pipeline
        run_pipeline()

