import time

import pytest
from fastapi.testclient import TestClient

from work04.app_main import app
from work04.paths import ARTIFACTS


@pytest.fixture(scope="module")
def client():
    if not (ARTIFACTS / "model_bundle.joblib").is_file():
        pytest.skip("run work04 all first")
    with TestClient(app) as c:
        yield c


def test_predict_schema(client):
    r = client.post(
        "/v1/predict",
        json={
            "hours_used": 10,
            "maint_score": 1.2,
            "region": "north",
            "equipment_type": "tractor",
            "use_candidate": True,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["model_version"]
    assert body["preprocessing_version"]
    assert 0 <= body["probability"] <= 1
    assert body["decision"] in ("review", "accept")


def test_predict_p95_latency(client):
    times = []
    payload = {
        "hours_used": 6,
        "maint_score": 0.2,
        "region": "south",
        "equipment_type": "sprayer",
        "use_candidate": False,
    }
    for _ in range(50):
        t0 = time.perf_counter()
        client.post("/v1/predict", json=payload)
        times.append(time.perf_counter() - t0)
    times.sort()
    p95 = times[int(0.95 * (len(times) - 1))]
    assert p95 < 0.5, f"p95 latency {p95:.3f}s too high for local MVP"