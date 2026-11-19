"""Моделі машинного навчання для прогнозування попиту (LightGBM Point & Quantile Forecasters)."""
from __future__ import annotations

import lightgbm as lgb
import numpy as np
import pandas as pd


class LightGBMPointForecaster:
    """Точковий прогнозист на базі градієнтного бустингу (L1-loss / MAE objective)."""

    def __init__(self, params: dict | None = None):
        self.params = params or {
            "objective": "regression_l1",
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
        self.model = lgb.LGBMRegressor(**self.params)
        self.feature_names_: list[str] = []

    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series | np.ndarray,
        feature_cols: list[str],
        val_set: tuple[pd.DataFrame, pd.Series | np.ndarray] | None = None,
    ) -> LightGBMPointForecaster:
        self.feature_names_ = list(feature_cols)
        X_tr = X_train[self.feature_names_]
        
        callbacks = []
        eval_set = None
        if val_set is not None:
            X_val, y_val = val_set
            eval_set = [(X_val[self.feature_names_], y_val)]
            callbacks.append(lgb.early_stopping(stopping_rounds=25, verbose=False))

        self.model.fit(
            X_tr,
            y_train,
            eval_set=eval_set,
            callbacks=callbacks if callbacks else None,
        )
        return self

    def predict(self, X_test: pd.DataFrame) -> np.ndarray:
        preds = self.model.predict(X_test[self.feature_names_])
        # Попит не може бути від'ємним
        return np.maximum(0.0, preds)


class LightGBMQuantileForecaster:
    """Ймовірнісний прогнозист для оцінки ризику запасів (Newsvendor Inventory Policy).
    Навчає окремі квантильні бустинги для P10, P50, P90 та оптимального критичного квантиля tau*.
    Підтримує Split Conformal Calibration для калібрування інтервалу [P10, P90] до цільового
    номінального покриття >= 80% out-of-sample.
    """

    def __init__(
        self,
        quantiles: list[float] | None = None,
        critical_ratio: float = 0.833,
        base_params: dict | None = None,
        conformal_target: float = 0.85,
    ):
        self.quantiles = quantiles or [0.10, 0.50, 0.90]
        self.critical_ratio = critical_ratio
        all_alphas = sorted(set(self.quantiles + [self.critical_ratio]))
        self.all_alphas = all_alphas
        self.conformal_target = conformal_target
        
        self.base_params = base_params or {
            "boosting_type": "gbdt",
            "n_estimators": 200,
            "learning_rate": 0.05,
            "num_leaves": 31,
            "min_child_samples": 20,
            "random_state": 42,
            "verbose": -1,
            "n_jobs": -1,
        }
        self.models_: dict[float, lgb.LGBMRegressor] = {}
        self.feature_names_: list[str] = []
        self.conformal_adjustment_80_: float = 0.0

    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series | np.ndarray,
        feature_cols: list[str],
        val_set: tuple[pd.DataFrame, pd.Series | np.ndarray] | None = None,
    ) -> LightGBMQuantileForecaster:
        self.feature_names_ = list(feature_cols)
        X_tr = X_train[self.feature_names_]

        for alpha in self.all_alphas:
            p = dict(self.base_params)
            p["objective"] = "quantile"
            p["alpha"] = alpha
            reg = lgb.LGBMRegressor(**p)
            reg.fit(X_tr, y_train)
            self.models_[alpha] = reg

        # Conformal quantile calibration на валідаційному фолді
        if val_set is not None:
            X_val, y_val = val_set
            preds_val = self.predict(X_val, calibrated=False)
            p10_val = preds_val[0.10]
            p90_val = preds_val[0.90]
            y_v = np.asarray(y_val)
            scores = np.maximum(p10_val - y_v, y_v - p90_val)
            self.conformal_adjustment_80_ = float(np.quantile(scores, self.conformal_target))
        else:
            self.conformal_adjustment_80_ = 0.0

        return self

    def predict(self, X_test: pd.DataFrame, calibrated: bool = False) -> dict[float, np.ndarray]:
        X_te = X_test[self.feature_names_]
        res = {}
        for alpha, model in self.models_.items():
            pred = model.predict(X_te)
            res[alpha] = np.maximum(0.0, pred)

        if calibrated and self.conformal_adjustment_80_ != 0.0:
            res[0.10] = np.maximum(0.0, res[0.10] - self.conformal_adjustment_80_)
            res[0.90] = res[0.90] + self.conformal_adjustment_80_

        return res

    def predict_safety_stock(self, X_test: pd.DataFrame) -> np.ndarray:
        """Рекомендований обсяг замовлення за критичним квантилем Newsvendor."""
        return self.predict(X_test, calibrated=False)[self.critical_ratio]
