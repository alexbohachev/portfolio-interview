[**Українська**](REPORT.md) | [English](REPORT.en.md)

# Звіт — робота 1: навчання й оцінювання моделей

## Задача
Бінарна класифікація підписки на депозит (UCI Bank Marketing, `bank-full.csv`), ознака `duration` виключена.

## Дані
- SHA-256 `bank-full.csv`: `d1513ec63b385506f7cfce9f2c5caa9fe99e7ba4e8c3fa264b3aaf0f849ed32d`
- Test: 6782 прикладів (фіксований часовий split, `manifests/test_manifest.json`)
- Частка `yes`: train 0.0581, val 0.1152, test 0.3934 (часовий shift)

## Метод
- **Baseline:** логістична регресія (`class_weight=balanced`), поріг macro-F1 на validation
- **Candidate:** MLP + early stopping (val macro-F1), temperature scaling на validation, вибір seed 44 за val macro-F1
- **Ablation:** candidate з фіксованим порогом 0.5 (без підбору) — для порівняння

## Результати (test, один прогон)

| Метрика | Baseline | Candidate |
|---------|----------|-----------|
| macro-F1 | 0.5379 | 0.5377 |
| Brier | 0.2599 | 0.2683 |
| PR-AUC | 0.4969 | 0.4807 |

Пороги (підібрані на val): baseline=0.73, candidate=0.69.

### Ablation: candidate, поріг 0.5
- macro-F1=0.5793, Brier=0.2683, PR-AUC=0.4807

## Нестабільність навчання (5 seed, **validation** macro-F1)

- значення: [0.5946, 0.6048, 0.5976, 0.6068, 0.602]
- std: 0.0045

## Bootstrap різниці macro-F1 (candidate − baseline, test, фіксовані пороги)

- Точка: -0.0002
- 95% CI: [-0.0085, 0.0089]

## Аналіз помилок (candidate)

- Помилок на test: 2628 / 6782 (38.8%)

**Групи (усі помилки на test):**

- FN_borderline_high: 899
- FN_mid_score: 645
- FP_high_confidence: 551
- FN_low_score: 411
- FP_borderline: 122

**Розібрані приклади (до 20):**

- рядок 40397: true=yes, pred=no, p=0.450, FN_borderline_high, age=37, month=jul
- рядок 40069: true=yes, pred=no, p=0.250, FN_mid_score, age=39, month=jun
- рядок 43366: true=no, pred=yes, p=0.985, FP_high_confidence, age=82, month=mar
- рядок 44090: true=yes, pred=no, p=0.001, FN_low_score, age=37, month=jul
- рядок 43456: true=no, pred=yes, p=0.748, FP_borderline, age=56, month=apr
- рядок 42740: true=yes, pred=no, p=0.450, FN_borderline_high, age=42, month=jan
- рядок 42482: true=yes, pred=no, p=0.251, FN_mid_score, age=72, month=dec
- рядок 42075: true=no, pred=yes, p=0.984, FP_high_confidence, age=84, month=oct
- рядок 44531: true=yes, pred=no, p=0.001, FN_low_score, age=34, month=aug
- рядок 44544: true=no, pred=yes, p=0.748, FP_borderline, age=27, month=aug
- рядок 42723: true=yes, pred=no, p=0.451, FN_borderline_high, age=63, month=jan
- рядок 44080: true=yes, pred=no, p=0.252, FN_mid_score, age=30, month=jul
- рядок 45048: true=no, pred=yes, p=0.982, FP_high_confidence, age=69, month=oct
- рядок 44859: true=yes, pred=no, p=0.002, FN_low_score, age=31, month=sep
- рядок 40852: true=no, pred=yes, p=0.748, FP_borderline, age=71, month=aug
- рядок 44057: true=yes, pred=no, p=0.451, FN_borderline_high, age=32, month=jul
- рядок 43734: true=yes, pred=no, p=0.253, FN_mid_score, age=27, month=may
- рядок 42027: true=no, pred=yes, p=0.982, FP_high_confidence, age=74, month=oct
- рядок 44490: true=yes, pred=no, p=0.003, FN_low_score, age=31, month=aug
- рядок 42977: true=no, pred=yes, p=0.748, FP_borderline, age=38, month=feb

### Висновки з помилок
1. **Часовий shift** — test має набагато вищу частку `yes`; поріг з val часто завищений для test.
2. **FN_borderline** — модель недооцінює `yes` у новішому періоді (кампанії/сезонність `month`).
3. **FP_high_confidence** — рідкісні перепідтвердження `yes` при фактичному `no` після калібрування.

## Обмеження
- Один фінальний прогон test; пороги зафіксовані з validation.
- Temperature scaling не компенсує повністю covariate shift між val і test.
- MLP без явних cross-фіч; логістична регресія сильна на табличних даних.

## Наступний крок
- Часовий re-fit / окремий калібратор на останньому вікні; або модель із явною `month`/кампанійною ознакою часу.

_Автогенерація; час `make all`: ~50.34 с._
