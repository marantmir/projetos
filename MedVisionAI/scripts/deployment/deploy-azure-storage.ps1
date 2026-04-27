# =========================================
# Deploy Frontend - Azure Storage (Simples)
# MedVision AI - Hospedagem Estática
# =========================================

param(
    [string]$ResourceGroup = "medvision-rg",
    [string]$Location = "brazilsouth",
    [string]$StorageAccountName = "medvisionfrontend",
    [Parameter(Mandatory=$true)]
    [string]$BackendUrl
)

Write-Host "MedVision AI - Deploy Frontend (Azure Storage)" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

function Log-Step {
    param($message)
    Write-Host ">> $message" -ForegroundColor Yellow
}

function Log-Success {
    param($message)
    Write-Host "[OK] $message" -ForegroundColor Green
}

function Log-Error {
    param($message)
    Write-Host "[ERRO] $message" -ForegroundColor Red
}

# Verificar Azure CLI
try {
    az --version | Out-Null
} catch {
    Log-Error "Azure CLI não está instalado!"
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
Log-Success ".env.production configurado"

# Build
Log-Step "Building frontend..."
npm install
npm run build
if ($LASTEXITCODE -ne 0) {
    Log-Error "Erro no build"
    Pop-Location
    exit 1
}
Log-Success "Build concluído"

Pop-Location

# Criar Storage Account
Log-Step "Criando Storage Account: $StorageAccountName"
$saExists = az storage account show --name $StorageAccountName --resource-group $ResourceGroup 2>&1

if ($LASTEXITCODE -ne 0) {
    az storage account create `
        --name $StorageAccountName `
        --resource-group $ResourceGroup `
        --location $Location `
        --sku Standard_LRS `
        --kind StorageV2 `
        --allow-blob-public-access true `
        --output none
    
    if ($LASTEXITCODE -eq 0) {
        Log-Success "Storage Account criado"
    } else {
        Log-Error "Erro ao criar Storage Account"
        exit 1
    }
} else {
    Log-Success "Storage Account já existe"
}

# Habilitar static website
Log-Step "Habilitando hospedagem estática..."
az storage blob service-properties update `
    --account-name $StorageAccountName `
    --static-website `
    --index-document index.html `
    --404-document index.html `
    --output none

Log-Success "Hospedagem estática habilitada"

# Upload dos arquivos
Log-Step "Fazendo upload dos arquivos..."
az storage blob upload-batch `
    --account-name $StorageAccountName `
    --source ./frontend/dist `
    --destination '$web' `
    --overwrite `
    --output none

if ($LASTEXITCODE -eq 0) {
    Log-Success "Arquivos enviados"
} else {
    Log-Error "Erro ao enviar arquivos"
    exit 1
}

# Obter URL do site
$websiteUrl = az storage account show `
    --name $StorageAccountName `
    --resource-group $ResourceGroup `
    --query "primaryEndpoints.web" `
    -o tsv

Write-Host ""
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "[SUCESSO] Frontend implantado com sucesso!" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend URL: $websiteUrl" -ForegroundColor White
Write-Host "Backend URL: $BackendUrl" -ForegroundColor White
Write-Host ""
Write-Host "IMPORTANTE: Configure CORS no backend" -ForegroundColor Yellow
Write-Host "   Adicione esta URL nas variáveis de ambiente do backend:" -ForegroundColor Gray
Write-Host "   CORS_ORIGINS=[`"$websiteUrl`",`"http://localhost:5173`"]" -ForegroundColor White
Write-Host ""
Write-Host "   Execute:" -ForegroundColor Yellow
Write-Host "   az containerapp update --name medvision-backend --resource-group $ResourceGroup --set-env-vars `"CORS_ORIGINS=['$websiteUrl','http://localhost:5173']`"" -ForegroundColor Gray
Write-Host ""
Write-Host "Para domínio customizado, configure Azure CDN:" -ForegroundColor Cyan
Write-Host "   https://docs.microsoft.com/azure/storage/blobs/static-website-content-delivery-network" -ForegroundColor Gray
Write-Host ""
