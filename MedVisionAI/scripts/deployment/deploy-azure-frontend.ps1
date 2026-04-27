# =========================================
# Script de Deploy Frontend - Azure
# MedVision AI - Azure Static Web Apps
# =========================================

param(
    [string]$ResourceGroup = "medvision-rg",
    [string]$Location = "brazilsouth",
    [string]$AppName = "medvision-frontend",
    [Parameter(Mandatory=$true)]
    [string]$BackendUrl
)

Write-Host "🚀 MedVision AI - Deploy Frontend (Azure Static Web Apps)" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

function Log-Step {
    param($message)
    Write-Host "▶ $message" -ForegroundColor Yellow
}

function Log-Success {
    param($message)
    Write-Host "✓ $message" -ForegroundColor Green
}

function Log-Error {
    param($message)
    Write-Host "✗ $message" -ForegroundColor Red
}

# Verificar Azure CLI
try {
    az --version | Out-Null
    Log-Success "Azure CLI instalado"
} catch {
    Log-Error "Azure CLI não está instalado!"
    exit 1
}

# Verificar Node.js
try {
    node --version | Out-Null
    Log-Success "Node.js instalado"
} catch {
    Log-Error "Node.js não está instalado!"
    exit 1
}

# Criar arquivo .env.production
Log-Step "Configurando variáveis de ambiente..."
Push-Location frontend

$envContent = @"
VITE_API_URL=$BackendUrl
VITE_WS_URL=$($BackendUrl -replace 'https://', 'wss://')
"@

Set-Content -Path ".env.production" -Value $envContent
Log-Success "Arquivo .env.production criado"

# Instalar dependências
Log-Step "Instalando dependências do frontend..."
npm install
if ($LASTEXITCODE -ne 0) {
    Log-Error "Erro ao instalar dependências"
    Pop-Location
    exit 1
}
Log-Success "Dependências instaladas"

# Build do frontend
Log-Step "Building frontend para produção..."
npm run build
if ($LASTEXITCODE -ne 0) {
    Log-Error "Erro no build do frontend"
    Pop-Location
    exit 1
}
Log-Success "Build concluído"

Pop-Location

# Instalar extensão Static Web Apps
Log-Step "Preparando Static Web Apps..."
az extension add --name staticwebapp --upgrade --only-show-errors 2>&1 | Out-Null

# Criar Static Web App
Log-Step "Criando Static Web App..."
$appExists = az staticwebapp show --name $AppName --resource-group $ResourceGroup 2>&1

if ($LASTEXITCODE -ne 0) {
    # Criar novo
    Write-Host ""
    Write-Host "⚠️  ATENÇÃO: Azure Static Web Apps requer conexão com GitHub/GitLab" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Opções de deploy:" -ForegroundColor Cyan
    Write-Host "1. Via GitHub Actions (Recomendado)" -ForegroundColor White
    Write-Host "   - Crie repositório no GitHub" -ForegroundColor Gray
    Write-Host "   - Use Azure Portal: https://portal.azure.com → Static Web Apps" -ForegroundColor Gray
    Write-Host "   - Conecte ao repositório GitHub" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Via SWA CLI (Deploy manual dos arquivos)" -ForegroundColor White
    Write-Host "   - npm install -g @azure/static-web-apps-cli" -ForegroundColor Gray
    Write-Host "   - swa deploy ./frontend/dist --env production" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Via Azure App Service (Alternativa)" -ForegroundColor White
    Write-Host "   - Execute: .\deploy-azure-appservice.ps1" -ForegroundColor Gray
    Write-Host ""
    
    # Opção: criar via CLI (sem GitHub)
    $response = Read-Host "Deseja criar Static Web App via Portal Azure agora? (s/n)"
    if ($response -eq 's') {
        Start-Process "https://portal.azure.com/#create/Microsoft.StaticApp"
        Write-Host "Portal Azure aberto. Configure:" -ForegroundColor Yellow
        Write-Host "  - Resource Group: $ResourceGroup" -ForegroundColor White
        Write-Host "  - Name: $AppName" -ForegroundColor White
        Write-Host "  - Region: $Location" -ForegroundColor White
        Write-Host "  - Build Presets: React" -ForegroundColor White
        Write-Host "  - App location: /frontend" -ForegroundColor White
        Write-Host "  - Output location: /dist" -ForegroundColor White
    }
} else {
    Log-Success "Static Web App já existe"
    # Aqui poderia fazer update se necessário
}

Write-Host ""
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "✅ Build do frontend concluído!" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📦 Arquivos estáticos gerados em: ./frontend/dist" -ForegroundColor White
Write-Host "🔗 Backend URL configurada: $BackendUrl" -ForegroundColor White
Write-Host ""
Write-Host "📋 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. Commitee e push seu código para GitHub" -ForegroundColor White
Write-Host "2. Crie Static Web App via Portal Azure" -ForegroundColor White
Write-Host "3. Conecte ao seu repositório GitHub" -ForegroundColor White
Write-Host "   OU" -ForegroundColor Yellow
Write-Host "4. Use Azure App Service para hospedar os arquivos estáticos" -ForegroundColor White
Write-Host "   Execute: .\deploy-azure-appservice.ps1" -ForegroundColor Gray
Write-Host ""
