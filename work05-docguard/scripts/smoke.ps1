param(
    [string]$Gateway = "http://localhost:8096",
    [string]$Retrieval = "http://localhost:8097"
)
$ErrorActionPreference = "Stop"

function Wait-Http([string]$Url, [int]$MaxSec = 90) {
    $deadline = (Get-Date).AddSeconds($MaxSec)
    while ((Get-Date) -lt $deadline) {
        try {
            Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec 3 | Out-Null
            return
        } catch {
            Start-Sleep -Seconds 2
        }
    }
    throw "timeout waiting for $Url"
}

Wait-Http "$Retrieval/health"
$health = Invoke-RestMethod -Uri "$Retrieval/health" -Method Get
if ($health.docs -lt 10) {
    throw "corpus not mounted (docs=$($health.docs))"
}

Wait-Http "$Gateway/health"
$headers = @{
    "X-Tenant-Id"    = "tenant_a"
    "X-Principal-Id" = "alice"
}
$body = @{ question = "бура іржа пшениця" } | ConvertTo-Json -Compress
$res = Invoke-RestMethod -Uri "$Gateway/api/v1/query" -Method Post -Headers $headers `
    -ContentType "application/json; charset=utf-8" -Body ([System.Text.Encoding]::UTF8.GetBytes($body))
if (-not $res.hits -or $res.hits.Count -lt 1) {
    throw "expected hits from live retrieval"
}
Write-Host "OK smoke hits=$($res.hits.Count) doc_id=$($res.hits[0].doc_id)"