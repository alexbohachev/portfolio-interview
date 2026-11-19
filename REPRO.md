# Reproducibility

## Clean clone (Windows)

```powershell
git clone https://github.com/alexbohachev/portfolio-interview.git
cd portfolio-interview
.\scripts\repro_check.ps1
```

With Docker (Work 05 + 07):

```powershell
.\scripts\repro_check.ps1 -Docker
```

## What must pass

| Step | Command | Exit code |
|------|---------|-----------|
| Offline demos | `.\scripts\prep_interview.ps1` | 0 |
| Smoke + work05 (Docker up) | `.\scripts\prep_interview.ps1 -Strict` | 0 |
| Strict smoke only | `.\scripts\portfolio_smoke.ps1 -Strict` | 0 |
| Work 07 platform | `cd work07-ai-platform; .\make.ps1 finalize` | 0 |
| Work 05 ACL | `cd work05-docguard; .\gradlew.bat test` | 0 |

## CI

| Workflow | What it checks |
|----------|----------------|
| [`repro.yml`](.github/workflows/repro.yml) | `repro_check` (offline) on Windows |
| [`portfolio-prep.yml`](.github/workflows/portfolio-prep.yml) | offline demos 01, 03, 07 |
| `work05.yml` / `work07.yml` | unit/build; Docker smoke on `repro-docker` job |

Last known green runs: see [GitHub Actions](https://github.com/alexbohachev/portfolio-interview/actions).

## Root path fix

Scripts under `scripts/` resolve repo root via [`Get-RepoRoot.ps1`](scripts/Get-RepoRoot.ps1) (parent of `scripts/`, not `scripts/` itself).