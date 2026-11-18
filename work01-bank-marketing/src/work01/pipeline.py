from __future__ import annotations

import json
import time
from typing import Any

import joblib
import numpy as np

from work01 import baseline, candidate, metrics
from work01.calibration import apply_temperature, fit_temperature
from work01.config import config_fingerprint, load_config
from work01.data import load_dataset, prepare_features_target, split_indices
from work01.errors import build_error_analysis
from work01.paths import ARTIFACTS, CONFIG_PATH, DATA_RAW, MANIFEST_PATH, REPORT_PATH
from work01.threshold import tune_threshold_macro_f1


def _load_locked_manifest() -> dict[str, Any]:
    with MANIFEST_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def _scores_at_threshold(y: np.ndarray, prob: np.ndarray, threshold: float) -> dict[str, float]:
    return metrics.classification_scores(y, prob, threshold=threshold)


def run_all() -> dict[str, Any]:
    t0 = time.perf_counter()
    cfg = load_config(CONFIG_PATH)
    fingerprint = config_fingerprint(cfg)
    manifest = _load_locked_manifest()
    locked_hash = manifest.get("config_hash")
    if locked_hash and locked_hash != fingerprint:
        raise RuntimeError(
            f"config_hash у manifest ({locked_hash}) не збігається з config/default.yaml ({fingerprint}). "
            "Оновіть manifest лише до нового test-прогону."
        )

    df, data_meta = load_dataset(cfg, DATA_RAW)
    x, y = prepare_features_target(df, cfg["data"]["target"], cfg["data"]["drop_columns"])
    train_idx, val_idx, test_idx = split_indices(cfg, len(df))

    x_train, y_train = x.iloc[train_idx], y[train_idx]
    x_val, y_val = x.iloc[val_idx], y[val_idx]
    x_test, y_test = x.iloc[test_idx], y[test_idx]

    base_pipe = baseline.train_baseline(x_train, y_train, cfg, x_train)
    base_prob_val = baseline.predict_proba(base_pipe, x_val)
    base_thresh, _ = tune_threshold_macro_f1(y_val, base_prob_val)
    base_prob_test = baseline.predict_proba(base_pipe, x_test)

    val_f1_by_seed: list[float] = []
    candidates: list[candidate.TrainResult] = []
    for seed in cfg["seeds"]:
        res = candidate.train_candidate(x_train, y_train, x_val, y_val, cfg, seed)
        val_logits = candidate.predict_logits(res, x_val)
        res.temperature = fit_temperature(val_logits, y_val)
        val_prob = apply_temperature(val_logits, res.temperature)
        _, val_f1 = tune_threshold_macro_f1(y_val, val_prob)
        val_f1_by_seed.append(val_f1)
        candidates.append(res)

    best_i = int(np.argmax(val_f1_by_seed))
    best_model = candidates[best_i]
    cand_logits_val = candidate.predict_logits(best_model, x_val)
    cand_logits_test = candidate.predict_logits(best_model, x_test)
    cand_prob_val = apply_temperature(cand_logits_val, best_model.temperature)
    cand_prob_test = apply_temperature(cand_logits_test, best_model.temperature)
    cand_thresh, _ = tune_threshold_macro_f1(y_val, cand_prob_val)

    base_scores = _scores_at_threshold(y_test, base_prob_test, base_thresh)
    cand_scores = _scores_at_threshold(y_test, cand_prob_test, cand_thresh)
    cand_ablation_fixed_05 = _scores_at_threshold(y_test, cand_prob_test, 0.5)

    boot_cfg = cfg["bootstrap"]
    n = len(y_test)

    def macro_f1_diff_on_subset(idx: np.ndarray) -> float:
        yt = y_test[idx]
        return (
            metrics.classification_scores(yt, cand_prob_test[idx], threshold=cand_thresh)["macro_f1"]
            - metrics.classification_scores(yt, base_prob_test[idx], threshold=base_thresh)["macro_f1"]
        )

    rng = np.random.default_rng(cfg["seed"])
    diffs = [macro_f1_diff_on_subset(rng.integers(0, n, size=n)) for _ in range(boot_cfg["n_resamples"])]
    diffs_arr = np.asarray(diffs, dtype=np.float64)
    alpha = (1 - boot_cfg["ci"]) / 2
    ci_f1 = {
        "point": float(np.mean(diffs_arr)),
        "ci_low": float(np.quantile(diffs_arr, alpha)),
        "ci_high": float(np.quantile(diffs_arr, 1 - alpha)),
    }

    error_analysis = build_error_analysis(x_test, y_test, cand_prob_test, cand_thresh)

    pos_rate = {
        "train": round(float(y_train.mean()), 4),
        "val": round(float(y_val.mean()), 4),
        "test": round(float(y_test.mean()), 4),
    }

    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    joblib.dump(base_pipe, ARTIFACTS / "baseline.joblib")
    joblib.dump(
        {
            "preprocessor": best_model.preprocessor,
            "state_dict": best_model.best_state,
            "temperature": best_model.temperature,
            "selected_seed": best_model.seed,
            "threshold": cand_thresh,
        },
        ARTIFACTS / "candidate_bundle.joblib",
    )

    results: dict[str, Any] = {
        "data": data_meta,
        "fingerprint": fingerprint,
        "class_balance": pos_rate,
        "thresholds": {"baseline": base_thresh, "candidate": cand_thresh},
        "model_selection": {
            "candidate_seed": int(best_model.seed),
            "val_macro_f1_by_seed": [round(v, 4) for v in val_f1_by_seed],
            "val_macro_f1_std": round(float(np.std(val_f1_by_seed)), 4),
        },
        "baseline_test": base_scores,
        "candidate_test": cand_scores,
        "ablation_candidate_threshold_0_5": cand_ablation_fixed_05,
        "bootstrap_macro_f1_diff": ci_f1,
        "error_analysis": error_analysis,
        "n_test": int(len(y_test)),
        "elapsed_sec": round(time.perf_counter() - t0, 2),
        "seeds": cfg["seeds"],
    }

    with (ARTIFACTS / "results.json").open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        f.write("\n")

    with (ARTIFACTS / "error_cases.json").open("w", encoding="utf-8") as f:
        json.dump(error_analysis, f, indent=2, ensure_ascii=False)
        f.write("\n")

    _write_report(results)
    return results


def _write_report(results: dict[str, Any]) -> None:
    b = results["baseline_test"]
    c = results["candidate_test"]
    abl = results["ablation_candidate_threshold_0_5"]
    boot = results["bootstrap_macro_f1_diff"]
    bal = results["class_balance"]
    thr = results["thresholds"]
    sel = results["model_selection"]
    err = results["error_analysis"]

    lines = [
        "# Звіт — робота 1: навчання й оцінювання моделей",
        "",
        "## Задача",
        "Бінарна класифікація підписки на депозит (UCI Bank Marketing, `bank-full.csv`), ознака `duration` виключена.",
        "",
        "## Дані",
        f"- SHA-256 `bank-full.csv`: `{results['data']['csv_sha256']}`",
        f"- Test: {results['n_test']} прикладів (фіксований часовий split, `manifests/test_manifest.json`)",
        f"- Частка `yes`: train {bal['train']}, val {bal['val']}, test {bal['test']} (часовий shift)",
        "",
        "## Метод",
        "- **Baseline:** логістична регресія (`class_weight=balanced`), поріг macro-F1 на validation",
        f"- **Candidate:** MLP + early stopping (val macro-F1), temperature scaling на validation, вибір seed {sel['candidate_seed']} за val macro-F1",
        f"- **Ablation:** candidate з фіксованим порогом 0.5 (без підбору) — для порівняння",
        "",
        "## Результати (test, один прогон)",
        "",
        "| Метрика | Baseline | Candidate |",
        "|---------|----------|-----------|",
        f"| macro-F1 | {b['macro_f1']:.4f} | {c['macro_f1']:.4f} |",
        f"| Brier | {b['brier']:.4f} | {c['brier']:.4f} |",
        f"| PR-AUC | {b['pr_auc']:.4f} | {c['pr_auc']:.4f} |",
        "",
        f"Пороги (підібрані на val): baseline={thr['baseline']:.2f}, candidate={thr['candidate']:.2f}.",
        "",
        "### Ablation: candidate, поріг 0.5",
        f"- macro-F1={abl['macro_f1']:.4f}, Brier={abl['brier']:.4f}, PR-AUC={abl['pr_auc']:.4f}",
        "",
        "## Нестабільність навчання (5 seed, **validation** macro-F1)",
        "",
        f"- значення: {sel['val_macro_f1_by_seed']}",
        f"- std: {sel['val_macro_f1_std']:.4f}",
        "",
        "## Bootstrap різниці macro-F1 (candidate − baseline, test, фіксовані пороги)",
        "",
        f"- Точка: {boot['point']:.4f}",
        f"- 95% CI: [{boot['ci_low']:.4f}, {boot['ci_high']:.4f}]",
        "",
        "## Аналіз помилок (candidate)",
        "",
        f"- Помилок на test: {err['n_errors']} / {err['n_test']} ({err['error_rate']:.1%})",
        "",
        "**Групи (усі помилки на test):**",
        "",
    ]
    for bucket, count in sorted(err["bucket_counts_errors_only"].items(), key=lambda x: -x[1]):
        lines.append(f"- {bucket}: {count}")

    lines.extend(["", "**Розібрані приклади (до 20):**", ""])
    for case in err["cases"]:
        yt = "yes" if case["y_true"] == 1 else "no"
        yp = "yes" if case["y_pred"] == 1 else "no"
        lines.append(
            f"- рядок {case['row_1based']}: true={yt}, pred={yp}, p={case['prob_yes']:.3f}, "
            f"{case['bucket']}, age={case['age']}, month={case['month']}"
        )

    lines.extend(
        [
            "",
            "### Висновки з помилок",
            "1. **Часовий shift** — test має набагато вищу частку `yes`; поріг з val часто завищений для test.",
            "2. **FN_borderline** — модель недооцінює `yes` у новішому періоді (кампанії/сезонність `month`).",
            "3. **FP_high_confidence** — рідкісні перепідтвердження `yes` при фактичному `no` після калібрування.",
            "",
            "## Обмеження",
            "- Один фінальний прогон test; пороги зафіксовані з validation.",
            "- Temperature scaling не компенсує повністю covariate shift між val і test.",
            "- MLP без явних cross-фіч; логістична регресія сильна на табличних даних.",
            "",
            "## Наступний крок",
            "- Часовий re-fit / окремий калібратор на останньому вікні; або модель із явною `month`/кампанійною ознакою часу.",
            "",
            f"_Автогенерація; час `make all`: ~{results['elapsed_sec']} с._",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")