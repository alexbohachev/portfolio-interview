# Демонстраційні виклики для запису відео (читабельний вивід)
$ErrorActionPreference = "Stop"
$rag = "http://localhost:8090"
$log = "http://localhost:8084"
$scout = "http://localhost:8082"

function Show($title, $json) {
    Write-Host "`n=== $title ===" -ForegroundColor Cyan
    $json | ConvertTo-Json -Depth 6
}

$h = Invoke-RestMethod "$rag/health"
Show "rag-api health" $h

$search = Invoke-RestMethod "$rag/v1/knowledge/search" -Method Post -ContentType "application/json" `
    -Body '{"query":"бура іржа озимої пшениці","topK":3,"mode":"hybrid"}'
Show "hybrid search" $search

$qa = Invoke-RestMethod "$log/api/v1/knowledge/qa" -Method Post -ContentType "application/json" `
    -Body '{"question":"Який фактор важливий для хвороб пшениці?"}'
Show "Q&A via logistics" $qa

$obs = Invoke-RestMethod "$scout/api/v1/observations" -Method Post -ContentType "application/json" `
    -Body '{"fieldId":"F-001","note":"плями на листі"}'
Show "scout observation" $obs

$ref = Invoke-RestMethod "$log/api/v1/knowledge/qa" -Method Post -ContentType "application/json" `
    -Body '{"question":"Посіви на Марсі у 2040?"}'
Show "refusal example" $ref

Write-Host "`nГотово для запису. Детальніше: DEMO.md" -ForegroundColor Green