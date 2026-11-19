"""Тести FastAPI сервісу сервінгу прогнозу (/v1/health та /v1/forecast)."""
from __future__ import annotations

from fastapi.testclient import TestClient
from work08.server import app


def test_health_endpoint():
    with TestClient(app) as client:
        resp = client.get("/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "hub_central" in data["indexed_hubs"]
        assert "SKU_FERT_NPK" in data["indexed_skus"]


def test_forecast_endpoint_valid():
    with TestClient(app) as client:
        payload = {
            "hub_id": "hub_central",
            "sku_id": "SKU_FERT_NPK",
            "horizon_days": 14,
        }
        resp = client.post("/v1/forecast", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["hub_id"] == "hub_central"
        assert data["sku_id"] == "SKU_FERT_NPK"
        assert len(data["predictions"]) == 14
        
        # Перевірка квантильної монотонності: P10 <= P50 <= P90
        for p in data["predictions"]:
            assert p["p10_lower"] <= p["p50_median"] + 1e-3
            assert p["p50_median"] <= p["p90_upper"] + 1e-3
            assert p["recommended_order"] >= 0.0


def test_forecast_endpoint_invalid_horizon():
    with TestClient(app) as client:
        # Horizon != 14 (наприклад 7, 21 або 28) повертає 422 за контрактом прямої моделі H=14
        for bad_h in [7, 21, 28, 40]:
            payload = {
                "hub_id": "hub_central",
                "sku_id": "SKU_FERT_NPK",
                "horizon_days": bad_h,
            }
            resp = client.post("/v1/forecast", json=payload)
            assert resp.status_code == 422
            assert "Непідтримуваний горизонт прогнозу" in resp.json()["detail"]


def test_forecast_endpoint_unknown_series():
    with TestClient(app) as client:
        payload = {
            "hub_id": "unknown_hub_99",
            "sku_id": "SKU_FERT_NPK",
            "horizon_days": 14,
        }
        resp = client.post("/v1/forecast", json=payload)
        assert resp.status_code == 404
