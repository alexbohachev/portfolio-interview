"""Еталонні бейзлайни прогнозування попиту (Seasonal Naive та Historical DOW Moving Average)."""
from __future__ import annotations

import numpy as np
import pandas as pd


class SeasonalNaiveForecaster:
    """Сезонний наївний бейзлайн: прогнозує попит за аналогічний день тижня з останнього
    відомого тижня до моменту відсікання T0 (Zero Lookahead).
    """

    def __init__(self, season_length: int = 7):
        self.season_length = season_length
        self._last_season_data: dict[tuple[str, str], dict[int, float]] = {}

    def fit(self, train_df: pd.DataFrame) -> SeasonalNaiveForecaster:
        """Зберігає останнє спостереження для кожного дня тижня (0..6) по кожній серії."""
        self._last_season_data.clear()
        grouped = train_df.groupby(["hub_id", "sku_id"])
        
        for (hub, sku), group in grouped:
            sorted_group = group.sort_values(by="date")
            dow_dict = {}
            for dow in range(7):
                dow_rows = sorted_group[sorted_group["date"].dt.dayofweek == dow]
                if not dow_rows.empty:
                    dow_dict[dow] = float(dow_rows.iloc[-1]["demand"])
                else:
                    dow_dict[dow] = float(sorted_group["demand"].mean())
            self._last_season_data[(hub, sku)] = dow_dict
            
        return self

    def predict(self, test_df: pd.DataFrame) -> np.ndarray:
        preds = []
        for _, row in test_df.iterrows():
            key = (row["hub_id"], row["sku_id"])
            dow = row["date"].dayofweek
            series_dow_map = self._last_season_data.get(key, {})
            val = series_dow_map.get(dow, 0.0)
            preds.append(val)
        return np.array(preds, dtype=float)


class HistoricalDowMovingAverageForecaster:
    """Евристичний бейзлайн ланцюгів постачання (DOW 4-Week Average):
    Середнє значення попиту за останні 4 тижні для відповідного дня тижня.
    """

    def __init__(self, n_weeks: int = 4):
        self.n_weeks = n_weeks
        self._dow_ma_data: dict[tuple[str, str], dict[int, float]] = {}

    def fit(self, train_df: pd.DataFrame) -> HistoricalDowMovingAverageForecaster:
        self._dow_ma_data.clear()
        grouped = train_df.groupby(["hub_id", "sku_id"])
        
        for (hub, sku), group in grouped:
            sorted_group = group.sort_values(by="date")
            dow_dict = {}
            for dow in range(7):
                dow_rows = sorted_group[sorted_group["date"].dt.dayofweek == dow]
                if not dow_rows.empty:
                    # беремо останні n_weeks спостережень
                    recent_dow = dow_rows.iloc[-self.n_weeks:]["demand"]
                    dow_dict[dow] = float(recent_dow.mean())
                else:
                    dow_dict[dow] = float(sorted_group["demand"].mean())
            self._dow_ma_data[(hub, sku)] = dow_dict
            
        return self

    def predict(self, test_df: pd.DataFrame) -> np.ndarray:
        preds = []
        for _, row in test_df.iterrows():
            key = (row["hub_id"], row["sku_id"])
            dow = row["date"].dayofweek
            series_dow_map = self._dow_ma_data.get(key, {})
            val = series_dow_map.get(dow, 0.0)
            preds.append(val)
        return np.array(preds, dtype=float)
