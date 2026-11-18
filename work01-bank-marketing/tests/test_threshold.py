import numpy as np

from work01.threshold import tune_threshold_macro_f1


def test_tune_threshold_improves_over_half():
    y = np.array([0, 0, 0, 1, 1, 1])
    prob = np.array([0.1, 0.2, 0.4, 0.6, 0.8, 0.9])
    t, f1 = tune_threshold_macro_f1(y, prob)
    assert 0.05 <= t <= 0.95
    f1_half = __import__("sklearn.metrics", fromlist=["f1_score"]).f1_score(
        y, (prob >= 0.5).astype(int), average="macro"
    )
    assert f1 >= f1_half - 1e-9