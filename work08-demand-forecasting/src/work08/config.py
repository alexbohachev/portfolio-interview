"""Конфігурація пайплайну прогнозування попиту (work08)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ForecastingConfig:
    # Шляхи до даних та артефактів
    data_path: Path = Path("data/raw/historical_demand.csv")
    artifacts_dir: Path = Path("artifacts")
    manifests_dir: Path = Path("manifests")
    
    # Горизонт прогнозування
    horizon_days: int = 14
    
    # Кількість фолдів для chronological rolling backtest
    backtest_folds: int = 4
    
    # Лаги (повинні бути >= horizon_days для запобігання target leakage при direct forecasting)
    lag_steps: list[int] = field(default_factory=lambda: [14, 21, 28, 35])
    
    # Вікна ковзного середнього та ст. відхилення (зміщені на lag_steps[0])
    rolling_windows: list[int] = field(default_factory=lambda: [7, 14, 28])
    
    # Бізнес-вартість помилок для асиметричного складського ризику
    c_under: float = 5.0  # штраф за дефіцит (stockout / lost margin)
    c_over: float = 1.0   # вартість надлишку / зберігання (holding / spoilage cost)
    
    # Квантилі для ймовірнісного прогнозування
    quantiles: list[float] = field(default_factory=lambda: [0.10, 0.50, 0.90])
    
    # Гіперпараметри LightGBM
    lgb_params: dict = field(
        default_factory=lambda: {
            "objective": "regression_l1",  # MAE / L1 для прямої оптимізації WAPE
            "metric": "mae",
            "boosting_type": "gbdt",
            "n_estimators": 250,
            "learning_rate": 0.05,
            "num_leaves": 31,
            "min_child_samples": 20,
            "subsample": 0.85,
            "colsample_bytree": 0.85,
            "random_state": 42,
            "verbose": -1,
            "n_jobs": -1,
        }
    )

    @property
    def critical_fractile(self) -> float:
        """Оптимальний квантиль запасів (Newsvendor critical ratio):
        tau* = C_under / (C_under + C_over)
        """
        return self.c_under / (self.c_under + self.c_over)
