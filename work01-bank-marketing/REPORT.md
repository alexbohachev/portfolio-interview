# Звіт — робота 1: навчання й оцінювання моделей

## Задача
Бінарна класифікація підписки на депозит (UCI Bank Marketing, `bank-full.csv`), ознака `duration` виключена.

## Дані
- SHA-256 архіву: `99d7e8eb12401ed278b793984423915411ea8df099e1795f9fefe254f513fe5e`
- Test: 6782 прикладів (фіксований часовий split, див. `manifests/test_manifest.json`)

## Методи
- **Baseline:** логістична регресія (sklearn Pipeline + OneHotEncoder)
- **Candidate:** MLP у PyTorch, early stopping за val loss, 5 seed для оцінки нестабільності

## Результати (test, один прогон candidate — останній seed)

| Метрика | Baseline | Candidate |
|---------|----------|-----------|
| macro-F1 | 0.5989 | 0.5312 |
| Brier | 0.2599 | 0.2854 |
| PR-AUC | 0.4969 | 0.4735 |

## Нестабільність навчання (5 seed, test)

- macro-F1: 0.5440 ± 0.0119
- Brier: 0.2715 ± 0.0082
- PR-AUC: 0.4848 ± 0.0101

## Bootstrap різниці macro-F1 (candidate − baseline, test)

- Точка: -0.0675
- 95% CI: [-0.0791, -0.0563]

## Обмеження
- Часовий shift частки `yes` між train/val/test; поріг 0.5 не оптимізувався на test.
- Один фінальний candidate checkpoint (останній seed); ablation не виконувались.

## Наступний крок
- Підбір порогу за validation (ціна FP/FN) і калібрування ймовірностей.

_Згенеровано автоматично; час виконання `make all`: ~25.12 с._
