import numpy as np

from work02.gate import tune_refusal_threshold


class _FakeRetriever:
    def __init__(self, table):
        self.table = table

    def search_hybrid(self, query, k):
        class H:
            def __init__(self, score):
                self.score = score

        return [H(self.table[query])]


def test_gate_picks_threshold():
    retriever = _FakeRetriever({"a": 0.2, "b": 0.01, "c": 0.15})
    dev = [
        {"question": "a", "answerable": True},
        {"question": "c", "answerable": True},
        {"question": "b", "answerable": False},
    ]
    t, _ = tune_refusal_threshold(retriever, dev, k=1, grid=np.array([0.05, 0.1, 0.12]))
    assert t >= 0.05