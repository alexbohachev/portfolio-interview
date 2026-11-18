from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from work04.drift import drift_summary
from work04.serving import PredictRequest, PredictResponse, load_bundle, predict_one

_bundle = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _bundle
    _bundle = load_bundle()
    yield


app = FastAPI(title="work04-ml-serving", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok", "model_version": _bundle["model_version"] if _bundle else None}


@app.post("/v1/predict", response_model=PredictResponse)
def predict(req: PredictRequest) -> PredictResponse:
    if _bundle is None:
        raise HTTPException(503, "model not loaded")
    return predict_one(_bundle, req)


@app.get("/v1/drift")
def drift():
    if _bundle is None:
        raise HTTPException(503, "model not loaded")
    return drift_summary(_bundle)