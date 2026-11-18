from work06.generate import extractive_answer
from work06.retriever import VerseHit


def test_extractive_answer_lists_citations():
    hits = [
        VerseHit(osis_id="Gen.1.1", text="Текст вірша один.", translation_id="uk_ubk_stub", score=0.9),
        VerseHit(osis_id="Gen.1.2", text="Текст вірша два.", translation_id="uk_ubk_stub", score=0.8),
    ]
    ans = extractive_answer("Що про творіння?", hits)
    assert "Gen.1.1" in ans
    assert "Gen.1.2" in ans


def test_extractive_empty():
    assert "Немає" in extractive_answer("?", [])