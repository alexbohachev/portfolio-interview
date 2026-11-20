[**Українська**](DEMO.md) | [English](DEMO.en.md)

# Демо work01 (2–4 хв, offline)

## Підготовка

```powershell
cd c:\Portfolio\work01-bank-marketing
py -3.13 -m pip install -r requirements.txt
.\make.ps1 all
.\scripts\demo.ps1
```

## Сценарій

1. **Дані:** UCI Bank Marketing, **без `duration`** (leakage).
2. **Часовий split** + bootstrap CI різниці macro-F1.
3. **Baseline LR** vs **candidate MLP** + temperature scaling.
4. Показати `REPORT.md` — test метрики та ablation порогу 0.5.

## Повідомлення для інтерв'ю

«Кандидат не перемагає baseline на test — і це задокументовано; важливі стабільність, ablation і чесний звіт».