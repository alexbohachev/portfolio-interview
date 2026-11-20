[Українська](DATA.md) | **English**

# Data — work 1

| Field | Value |
|------|----------|
| Dataset | UCI Bank Marketing |
| File | `bank-full.csv` in `bank.zip` |
| License | CC BY 4.0 |
| Delimiter | `;` |
| Rows | 45 211 (header not counted, per the task spec) |
| SHA-256 `bank-full.csv` | `d1513ec63b385506f7cfce9f2c5caa9fe99e7ba4e8c3fa264b3aaf0f849ed32d` |
| Target | `y` → binary (`yes` = 1) |
| Excluded | `duration` (known only after the call) |

## Split (sequential, as in the file)

| Part | Rows (1-based) | Count |
|---------|-------------------|-----------|
| train | 1–31 647 | 31 647 |
| validation | 31 648–38 429 | 6 782 |
| test | 38 430–45 211 | 6 782 |

Download: `py -3 -m work01 data` or the full cycle `.\make.ps1 all`.
