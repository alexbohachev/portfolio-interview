"""Генератор реалістичного датасету попиту для 20 часових рядів (5 регіональних хабів x 4 категорії агро-товарів/SKU)
на щоденному інтервалі за 3 роки (2015-01-01 .. 2017-12-31).

Фіксований seed для 100% детермінізму та відтворюваності в CI/тестах без мережевих залежностей.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "historical_demand.csv"

HUBS = ["hub_central", "hub_north", "hub_south", "hub_east", "hub_west"]
SKUS = [
    {"id": "SKU_FERT_NPK", "base": 120.0, "spring_peak": 2.2, "autumn_peak": 1.7, "dow_effect": 1.2},
    {"id": "SKU_SEED_WHEAT", "base": 85.0, "spring_peak": 3.0, "autumn_peak": 2.5, "dow_effect": 1.1},
    {"id": "SKU_PEST_HERB", "base": 45.0, "spring_peak": 1.8, "autumn_peak": 1.1, "dow_effect": 1.15},
    {"id": "SKU_EQUIP_PARTS", "base": 18.0, "spring_peak": 1.4, "autumn_peak": 1.3, "dow_effect": 1.3},
]


def generate_demand_series(seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    date_range = pd.date_range(start="2015-01-01", end="2017-12-31", freq="D")
    n_days = len(date_range)
    
    rows = []
    
    # Hub multipliers
    hub_factors = {
        "hub_central": 1.35,
        "hub_north": 1.05,
        "hub_south": 1.15,
        "hub_east": 0.85,
        "hub_west": 0.90,
    }
    
    for hub in HUBS:
        h_mult = hub_factors[hub]
        for sku_info in SKUS:
            sku = sku_info["id"]
            base = sku_info["base"] * h_mult
            
            for i, dt in enumerate(date_range):
                day_of_year = dt.timetuple().tm_yday
                dow = dt.weekday() # 0 = Monday, 6 = Sunday
                year_ratio = (dt.year - 2015) / 3.0
                
                # 1. Трендова складова (~4% щорічного зростання)
                trend = 1.0 + 0.04 * year_ratio
                
                # 2. Річна сезонність (весняний пік ~квітень [день 90-120], осінній пік ~вересень [день 240-270])
                spring_dist = np.exp(-0.5 * ((day_of_year - 105) / 25.0) ** 2)
                autumn_dist = np.exp(-0.5 * ((day_of_year - 255) / 25.0) ** 2)
                yearly_season = 1.0 + (sku_info["spring_peak"] - 1.0) * spring_dist + (sku_info["autumn_peak"] - 1.0) * autumn_dist
                
                # 3. Тижнева сезонність (субота/неділя менший попит для b2b/дистрибуції)
                if dow == 6: # Sunday
                    dow_factor = 0.35
                elif dow == 5: # Saturday
                    dow_factor = 0.60
                elif dow in (1, 2): # Tue, Wed
                    dow_factor = sku_info["dow_effect"]
                else:
                    dow_factor = 1.0
                
                # 4. Промокампанії (випадкові 5-денні акції ~3 рази на рік на хаб/SKU)
                promo = 1 if ((i % 113 < 4) or (i % 179 < 3)) and (dow < 5) else 0
                promo_lift = 1.30 if promo == 1 else 1.0
                
                # 5. Температурний проксі-ефект
                avg_temp = 10.0 + 15.0 * np.sin(2 * np.pi * (day_of_year - 100) / 365.25)
                temp_noisy = avg_temp + np.random.normal(0, 3.0)
                
                # 6. Шум і цільовий попит
                lambda_val = base * trend * yearly_season * dow_factor * promo_lift
                noise = np.random.normal(1.0, 0.08)
                demand = max(0.0, np.round(lambda_val * noise, 1))
                
                # Ціна зі знижкою при промо
                base_price = 1000.0 / (sku_info["base"] ** 0.5)
                price = round(base_price * (0.85 if promo else 1.0), 2)
                
                is_holiday = 1 if (dt.month == 1 and dt.day in (1, 7)) or (dt.month == 5 and dt.day in (1, 9)) else 0
                if is_holiday:
                    demand = round(demand * 0.4, 1)
                
                rows.append({
                    "date": dt.strftime("%Y-%m-%d"),
                    "hub_id": hub,
                    "sku_id": sku,
                    "demand": demand,
                    "unit_price": price,
                    "promo": promo,
                    "temperature_c": round(temp_noisy, 1),
                    "is_holiday": is_holiday,
                })
                
    df = pd.DataFrame(rows)
    return df


def main() -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = generate_demand_series(seed=42)
    df.to_csv(DATA_PATH, index=False)
    print(f"Generated {len(df)} rows across {df['hub_id'].nunique()} hubs and {df['sku_id'].nunique()} SKUs.")
    print(f"Saved to: {DATA_PATH}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print("Sample:\n", df.head(3))


if __name__ == "__main__":
    main()
