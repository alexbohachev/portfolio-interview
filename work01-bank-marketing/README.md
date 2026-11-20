[**Українська**](README.md) | [English](README.en.md)

# Робота 1 — навчання й оцінювання моделей

**Одне речення:** на UCI Bank Marketing (без `duration`) логістична регресія та MLP з калібруванням дають **macro-F1 ≈ 0.538** на test; різниця всередині bootstrap CI **[−0.0085; 0.0089]** (candidate не кращий за baseline).

## Результати (test, пороги з validation)

| Метрика | Baseline | Candidate |
|---------|----------|-----------|
| macro-F1 | 0.5379 | 0.5377 |
| Brier | 0.2599 | 0.2683 |
| PR-AUC | 0.4969 | 0.4807 |

Пороги: baseline **0.73**, candidate **0.69** (macro-F1 на val). Частка `yes`: train 5.8% → val 11.5% → **test 39.3%**.

```text
[train 5.8% yes] → [val 11.5%] → threshold tuning → [test 39.3% yes] → сильний covariate shift
```

## Схема рішення

```text
bank-full.csv ──► часовий split ──► OneHot+Scaler
                        ├─► LogReg (baseline) ──► поріг на val ──► test
                        └─► MLP (5 seed) ──► best seed на val ──► temperature scale ──► поріг на val ──► test
```

## Три головні причини помилок (candidate)

| # | Причина | Що зроблено |
|---|---------|-------------|
| 1 | Часовий shift частки `yes` (5.8% → 39.3%) | Поріг лише з val; у звіті — негативний результат, без підбору на test |
| 2 | Масовий **FN** у пізніх `month` (низькі p при true=yes) | Групування в `artifacts/error_cases.json`, 20 розібраних рядків у `REPORT.md` |
| 3 | Табличні дані — логістична регресія сильна; MLP не дає виграшу | Фіксовано seed 44 за val; bootstrap показує ефект ≈ 0 |

## Запуск

```powershell
py -3.13 -m pip install -r requirements.txt
py -3.13 -m work01 lock    # після зміни config, перед фінальним test
.\make.ps1 all             # ~50–60 с на CPU
```

| Команда | Дія |
|---------|-----|
| `.\make.ps1 data` | Завантаження + SHA-256 |
| `.\make.ps1 test` | pytest (offline) |

Повний звіт: [`REPORT.md`](REPORT.md). Дані: [`DATA.md`](DATA.md). Test manifest: [`manifests/test_manifest.json`](manifests/test_manifest.json).

## Критерії готовності (ТЗ)

- [x] `make all` / `make.ps1 all` на чистій машині (після `pip install`)
- [x] manifest + config_hash **до** test (`work01 lock`)
- [x] baseline + candidate + ablation (поріг 0.5)
- [x] 5 seed — std на **validation**
- [x] bootstrap різниці macro-F1 на test
- [x] аналіз помилок (≤20 кейсів)
- [ ] git-tag `work01-v1.0` після вашої рецензії звіту
- [ ] відрепетирувати 2-хв розповідь + 3 питання з таблиці ТЗ

## Співбесідні підказки

- **Чому CI перетинає нуль?** — ефект candidate статистично не відмінний від baseline при фіксованих порогах.
- **Чому ablation 0.5 має вищий F1 на test?** — поріг з val не переноситься при shift; **не** використовували test для вибору порога.
- **Seed vs bootstrap:** seed-розкид на val (~0.0045 std); bootstrap — похибка на test.

## Git-tag

```bash
git tag -a work01-v1.0 -m "Робота 1: Bank Marketing, baseline vs MLP, REPORT.md"
```