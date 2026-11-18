"""40 спостережень: dev 20 / test 20 з множиною прийнятних дій (ТЗ)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DEV = ROOT / "data" / "golden" / "recommendations_dev.json"
OUT_TEST = ROOT / "data" / "golden" / "recommendations_test.json"

SCENARIOS = [
    ("бура іржа на листі пшениці", ["spray_fungicide", "rescout_7d", "disease_lab_test"]),
    ("метелики в пшеничному полі феромони", ["ipm_scouting", "beneficial_release", "trap_crops"]),
    ("посуха низька вологість кукурудза", ["adjust_irrigation", "moisture_sensor", "irrigation_pressure"]),
    ("кислий ґрунт pH вапнування", ["soil_lime", "soil_sampling_grid", "nitrogen_topdress"]),
    ("бур'яни в смузі між рядами", ["herbicide_band", "resistance_rotation", "equipment_clean"]),
    ("норма висіву занадто густа", ["seed_rate_review", "nitrogen_topdress", "tillage_depth"]),
    ("дефіцит азоту у фазі кущіння", ["nitrogen_topdress", "foliar_fertilizer", "soil_sampling_grid"]),
    ("зрошення краплинна система", ["adjust_irrigation", "irrigation_pressure", "moisture_sensor"]),
    ("шкідники над економічним порогом", ["ipm_scouting", "beneficial_release", "weather_hold"]),
    ("септоріоз на нижніх листках", ["spray_fungicide", "rescout_7d", "resistance_rotation"]),
]


def expand_scenarios(n: int, prefix: str) -> list[dict]:
    rows: list[dict] = []
    i = 0
    variant_suffix = [
        "",
        " північне поле F-001",
        " південне поле F-002",
        " — терміновий сигнал",
        " (повторне спостереження)",
    ]
    while len(rows) < n:
        note, acceptable = SCENARIOS[i % len(SCENARIOS)]
        suf = variant_suffix[(len(rows) // len(SCENARIOS)) % len(variant_suffix)]
        rows.append(
            {
                "field_id": "F-00" + str((len(rows) % 2) + 1),
                "note": note + suf,
                "acceptable_action_ids": acceptable,
            }
        )
        i += 1
    for j, row in enumerate(rows):
        row["id"] = f"{prefix}_{j + 1:03d}"
    return rows


def main() -> None:
    dev = expand_scenarios(20, "rec_dev")
    test_notes = [
        ("фузаріоз колосся озимої", ["spray_fungicide", "rescout_7d"]),
        ("трихограма проти метеликів", ["ipm_scouting", "beneficial_release"]),
        ("вологоємність нижче 25%", ["adjust_irrigation", "moisture_sensor"]),
        ("лімаш рекомендовано агрономом", ["soil_lime", "soil_sampling_grid"]),
        ("заростання бур'янів у краплині", ["herbicide_band", "equipment_clean"]),
        ("прорідження густоти після сходів", ["seed_rate_review", "tillage_depth"]),
        ("брак калія жовтіє листя", ["potassium_autumn", "foliar_fertilizer"]),
        ("покривна культура після жнив", ["cover_crop_seed", "crop_rotation"]),
        ("затримка обприскування вітер 12 м/с", ["weather_hold", "rescout_7d"]),
        ("перелив від попереднього поля", ["equipment_clean", "buffer_zone_sign"]),
        ("фотофіксація плям у скаут-додатку", ["scouting_photos", "rescout_7d"]),
        ("дренаж не відводить воду", ["drainage_repair", "soil_sampling_grid"]),
        ("органіка компост перед посівом", ["organic_compost", "crop_rotation"]),
        ("смуговий фосфор при сівалці", ["phosphorus_band", "seed_rate_review"]),
        ("десикація перед збором сої", ["desiccation", "harvest_moisture"]),
        ("мертва зона біля водойми", ["buffer_zone_sign", "trap_crops"]),
        ("вітерозахист посадок лісосмуги", ["windbreak_check", "crop_rotation"]),
        ("калібрування датчиків поливу", ["moisture_sensor", "irrigation_pressure"]),
        ("ротація препаратів від резистентності", ["resistance_rotation", "spray_fungicide"]),
        ("вологість зерна на току 19%", ["harvest_moisture", "desiccation"]),
    ]
    test = []
    for j, (note, acceptable) in enumerate(test_notes):
        test.append(
            {
                "id": f"rec_test_{j + 1:03d}",
                "field_id": f"F-00{(j % 2) + 1}",
                "note": note,
                "acceptable_action_ids": acceptable,
            }
        )
    OUT_DEV.parent.mkdir(parents=True, exist_ok=True)
    OUT_DEV.write_text(json.dumps(dev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_TEST.write_text(json.dumps(test, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"dev={len(dev)} test={len(test)}")


if __name__ == "__main__":
    main()