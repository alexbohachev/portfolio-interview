from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from work01 import baseline, candidate, metrics
from work01.config import config_fingerprint, load_config
from work01.data import load_dataset, prepare_features_target, split_indices
from work01.paths import ARTIFACTS, CONFIG_PATH, DATA_RAW, MANIFEST_PATH, REPORT_PATH


def _update_manifest_config_hash(fingerprint: str) -> None:
    with MANIFEST_PATH.open(encoding="utf-8") as f:
        manifest = json.load(f)
    manifest["config_hash"] = fingerprint
    with MANIFEST_PATH.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")


def run_all() -> dict[str, Any]:
    t0 = time.perf_counter()
    cfg = load_config(CONFIG_PATH)
    fingerprint = config_fingerprint(cfg)
    _update_manifest_config_hash(fingerprint)

    df, data_meta = load_dataset(cfg, DATA_RAW)
    x, y = prepare_features_target(df, cfg["data"]["target"], cfg["data"]["drop_columns"])
    train_idx, val_idx, test_idx = split_indices(cfg, len(df))

    x_train, y_train = x.iloc[train_idx], y[train_idx]
    x_val, y_val = x.iloc[val_idx], y[val_idx]
    x_test, y_test = x.iloc[test_idx], y[test_idx]

    base_pipe = baseline.train_baseline(x_train, y_train, cfg, x_train)
    base_prob = baseline.predict_proba(base_pipe, x_test)
    base_scores = metrics.classification_scores(y_test, base_prob)

    seed_scores: list[dict[str, float]] = []
    last_result = None
    for seed in cfg["seeds"]:
        last_result = candidate.train_candidate(x_train, y_train, x_val, y_val, cfg, seed)
        cand_prob = candidate.predict_proba(last_result, x_test)
        seed_scores.append(metrics.classification_scores(y_test, cand_prob))

    def mean_key(key: str) -> float:
        return float(np.mean([s[key] for s in seed_scores]))

    cand_prob_final = candidate.predict_proba(last_result, x_test)  # type: ignore[arg-type]
    cand_scores = metrics.classification_scores(y_test, cand_prob_final)

    boot_cfg = cfg["bootstrap"]
    ci_f1 = metrics.bootstrap_metric_diff(
        y_test,
        base_prob,
        cand_prob_final,
        lambda yt, pr: metrics.classification_scores(yt, pr)["macro_f1"],
        n_resamples=boot_cfg["n_resamples"],
        ci=boot_cfg["ci"],
        seed=cfg["seed"],
    )

    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    joblib.dump(base_pipe, ARTIFACTS / "baseline.joblib")
    joblib.dump(
        {"preprocessor": last_result.preprocessor, "state_dict": last_result.best_state, "cfg": cfg},
        ARTIFACTS / "candidate_bundle.joblib",
    )

    results = {
        "data": data_meta,
        "fingerprint": fingerprint,
        "baseline_test": base_scores,
        "candidate_test": cand_scores,
        "candidate_seed_spread": {
            "macro_f1_mean": mean_key("macro_f1"),
            "macro_f1_std": float(np.std([s["macro_f1"] for s in seed_scores])),
            "brier_mean": mean_key("brier"),
            "brier_std": float(np.std([s["brier"] for s in seed_scores])),
            "pr_auc_mean": mean_key("pr_auc"),
            "pr_auc_std": float(np.std([s["pr_auc"] for s in seed_scores])),
        },
        "bootstrap_macro_f1_diff": {
            "point": ci_f1.point,
            "ci_low": ci_f1.low,
            "ci_high": ci_f1.high,
        },
        "n_test": int(len(y_test)),
        "elapsed_sec": round(time.perf_counter() - t0, 2),
        "seeds": cfg["seeds"],
    }

    with (ARTIFACTS / "results.json").open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        f.write("\n")

    _write_report(results)
    return results


def _write_report(results: dict[str, Any]) -> None:
    b = results["baseline_test"]
    c = results["candidate_test"]
    spread = results["candidate_seed_spread"]
    boot = results["bootstrap_macro_f1_diff"]
    lines = [
        "# Звіт — робота 1: навчання й оцінювання моделей",
        "",
        "## Задача",
        "Бінарна класифікація підписки на депозит (UCI Bank Marketing, `bank-full.csv`), ознака `duration` виключена.",
        "",
        "## Дані",
        f"- SHA-256 архіву: `{results['data']['zip_sha256']}`",
        f"- Test: {results['n_test']} прикладів (фіксований часовий split, див. `manifests/test_manifest.json`)",
        "",
        "## Методи",
        "- **Baseline:** логістична регресія (sklearn Pipeline + OneHotEncoder)",
        "- **Candidate:** MLP у PyTorch, early stopping за val loss, 5 seed для оцінки нестабільності",
        "",
        "## Результати (test, один прогон candidate — останній seed)",
        "",
        "| Метрика | Baseline | Candidate |",
        "|---------|----------|-----------|",
        f"| macro-F1 | {b['macro_f1']:.4f} | {c['macro_f1']:.4f} |",
        f"| Brier | {b['brier']:.4f} | {c['brier']:.4f} |",
        f"| PR-AUC | {b['pr_auc']:.4f} | {c['pr_auc']:.4f} |",
        "",
        "## Нестабільність навчання (5 seed, test)",
        "",
        f"- macro-F1: {spread['macro_f1_mean']:.4f} ± {spread['macro_f1_std']:.4f}",
        f"- Brier: {spread['brier_mean']:.4f} ± {spread['brier_std']:.4f}",
        f"- PR-AUC: {spread['pr_auc_mean']:.4f} ± {spread['pr_auc_std']:.4f}",
        "",
        "## Bootstrap різниці macro-F1 (candidate − baseline, test)",
        "",
        f"- Точка: {boot['point']:.4f}",
        f"- 95% CI: [{boot['ci_low']:.4f}, {boot['ci_high']:.4f}]",
        "",
        "## Обмеження",
        "- Часовий shift частки `yes` між train/val/test; поріг 0.5 не оптимізувався на test.",
        "- Один фінальний candidate checkpoint (останній seed); ablation не виконувались.",
        "",
        "## Наступний крок",
        "- Підбір порогу за validation (ціна FP/FN) і калібрування ймовірностей.",
        "",
        f"_Згенеровано автоматично; час виконання `make all`: ~{results['elapsed_sec']} с._",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")