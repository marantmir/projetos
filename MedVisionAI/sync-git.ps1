#!/usr/bin/env pwsh
# Script para sincronizar Git automaticamente

$ErrorActionPreference = "Continue"
cd C:\dev\TechChallengeF04\medvision-ai

Write-Host "=== Limpando estado Git ===" -ForegroundColor Cyan

# Configurar editor não-interativo
git config --global core.editor "true"
$env:GIT_EDITOR = "true"
$env:EDITOR = "true"

# Limpar qualquer operação pendente
git merge --abort 2>$null
git rebase --abort 2>$null
git cherry-pick --abort 2>$null

# Remover arquivos de estado de merge
Remove-Item .git\MERGE_HEAD -Force -ErrorAction SilentlyContinue
Remove-Item .git\MERGE_MODE -Force -ErrorAction SilentlyContinue
Remove-Item .git\MERGE_MSG -Force -ErrorAction SilentlyContinue
Remove-Item .git\ORIG_HEAD -Force -ErrorAction SilentlyContinue

Write-Host "`n=== Verificando status ===" -ForegroundColor Cyan
git status --short

Write-Host "`n=== Sincronizando com remoto ===" -ForegroundColor Cyan
git fetch origin main
git pull origin main --no-edit --strategy=ours 2>&1 | Out-String

Write-Host "`n=== Fazendo push ===" -ForegroundColor Cyan
$pushResult = git push origin main 2>&1 | Out-String
Write-Host $pushResult

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Push realizado com sucesso!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️ Erro no push. Saída:" -ForegroundColor Yellow
    Write-Host $pushResult
}

Write-Host "`n=== Últimos commits ===" -ForegroundColor Cyan
git log --oneline -3

Write-Host "`nPressione Enter para fechar..."
Read-Host
