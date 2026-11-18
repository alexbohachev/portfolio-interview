from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
def fit_temperature(logits: np.ndarray, y_true: np.ndarray, max_iter: int = 200, lr: float = 0.01) -> float:
    """Temperature scaling: p = sigmoid(logit / T), T > 0."""
    if len(y_true) < 10:
        return 1.0
    logit_t = torch.tensor(logits, dtype=torch.float32)
    y_t = torch.tensor(y_true.astype(np.float32))
    log_T = nn.Parameter(torch.zeros(1))
    optim = torch.optim.LBFGS([log_T], lr=lr, max_iter=max_iter)
    bce = nn.BCEWithLogitsLoss()

    def closure():
        optim.zero_grad()
        scaled = logit_t / torch.exp(log_T).clamp(min=1e-3)
        loss = bce(scaled, y_t)
        loss.backward()
        return loss

    optim.step(closure)
    return float(torch.exp(log_T).detach().cpu().item())


def apply_temperature(logits: np.ndarray, temperature: float) -> np.ndarray:
    t = max(temperature, 1e-3)
    return 1.0 / (1.0 + np.exp(-logits / t))