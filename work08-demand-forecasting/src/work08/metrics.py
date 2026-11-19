"""Метрики якості прогнозування часових рядів та складської оптимізації."""
from __future__ import annotations

import numpy as np


def wape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Weighted Absolute Percentage Error (WAPE): sum(|y - y_hat|) / sum(y).
    Стандарт ритейлу та ланцюгів постачання: не має проблем ділення на нуль, як MAPE,
    та зважує помилки пропорційно реальному обсягу попиту.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    denom = np.sum(np.abs(y_true))
    if denom == 0:
        return 0.0
    return float(np.sum(np.abs(y_true - y_pred)) / denom)


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Error."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Root Mean Squared Error."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def normalized_bias(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Normalized Forecast Bias: sum(y_hat - y) / sum(y).
    Показує систематичний перепрогноз (>0) чи недопрогноз (<0).
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    denom = np.sum(y_true)
    if denom == 0:
        return 0.0
    return float(np.sum(y_pred - y_true) / denom)


def pinball_loss(y_true: np.ndarray, y_pred: np.ndarray, alpha: float) -> float:
    """Pinball loss (Quantile loss) для оцінки квантильного прогнозу:
    L_alpha(y, q) = max(alpha * (y - q), (1 - alpha) * (q - y))
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    diff = y_true - y_pred
    loss = np.maximum(alpha * diff, (alpha - 1.0) * diff)
    return float(np.mean(loss))


def coverage_rate(y_true: np.ndarray, y_lower: np.ndarray, y_upper: np.ndarray) -> float:
    """Емпіричне покриття довірчого інтервалу [P10, P90]. Очікується ~0.80."""
    y_true = np.asarray(y_true, dtype=float)
    y_lower = np.asarray(y_lower, dtype=float)
    y_upper = np.asarray(y_upper, dtype=float)
    covered = (y_true >= y_lower) & (y_true <= y_upper)
    return float(np.mean(covered))


def inventory_cost(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    c_under: float = 5.0,
    c_over: float = 1.0,
) -> float:
    """Сумарна вартість помилок для бізнесу за асиметричною моделлю запасів (Newsvendor loss):
    Total Cost = C_under * sum(max(0, y - y_hat)) + C_over * sum(max(0, y_hat - y))
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    under_stock = np.maximum(0.0, y_true - y_pred)
    over_stock = np.maximum(0.0, y_pred - y_true)
    return float(c_under * np.sum(under_stock) + c_over * np.sum(over_stock))


def evaluate_forecasts(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    c_under: float = 5.0,
    c_over: float = 1.0,
) -> dict[str, float]:
    """Зведений словник ключових бізнес- та ML-метрик прогнозу."""
    return {
        "wape": round(wape(y_true, y_pred), 4),
        "mae": round(mae(y_true, y_pred), 3),
        "rmse": round(rmse(y_true, y_pred), 3),
        "bias": round(normalized_bias(y_true, y_pred), 4),
        "inventory_cost": round(inventory_cost(y_true, y_pred, c_under, c_over), 1),
    }
