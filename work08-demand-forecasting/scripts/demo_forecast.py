"""Демонстрація інференсу: прогноз попиту на 14 днів для заданого хабу та SKU."""
from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastapi.testclient import TestClient
from work08.server import app


def main() -> int:
    print("=== WORK08: LIVE INFERENCE DEMO (/v1/forecast) ===")
    hub = "hub_central"
    sku = "SKU_FERT_NPK"
    horizon = 14
    
    with TestClient(app) as client:
        # 1. Health check
        h_resp = client.get("/v1/health")
        if h_resp.status_code != 200:
            print(f"Healthcheck failed: {h_resp.text}", file=sys.stderr)
            return 1
        h_data = h_resp.json()
        print(f"Status: {h_data['status']} | Max Date: {h_data['max_history_date']}")
        print(f"Запит прогнозу: Hub={hub}, SKU={sku}, Horizon={horizon} днів\n")
        
        # 2. Forecast
        payload = {
            "hub_id": hub,
            "sku_id": sku,
            "horizon_days": horizon,
        }
        resp = client.post("/v1/forecast", json=payload)
        if resp.status_code != 200:
            print(f"Forecast request failed: {resp.text}", file=sys.stderr)
            return 1
        
        data = resp.json()
        preds = data["predictions"]
        
        df_display = pd.DataFrame(preds)
        df_display.columns = ["Дата", "P10 (Нижня)", "P50 (Медіана)", "P90 (Верхня)", "Реком. Замовлення (Newsvendor)"]
        print(df_display.to_string(index=False))
        
        print("\n" + "-" * 55)
        print(f"Сумарний очікуваний попит (P50):    {data['summary_total_p50']} од.")
        print(f"Рекомендоване страхове замовлення:  {data['summary_total_recommended_order']} од.")
        print(f"Час інференсу (latency):            {data['latency_ms']} мс")
        print("-" * 55)
        
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
