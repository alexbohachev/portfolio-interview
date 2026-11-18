"""200 synthetic agri markdown docs (MVP; замінити відкритими джерелами — DATA.md)."""
from pathlib import Path

TOPICS = [
    ("wheat_disease", "Хвороби пшениці", "бура іржа", "септоріоз", "фузаріоз"),
    ("corn_irrigation", "Зрошення кукурудзи", "краплинне", "вологоємність грунту", "борознева"),
    ("soil_ph", "Кислотність грунту", "вапнування", "pH 6.0", "лімаш"),
    ("npk_fertilizer", "Мінеральні добрива NPK", "азот", "фосфор", "калій"),
    ("organic_matter", "Гумус", "сігальні культури", "компост", "органіка"),
    ("pest_ipm", "ІПМ шкідники", "трихограма", "феромони", "економічний поріг"),
    ("herbicide", "Гербіциди", "гліфосат", "2,4-D", "добірка"),
    ("seed_rate", "Норма висіву", "щільність", "гібрид", "проростки"),
    ("crop_rotation", "Сівозміна", "пар", "бобові", "фітосанітарія"),
    ("sunflower", "Соняшник", "олійність", "байрачний", "висота рослин"),
]

ROOT = Path(__file__).resolve().parents[1] / "corpus" / "bundled"
VARIANTS = 20


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    for old in ROOT.glob("*.md"):
        old.unlink()
    idx = 0
    for key, title, *facts in TOPICS:
        for variant in range(VARIANTS):
            idx += 1
            doc_id = f"agri_{idx:03d}_{key}_{variant}"
            season = 2016 + (variant % 9)
            fact = facts[variant % len(facts)]
            body = (
                f"# {title} ({variant + 1})\n\n"
                f"Документ {doc_id}. Ліцензія: синтетичний текст портфоліо (CC0).\n\n"
                f"Ключові факти: {', '.join(facts)}.\n\n"
                f"## Практика\n"
                f"Для {title.lower()} критичний фактор «{fact}» у сезоні {season}.\n\n"
                f"## Цитований фрагмент\n"
                f"Унікальне речення для пошуку {doc_id}: «{fact} впливає на урожай у сезоні {season}».\n"
            )
            (ROOT / f"{doc_id}.md").write_text(body, encoding="utf-8")
    print(f"wrote {idx} docs to {ROOT}")


if __name__ == "__main__":
    main()