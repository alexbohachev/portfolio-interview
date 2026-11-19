# Спільний корінь monorepo (батьківська папка для scripts/).
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

if (-not (Get-Command py -ErrorAction SilentlyContinue) -and (Get-Command python -ErrorAction SilentlyContinue)) {
    function global:py {
        $cleanArgs = @($args | Where-Object { $_ -notmatch '^-\d+(\.\d+)?$' })
        & python @cleanArgs
    }
}

function Get-RepoRoot {
    if ($PSScriptRoot) {
        return (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
    }
    $here = Split-Path -Parent $MyInvocation.ScriptName
    if ($here) {
        return (Resolve-Path (Join-Path $here "..")).Path
    }
    throw "Cannot resolve repo root"
}