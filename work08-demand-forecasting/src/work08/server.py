"""FastAPI сервіс онлайн-прогнозування попиту та рекомендацій замовлення (work08)."""
from __future__ import annotations

import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from work08.data import load_demand_data
from work08.features import create_features


class ForecastRequest(BaseModel):
    hub_id: str = Field(..., description="ID регіонального розподільчого хабу")
    sku_id: str = Field(..., description="ID товарної позиції / категорії")
    horizon_days: int = Field(default=14, ge=1, le=28, description="Горизонт прогнозу (1..28 днів)")


class DailyForecast(BaseModel):
    date: str
    p10_lower: float
    p50_median: float
    p90_upper: float
    recommended_order: float


class ForecastResponse(BaseModel):
    hub_id: str
    sku_id: str
    horizon_days: int
    predictions: list[DailyForecast]
    summary_total_p50: float
    summary_total_recommended_order: float
    latency_ms: float


class HealthResponse(BaseModel):
    status: str
    model_version: str
    indexed_hubs: list[str]
    indexed_skus: list[str]
    max_history_date: str


class ServerState:
    model_point: Any = None
    model_quantile: Any = None
    historical_df: pd.DataFrame | None = None
    feature_cols: list[str] = []
    backtest_metrics: dict[str, Any] = {}


state = ServerState()
ROOT = Path(__file__).resolve().parents[2]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ініціалізація моделей та даних
    art_dir = ROOT / "artifacts"
    pt_path = art_dir / "model_point.joblib"
    qt_path = art_dir / "model_quantile.joblib"
    data_path = ROOT / "data" / "raw" / "historical_demand.csv"
    
    if data_path.is_file():
        state.historical_df = load_demand_data(data_path)
    
    if pt_path.is_file() and qt_path.is_file():
        state.model_point = joblib.load(pt_path)
        state.model_quantile = joblib.load(qt_path)
        state.feature_cols = state.model_point.feature_names_
        
    yield


app = FastAPI(
    title="Demand Forecasting & Inventory Optimization API",
    version="1.0.0",
    description="Високоточний сервінг прогнозування попиту з асиметричним ризиком запасів для Senior ML Engineer track.",
    lifespan=lifespan,
)


@app.get("/v1/health", response_model=HealthResponse)
def health():
    if state.historical_df is None:
        raise HTTPException(status_code=503, detail="Historical data not loaded")
    
    hubs = sorted(state.historical_df["hub_id"].unique().tolist())
    skus = sorted(state.historical_df["sku_id"].unique().tolist())
    max_d = str(state.historical_df["date"].max().strftime("%Y-%m-%d"))
    
    return HealthResponse(
        status="healthy",
        model_version="1.0.0",
        indexed_hubs=hubs,
        indexed_skus=skus,
        max_history_date=max_d,
    )


@app.post("/v1/forecast", response_model=ForecastResponse)
def get_forecast(req: ForecastRequest):
    t0 = time.perf_counter()
    if state.historical_df is None or state.model_point is None:
        raise HTTPException(status_code=503, detail="Моделі або історичні дані ще не ініціалізовані")

    df = state.historical_df
    series_df = df[(df["hub_id"] == req.hub_id) & (df["sku_id"] == req.sku_id)].copy()
    if series_df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Серія для hub_id={req.hub_id} та sku_id={req.sku_id} не знайдена в історії.",
        )

    # Визначаємо дати майбутнього горизонту
    max_dt = series_df["date"].max()
    future_dates = pd.date_range(start=max_dt + pd.Timedelta(days=1), periods=req.horizon_days, freq="D")
    
    # Створюємо синтетичні майбутні рядки для конструювання ознак (з відомими календарем і ціною)
    last_price = float(series_df.iloc[-1]["unit_price"])
    future_rows = []
    for f_dt in future_dates:
        dow = f_dt.weekday()
        is_hol = 1 if (f_dt.month == 1 and f_dt.day in (1, 7)) or (f_dt.month == 5 and f_dt.day in (1, 9)) else 0
        avg_temp = 10.0 + 15.0 * np.sin(2 * np.pi * (f_dt.timetuple().tm_yday - 100) / 365.25)
        future_rows.append({
            "date": f_dt,
            "hub_id": req.hub_id,
            "sku_id": req.sku_id,
            "demand": 0.0, # плейсхолдер, не використовується для t - H ознак
            "unit_price": last_price,
            "promo": 0,
            "temperature_c": round(avg_temp, 1),
            "is_holiday": is_hol,
        })
    
    extended_df = pd.concat([series_df, pd.DataFrame(future_rows)], ignore_index=True)
    extended_feat, feat_cols, _ = create_features(extended_df, horizon_days=req.horizon_days)
    
    # Вибираємо тільки майбутні рядки
    inference_df = extended_feat[extended_feat["date"].isin(future_dates)].copy()
    if len(inference_df) != req.horizon_days:
        raise HTTPException(status_code=500, detail="Помилка формування вектора ознак майбутнього горизонту")

    p50_preds = state.model_point.predict(inference_df)
    q_preds = state.model_quantile.predict(inference_df)
    safety_preds = state.model_quantile.predict_safety_stock(inference_df)
    
    daily_preds = []
    for i, f_dt in enumerate(future_dates):
        daily_preds.append(
            DailyForecast(
                date=f_dt.strftime("%Y-%m-%d"),
                p10_lower=round(float(q_preds[0.10][i]), 1),
                p50_median=round(float(p50_preds[i]), 1),
                p90_upper=round(float(q_preds[0.90][i]), 1),
                recommended_order=round(float(safety_preds[i]), 1),
            )
        )
        
    latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    
    return ForecastResponse(
        hub_id=req.hub_id,
        sku_id=req.sku_id,
        horizon_days=req.horizon_days,
        predictions=daily_preds,
        summary_total_p50=round(float(np.sum(p50_preds)), 1),
        summary_total_recommended_order=round(float(np.sum(safety_preds)), 1),
        latency_ms=latency_ms,
    )
