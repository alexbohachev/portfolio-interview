"""Створення розширеного набору з 50 складних запитів (40 answerable + 10 unanswerable)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "data" / "golden" / "hard_retrieval_extended.json"

TOPICS = [
    ("wheat_disease", "Хвороби пшениці", ["бура іржа", "септоріоз", "фузаріоз"], 0),
    ("corn_irrigation", "Зрошення кукурудзи", ["краплинне", "вологоємність грунту", "борознева"], 20),
    ("soil_ph", "Кислотність грунту", ["вапнування", "pH 6.0", "лімаш"], 40),
    ("npk_fertilizer", "Мінеральні добрива NPK", ["азот", "фосфор", "калій"], 60),
    ("organic_matter", "Гумус та органіка", ["сігальні культури", "компост", "органіка"], 80),
    ("pest_ipm", "Інтегрований захист від шкідників", ["трихограма", "феромони", "економічний поріг"], 100),
    ("herbicide", "Гербіциди та бур'яни", ["гліфосат", "2,4-D", "добірка"], 120),
    ("seed_rate", "Норма висіву", ["щільність", "гібрид", "проростки"], 140),
    ("crop_rotation", "Сівозміна", ["пар", "бобові", "фітосанітарія"], 160),
    ("sunflower", "Агротехнологія соняшнику", ["олійність", "байрачний", "висота рослин"], 180),
]

YEARS = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]

queries = []
q_idx = 1

# Generate 40 answerable queries (4 per topic)
for topic_code, topic_title, keywords, offset in TOPICS:
    for variant in range(4):
        doc_num = variant * 4 + 1  # 1, 5, 9, 13
        doc_id = f"agri_{offset + doc_num:03d}_{topic_code}_{doc_num - 1}"
        year = YEARS[(doc_num - 1) % len(YEARS)]
        kw = keywords[(doc_num - 1) % len(keywords)]
        
        if variant == 0:
            question = f"Які заходи щодо {topic_title.lower()} та фактора «{kw}» описані для сезону {year}?"
            q_type = "paraphrase"
        elif variant == 1:
            question = f"Як впливає {kw} на урожайність у сезоні {year} в контексті {topic_title.lower()}?"
            q_type = "specific_factor"
        elif variant == 2:
            question = f"Вимоги до застосування «{kw}» у польових роботах {year} року"
            q_type = "technical_spec"
        else:
            question = f"Аналіз польових результатів: {topic_title.lower()} та динаміка «{kw}» за {year} рік"
            q_type = "multi_aspect"

        queries.append({
            "id": f"ext_{q_idx:03d}",
            "topic": topic_code,
            "type": q_type,
            "answerable": True,
            "question": question,
            "expected_contains": kw,
            "evidence": [{"doc_id": doc_id}]
        })
        q_idx += 1

# 10 Unanswerable queries (testing refusal gate)
UNANSWERABLE = [
    "Чи доцільно використовувати квантові комп'ютери для розрахунку NPK у 2026 році?",
    "Як вирощувати банани у відкритому ґрунті під Полтавою без теплиць?",
    "Чи ліцензовано блокчейн Ethereum для контролю сівозміни в агрохолдингах?",
    "Яка норма внесення марсіанського ґрунту під озиму пшеницю?",
    "Чи захищає графітовий наноматеріал кукурудзу від заморозків?",
    "Використання термоядерного синтезу для підігріву ґрунту взимку",
    "Чи реєструвався крипто-токен AGRI_COIN як сертифікат насіння в Україні?",
    "Які хвороби соняшнику викликані впливом супутників Starlink?",
    "Чи можна замінити трихограму на наноботів для боротьби з совкою?",
    "Як використовувати лазерне супутникове опромінення для боротьби з бур'янами?",
]

for text in UNANSWERABLE:
    queries.append({
        "id": f"ext_{q_idx:03d}",
        "topic": "out_of_domain",
        "type": "unanswerable",
        "answerable": False,
        "question": text,
        "evidence": []
    })
    q_idx += 1

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
OUT_PATH.write_text(json.dumps(queries, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Generated {len(queries)} queries ({len(queries)-len(UNANSWERABLE)} answerable + {len(UNANSWERABLE)} unanswerable) in {OUT_PATH}")
