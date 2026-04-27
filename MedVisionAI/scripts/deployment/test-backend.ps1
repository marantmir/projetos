#!/usr/bin/env pwsh

Write-Host "`n=========================" -ForegroundColor Cyan
Write-Host " Testando Backend Azure" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

$BackendUrl = "https://medvision-backend.livelycoast-50c79e76.brazilsouth.azurecontainerapps.io"

Write-Host "`nTestando endpoint: $BackendUrl/health" -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$BackendUrl/health" -Method Get -ErrorAction Stop
    
    Write-Host "`n[OK] Backend está respondendo!" -ForegroundColor Green
    Write-Host "`nResposta do Health Check:" -ForegroundColor White
    $response | ConvertTo-Json -Depth 5
    
    Write-Host "`nStatus:" -ForegroundColor White
    Write-Host "  - Status: $($response.status)" -ForegroundColor $(if ($response.status -eq "ok") { "Green" } else { "Red" })
    Write-Host "  - Version: $($response.version)" -ForegroundColor Cyan
    Write-Host "  - Environment: $($response.environment)" -ForegroundColor Cyan
    
    if ($response.services) {
        Write-Host "`nServicos:" -ForegroundColor White
        foreach ($service in $response.services.PSObject.Properties) {
            $statusColor = if ($service.Value) { "Green" } else { "Red" }
            $statusText = if ($service.Value) { "OK" } else { "ERRO" }
            Write-Host "  - $($service.Name): $statusText" -ForegroundColor $statusColor
        }
    }
    
} catch {
    Write-Host "`n[ERRO] Falha ao acessar o backend" -ForegroundColor Red
    Write-Host "Erro: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n=========================`n" -ForegroundColor Cyan
