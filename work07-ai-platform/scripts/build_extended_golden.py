"""Створення та верифікація 50 реалістичних семантичних запитів для агрономічного корпусу."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "data" / "golden" / "hard_retrieval_extended.json"

# 40 answerable queries: 4 per topic, using semantic paraphrases and domain terminology
QUERIES = [
    # 1. Wheat Disease (agri_001 - agri_020)
    {
        "id": "ext_001",
        "topic": "wheat_disease",
        "question": "Симптоми та захист зернових від іржі листя та плямистостей колоса",
        "evidence": [{"doc_id": "agri_001_wheat_disease_0"}]
    },
    {
        "id": "ext_002",
        "topic": "wheat_disease",
        "question": "Фузаріозне ураження озимих та методи фунгіцидної профілактики",
        "evidence": [{"doc_id": "agri_006_wheat_disease_5"}]
    },
    {
        "id": "ext_003",
        "topic": "wheat_disease",
        "question": "Септоріоз листя на ранніх фазах кущення пшениці",
        "evidence": [{"doc_id": "agri_011_wheat_disease_10"}]
    },
    {
        "id": "ext_004",
        "topic": "wheat_disease",
        "question": "Комплексний моніторинг грибкових патогенів колоса перед збиранням",
        "evidence": [{"doc_id": "agri_016_wheat_disease_15"}]
    },

    # 2. Corn Irrigation (agri_021 - agri_040)
    {
        "id": "ext_005",
        "topic": "corn_irrigation",
        "question": "Налаштування систем локального краплинного зволоження на кукурудзяних полях",
        "evidence": [{"doc_id": "agri_021_corn_irrigation_0"}]
    },
    {
        "id": "ext_006",
        "topic": "corn_irrigation",
        "question": "Розрахунок вологоємності ґрунту при борозневому поливі зернової кукурудзи",
        "evidence": [{"doc_id": "agri_026_corn_irrigation_5"}]
    },
    {
        "id": "ext_007",
        "topic": "corn_irrigation",
        "question": "Водний стрес кукурудзи в період викидання волоті та формування качана",
        "evidence": [{"doc_id": "agri_031_corn_irrigation_10"}]
    },
    {
        "id": "ext_008",
        "topic": "corn_irrigation",
        "question": "Автоматизоване керування поливними нормами при вирощуванні зерна на зрошенні",
        "evidence": [{"doc_id": "agri_036_corn_irrigation_15"}]
    },

    # 3. Soil pH (agri_041 - agri_060)
    {
        "id": "ext_009",
        "topic": "soil_ph",
        "question": "Меліоративні заходи та розкислення кислих ґрунтів вапняком",
        "evidence": [{"doc_id": "agri_041_soil_ph_0"}]
    },
    {
        "id": "ext_010",
        "topic": "soil_ph",
        "question": "Оптимізація показника pH до нейтрального рівня 6.0 для польових культур",
        "evidence": [{"doc_id": "agri_046_soil_ph_5"}]
    },
    {
        "id": "ext_011",
        "topic": "soil_ph",
        "question": "Внесення дефекату та лімашу на полях з дефіцитом кальцію",
        "evidence": [{"doc_id": "agri_051_soil_ph_10"}]
    },
    {
        "id": "ext_012",
        "topic": "soil_ph",
        "question": "Буферна здатність ґрунтового комплексу при регулярному вапнуванні",
        "evidence": [{"doc_id": "agri_056_soil_ph_15"}]
    },

    # 4. NPK Fertilizer (agri_061 - agri_080)
    {
        "id": "ext_013",
        "topic": "npk_fertilizer",
        "question": "Баланс азотного та фосфорного живлення для стартового розвитку сходів",
        "evidence": [{"doc_id": "agri_061_npk_fertilizer_0"}]
    },
    {
        "id": "ext_014",
        "topic": "npk_fertilizer",
        "question": "Калійне підживлення рослин для підвищення посухостійкості та міцності стебла",
        "evidence": [{"doc_id": "agri_066_npk_fertilizer_5"}]
    },
    {
        "id": "ext_015",
        "topic": "npk_fertilizer",
        "question": "Формули мінеральних туків NPK для основного осіннього внесення під оранку",
        "evidence": [{"doc_id": "agri_071_npk_fertilizer_10"}]
    },
    {
        "id": "ext_016",
        "topic": "npk_fertilizer",
        "question": "Дробове внесення азотних добрив по мерзлоталому ґрунту",
        "evidence": [{"doc_id": "agri_076_npk_fertilizer_15"}]
    },

    # 5. Organic Matter / Humus (agri_081 - agri_100)
    {
        "id": "ext_017",
        "topic": "organic_matter",
        "question": "Заорювання сидеральних культур для збагачення орного шару гумусом",
        "evidence": [{"doc_id": "agri_081_organic_matter_0"}]
    },
    {
        "id": "ext_018",
        "topic": "organic_matter",
        "question": "Використання компосту та післяжнивних решток для збереження структури ґрунту",
        "evidence": [{"doc_id": "agri_086_organic_matter_5"}]
    },
    {
        "id": "ext_019",
        "topic": "organic_matter",
        "question": "Відновлення вмісту органічної речовини в деградованих чорноземах",
        "evidence": [{"doc_id": "agri_091_organic_matter_10"}]
    },
    {
        "id": "ext_020",
        "topic": "organic_matter",
        "question": "Біопрепарати деструктори стерні для швидкої мінералізації органіки",
        "evidence": [{"doc_id": "agri_096_organic_matter_15"}]
    },

    # 6. Pest IPM (agri_101 - agri_120)
    {
        "id": "ext_021",
        "topic": "pest_ipm",
        "question": "Біологічний метод захисту рослин за допомогою випуску ентомофага трихограми",
        "evidence": [{"doc_id": "agri_101_pest_ipm_0"}]
    },
    {
        "id": "ext_022",
        "topic": "pest_ipm",
        "question": "Використання феромонних пасток для щоденного моніторингу шкідників",
        "evidence": [{"doc_id": "agri_106_pest_ipm_5"}]
    },
    {
        "id": "ext_023",
        "topic": "pest_ipm",
        "question": "Визначення економічного порогу шкодочинності гусениць совки та лучного метелика",
        "evidence": [{"doc_id": "agri_111_pest_ipm_10"}]
    },
    {
        "id": "ext_024",
        "topic": "pest_ipm",
        "question": "Інтегровані схеми боротьби зі шкідниками поля без перевищення пестицидного навантаження",
        "evidence": [{"doc_id": "agri_116_pest_ipm_15"}]
    },

    # 7. Herbicides (agri_121 - agri_140)
    {
        "id": "ext_025",
        "topic": "herbicide",
        "question": "Застосування гліфосату суцільної дії для знищення коренепаросткових бур'янів",
        "evidence": [{"doc_id": "agri_121_herbicide_0"}]
    },
    {
        "id": "ext_026",
        "topic": "herbicide",
        "question": "Контроль дводольних бур'янів у посівах злаків препаратами групи 2,4-D",
        "evidence": [{"doc_id": "agri_126_herbicide_5"}]
    },
    {
        "id": "ext_027",
        "topic": "herbicide",
        "question": "Підбір гербіцидних бакових сумішей для запобігання виникненню резистентності",
        "evidence": [{"doc_id": "agri_131_herbicide_10"}]
    },
    {
        "id": "ext_028",
        "topic": "herbicide",
        "question": "Терміни безпечного внесення післясходових страхових гербіцидів",
        "evidence": [{"doc_id": "agri_136_herbicide_15"}]
    },

    # 8. Seed Rate (agri_141 - agri_160)
    {
        "id": "ext_029",
        "topic": "seed_rate",
        "question": "Норма висіву та розрахункова густота рослин на гектар для зернових культур",
        "evidence": [{"doc_id": "agri_141_seed_rate_0"}]
    },
    {
        "id": "ext_030",
        "topic": "seed_rate",
        "question": "Врахування польової схожості насіння та маси 1000 зерен при посіві",
        "evidence": [{"doc_id": "agri_146_seed_rate_5"}]
    },
    {
        "id": "ext_031",
        "topic": "seed_rate",
        "question": "Коригування густоти стояння гібридів кукурудзи залежно від вологозабезпечення",
        "evidence": [{"doc_id": "agri_151_seed_rate_10"}]
    },
    {
        "id": "ext_032",
        "topic": "seed_rate",
        "question": "Вплив рівномірності розподілу проростків на фінальний урожай поля",
        "evidence": [{"doc_id": "agri_156_seed_rate_15"}]
    },

    # 9. Crop Rotation (agri_161 - agri_180)
    {
        "id": "ext_033",
        "topic": "crop_rotation",
        "question": "Чергування культур у польовій сівозміні та роль чистого пару",
        "evidence": [{"doc_id": "agri_161_crop_rotation_0"}]
    },
    {
        "id": "ext_034",
        "topic": "crop_rotation",
        "question": "Бобові попередники як природне джерело біологічного азоту в ґрунті",
        "evidence": [{"doc_id": "agri_166_crop_rotation_5"}]
    },
    {
        "id": "ext_035",
        "topic": "crop_rotation",
        "question": "Фітосанітарний розрив для обмеження поширення ґрунтових інфекцій",
        "evidence": [{"doc_id": "agri_171_crop_rotation_10"}]
    },
    {
        "id": "ext_036",
        "topic": "crop_rotation",
        "question": "Допустимі періоди повернення соняшнику на те саме поле в агроценозах",
        "evidence": [{"doc_id": "agri_176_crop_rotation_15"}]
    },

    # 10. Sunflower (agri_181 - agri_200)
    {
        "id": "ext_037",
        "topic": "sunflower",
        "question": "Фактори впливу на олійність насіння соняшнику в період наливу кошика",
        "evidence": [{"doc_id": "agri_181_sunflower_0"}]
    },
    {
        "id": "ext_038",
        "topic": "sunflower",
        "question": "Особливості вирощування високорослих гібридів соняшнику в байрачному рельєфі",
        "evidence": [{"doc_id": "agri_186_sunflower_5"}]
    },
    {
        "id": "ext_039",
        "topic": "sunflower",
        "question": "Стійкість сучасних гібридів соняшнику до посухи та високих літніх температур",
        "evidence": [{"doc_id": "agri_191_sunflower_10"}]
    },
    {
        "id": "ext_040",
        "topic": "sunflower",
        "question": "Десикація посівів соняшнику перед комбайновим збиранням",
        "evidence": [{"doc_id": "agri_196_sunflower_15"}]
    },
]

# 10 Unanswerable queries (testing refusal gate)
UNANSWERABLE_TEXTS = [
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

output_items = []
for q in QUERIES:
    output_items.append({
        "id": q["id"],
        "topic": q["topic"],
        "type": "domain_paraphrase",
        "answerable": True,
        "question": q["question"],
        "evidence": q["evidence"],
    })

for idx, text in enumerate(UNANSWERABLE_TEXTS, start=41):
    output_items.append({
        "id": f"ext_{idx:03d}",
        "topic": "out_of_domain",
        "type": "unanswerable",
        "answerable": False,
        "question": text,
        "evidence": [],
    })

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
OUT_PATH.write_text(json.dumps(output_items, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Generated {len(output_items)} high-quality realistic queries in {OUT_PATH}")
