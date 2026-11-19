# Спільний корінь monorepo (батьківська папка для scripts/).
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