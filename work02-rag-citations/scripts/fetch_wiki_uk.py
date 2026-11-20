"""Fetch a real Ukrainian agronomy corpus from uk.wikipedia.org (CC BY-SA 4.0).

Each article is saved as corpus/wiki_uk/<slug>.md with the page title, URL, revision id and license, so the
corpus is attributable and reproducible. Only the lead + first sections (plain text, <= MAX_CHARS) are kept.

Usage: python scripts/fetch_wiki_uk.py
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "corpus" / "wiki_uk"
API = "https://uk.wikipedia.org/w/api.php"
MAX_CHARS = 3500
UA = "portfolio-rag-eval/1.0 (educational; contact via GitHub repo)"

TITLES = """Пшениця|Кукурудза|Соняшник|Ячмінь|Жито|Овес|Соя|Ріпак|Цукровий буряк|Картопля|Гречка|Горох|Просо|Рис посівний|Льон|Люцерна|Конюшина|Тритикале|Сорго|Нут
Іржа злаків|Борошниста роса|Фузаріоз|Септоріоз|Сажка|Ріжки|Кореневі гнилі|Фітофтороз|Пероноспороз|Склеротинія|Вірусні хвороби рослин|Бактеріальні хвороби рослин
Колорадський жук|Попелиці|Лучний метелик|Бавовникова совка|Шкідники сільськогосподарських культур|Дротяники|Довгоносики|Хлібні жуки|Хрестоцвіті блішки|Совки
Гербіциди|Фунгіциди|Інсектициди|Пестициди|Протруйник|Бур'ян|Інтегрований захист рослин|Біологічний захист рослин
Ґрунт|Чорнозем|Кислотність ґрунту|Гумус|Ерозія ґрунту|Засолення ґрунтів|Структура ґрунту|Ґрунтознавство|Родючість ґрунту|Мікроорганізми ґрунту|Каштанові ґрунти|Сірі лісові ґрунти|Деградація ґрунтів
Мінеральні добрива|Органічні добрива|Азотні добрива|Фосфорні добрива|Калійні добрива|Аміачна селітра|Сечовина|Суперфосфат|Гній|Сидерат|Компост|Мікродобрива|Азот|Фосфор|Калій
Зрошення|Краплинне зрошення|Дощування|Меліорація|Осушення земель|Посуха|Водний баланс ґрунту|Транспірація|Евапотранспірація
Сівозміна|Парова система землеробства|Обробіток ґрунту|Безполицевий обробіток ґрунту|Нульовий обробіток ґрунту|Оранка|Боронування|Культивація|Мульчування|Мінімальний обробіток ґрунту|Сорт|Гібрид|Насіння|Сівба|Норма висіву|Схожість насіння|Яровизація|Фенологія
Комбайн|Трактор|Сівалка|Оприскувач|Плуг|Культиватор|Зернозбиральний комбайн|Точне землеробство|Дрон|Супутникове землеробство|Агрохолдинг|Фермерське господарство
Урожайність|Врожай|Жнива|Зберігання зерна|Елеватор|Зерно|Борошно|Хліборобство|Агрономія|Землеробство|Рослинництво|Агрохімія|Селекція рослин|Біотехнологія рослин
Фотосинтез|Вегетація|Кореневе живлення|Хлороз|Опадання листя|Ріст і розвиток рослин|Заморозки|Град|Кліматичні зміни|Агрометеорологія|Мікроклімат
Органічне землеробство|Агроекологія|Сталий розвиток сільського господарства|ГМО|Генетично модифіковані організми|Пасовище|Сінокіс|Силос|Кормові культури|Виноград|Яблуня|Томат|Огірок|Цибуля|Морква|Капуста""".replace("\n", "|").split("|")


def api(params: dict) -> dict:
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(float(e.headers.get("Retry-After", 5)) + 2 * attempt)
    raise RuntimeError("rate limited too many times")


def slugify(i: int, title: str) -> str:
    base = re.sub(r"[^\w]+", "_", title.lower(), flags=re.UNICODE).strip("_")
    return f"wiki_{i:03d}_{base}"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    titles = list(dict.fromkeys(t.strip() for t in TITLES if t.strip()))
    kept, missing = 0, []
    for i, title in enumerate(titles, 1):
        if any(OUT.glob(f"wiki_{i:03d}_*.md")):
            kept += 1
            continue
        data = api({
            "action": "query", "prop": "extracts|info", "explaintext": 1, "redirects": 1,
            "titles": title, "format": "json", "formatversion": 2, "inprop": "url",
        })
        page = data["query"]["pages"][0]
        text = (page.get("extract") or "").strip()
        if page.get("missing") or len(text) < 300:
            missing.append(title)
            continue
        text = re.sub(r"\n== .*? ==\n", "\n", text)  # drop section markers, keep the prose
        text = text[:MAX_CHARS].rsplit("\n", 1)[0] if len(text) > MAX_CHARS else text
        rev = page.get("lastrevid")
        slug = slugify(i, page["title"])
        (OUT / f"{slug}.md").write_text(
            f"# {page['title']}\n\nДжерело: {page['fullurl']} (ревізія {rev}). "
            f"Ліцензія: CC BY-SA 4.0, автори — спільнота Вікіпедії.\n\n{text}\n",
            encoding="utf-8",
        )
        kept += 1
        time.sleep(1.0)
    print(f"kept {kept} articles; missing/too short ({len(missing)}): {', '.join(missing)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
