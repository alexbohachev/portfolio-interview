from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field

from work04.paths import ARTIFACTS


class PredictRequest(BaseModel):
    hours_used: int = Field(ge=1, le=24)
    maint_score: float
    region: str
    equipment_type: str
    use_candidate: bool = True


class PredictResponse(BaseModel):
    model_version: str
    preprocessing_version: str
    schema_version: int
    system: str
    probability: float
    decision: str
    threshold: float


def load_bundle(path: Path | None = None) -> dict[str, Any]:
    p = path or ARTIFACTS / "model_bundle.joblib"
    return joblib.load(p)


def predict_one(bundle: dict, req: PredictRequest) -> PredictResponse:
    row = pd.DataFrame(
        [
            {
                "hours_used": req.hours_used,
                "maint_score": req.maint_score,
                "region": req.region,
                "equipment_type": req.equipment_type,
            }
        ]
    )
    cols = bundle["feature_columns"]
    x_num = row[["hours_used", "maint_score"]].astype(float)
    x_cat = pd.get_dummies(row[["region", "equipment_type"]].astype(str), prefix=["region", "equipment_type"], dtype=float)
    x = pd.concat([x_num, x_cat], axis=1)
    for c in cols:
        if c not in x.columns:
            x[c] = 0.0
    x = x.reindex(columns=cols, fill_value=0.0)
    system = "candidate" if req.use_candidate else "baseline"
    model = bundle["candidate"] if req.use_candidate else bundle["baseline"]
    thresh = bundle["threshold_candidate"] if req.use_candidate else bundle["threshold_baseline"]
    prob = float(model.predict_proba(x)[0, 1])
    decision = "review" if prob >= thresh else "accept"
    return PredictResponse(
        model_version=bundle["model_version"],
        preprocessing_version=bundle["preprocessing_version"],
        schema_version=bundle["schema_version"],
        system=system,
        probability=prob,
        decision=decision,
        threshold=thresh,
    )