from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from work01.data import build_sklearn_preprocessor


class MLP(nn.Module):
    def __init__(self, in_dim: int, hidden_dims: list[int], dropout: float) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        prev = in_dim
        for h in hidden_dims:
            layers.extend([nn.Linear(prev, h), nn.ReLU(), nn.Dropout(dropout)])
            prev = h
        layers.append(nn.Linear(prev, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x).squeeze(-1)


@dataclass
class TrainResult:
    model: MLP
    preprocessor: Any
    best_state: dict[str, Any]
    n_epochs: int


def _to_tensor(x: np.ndarray, device: torch.device) -> torch.Tensor:
    return torch.as_tensor(x, dtype=torch.float32, device=device)


def train_candidate(
    x_train_df,
    y_train: np.ndarray,
    x_val_df,
    y_val: np.ndarray,
    cfg: dict[str, Any],
    seed: int,
) -> TrainResult:
    torch.manual_seed(seed)
    np.random.seed(seed)
    device = torch.device("cpu")

    pre = build_sklearn_preprocessor(x_train_df)
    x_train = pre.fit_transform(x_train_df)
    x_val = pre.transform(x_val_df)

    cand_cfg = cfg["candidate"]
    model = MLP(
        in_dim=x_train.shape[1],
        hidden_dims=cand_cfg["hidden_dims"],
        dropout=cand_cfg["dropout"],
    ).to(device)

    pos = max(int(y_train.sum()), 1)
    neg = max(len(y_train) - int(y_train.sum()), 1)
    pos_weight = torch.tensor([neg / pos], dtype=torch.float32, device=device)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optim = torch.optim.AdamW(
        model.parameters(),
        lr=cand_cfg["learning_rate"],
        weight_decay=cand_cfg["weight_decay"],
    )

    train_ds = TensorDataset(
        _to_tensor(x_train, device),
        _to_tensor(y_train.astype(np.float32), device),
    )
    loader = DataLoader(train_ds, batch_size=cand_cfg["batch_size"], shuffle=True)

    x_val_t = _to_tensor(x_val, device)
    y_val_t = _to_tensor(y_val.astype(np.float32), device)

    best_val = float("inf")
    best_state: dict[str, Any] | None = None
    patience = cand_cfg["early_stopping_patience"]
    stale = 0
    epochs_run = 0

    for epoch in range(cand_cfg["max_epochs"]):
        epochs_run = epoch + 1
        model.train()
        for xb, yb in loader:
            optim.zero_grad()
            logits = model(xb)
            loss = criterion(logits, yb)
            loss.backward()
            optim.step()

        model.eval()
        with torch.no_grad():
            val_logits = model(x_val_t)
            val_loss = criterion(val_logits, y_val_t).item()

        if val_loss < best_val - 1e-5:
            best_val = val_loss
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            stale = 0
        else:
            stale += 1
            if stale >= patience:
                break

    if best_state is not None:
        model.load_state_dict(best_state)

    return TrainResult(model=model, preprocessor=pre, best_state=best_state or {}, n_epochs=epochs_run)


def predict_proba(result: TrainResult, x_df) -> np.ndarray:
    x = result.preprocessor.transform(x_df)
    model = result.model
    model.eval()
    with torch.no_grad():
        logits = model(_to_tensor(x, next(model.parameters()).device))
        probs = torch.sigmoid(logits).cpu().numpy()
    return probs