# =========================================
# Deploy Frontend - Azure Container Apps
# MedVision AI - Frontend como Container
# =========================================

param(
    [string]$ResourceGroup = "medvision-rg",
    [string]$Location = "brazilsouth",
    [string]$FrontendAppName = "medvision-frontend",
    [string]$AcrName = "medvisionacr",
    [string]$Environment = "medvision-env",
    [Parameter(Mandatory=$true)]
    [string]$BackendUrl
)

Write-Host "MedVision AI - Deploy Frontend (Container Apps)" -ForegroundColor Cyan
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
Log-Step "Verificando Azure CLI..."
try {
    az --version | Out-Null
    Log-Success "Azure CLI encontrado"
} catch {
    Log-Error "Azure CLI não instalado"
    exit 1
}

# Configurar .env.production
Log-Step "Configurando variáveis de ambiente..."
Push-Location frontend

$envContent = @"
VITE_API_URL=$BackendUrl
VITE_WS_URL=$($BackendUrl -replace 'https://', 'wss://')
"@

Set-Content -Path ".env.production" -Value $envContent
Log-Success ".env.production configurado"

# Build do frontend
Log-Step "Building frontend..."
npm install --silent
npm run build
if ($LASTEXITCODE -ne 0) {
    Log-Error "Erro no build do frontend"
    Pop-Location
    exit 1
}
Log-Success "Build concluído"

Pop-Location

# Login no ACR
Log-Step "Fazendo login no Azure Container Registry..."
az acr login --name $AcrName --output none
if ($LASTEXITCODE -ne 0) {
    Log-Error "Erro ao fazer login no ACR"
    exit 1
}
Log-Success "Login no ACR realizado"

# Build da imagem Docker
Log-Step "Construindo imagem Docker do frontend..."
$imageName = "$AcrName.azurecr.io/$FrontendAppName:latest"

docker build -t $imageName -f frontend/Dockerfile frontend/
if ($LASTEXITCODE -ne 0) {
    Log-Error "Erro ao construir imagem"
    exit 1
}
Log-Success "Imagem construída"

# Push da imagem
Log-Step "Enviando imagem para ACR..."
docker push $imageName
if ($LASTEXITCODE -ne 0) {
    Log-Error "Erro ao enviar imagem"
    exit 1
}
Log-Success "Imagem enviada para ACR"

# Deploy do Container App
Log-Step "Fazendo deploy do Container App..."

$appExists = az containerapp show --name $FrontendAppName --resource-group $ResourceGroup 2>&1

if ($LASTEXITCODE -ne 0) {
    # Criar novo
    Log-Step "Criando novo Container App..."
    
    # Obter credenciais do ACR
    $acrPassword = az acr credential show --name $AcrName --query "passwords[0].value" -o tsv
    
    az containerapp create `
        --name $FrontendAppName `
        --resource-group $ResourceGroup `
        --environment $Environment `
        --image $imageName `
        --registry-server "$AcrName.azurecr.io" `
        --registry-username $AcrName `
        --registry-password $acrPassword `
        --target-port 80 `
        --ingress 'external' `
        --min-replicas 1 `
        --max-replicas 3 `
        --cpu 0.5 `
        --memory 1.0Gi `
        --output none
} else {
    # Atualizar existente
    Log-Step "Atualizando Container App existente..."
    az containerapp update `
        --name $FrontendAppName `
        --resource-group $ResourceGroup `
        --image $imageName `
        --output none
}

if ($LASTEXITCODE -eq 0) {
    Log-Success "Container App implantado"
} else {
    Log-Error "Erro ao implantar Container App"
    exit 1
}

# Obter URL
Log-Step "Obtendo URL da aplicação..."
$frontendUrl = az containerapp show `
    --name $FrontendAppName `
    --resource-group $ResourceGroup `
    --query "properties.configuration.ingress.fqdn" `
    -o tsv

$frontendUrl = "https://$frontendUrl"

Write-Host ""
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "[SUCESSO] Frontend implantado!" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend URL: $frontendUrl" -ForegroundColor White
Write-Host "Backend URL: $BackendUrl" -ForegroundColor White
Write-Host ""
Write-Host "IMPORTANTE: Configure CORS no backend" -ForegroundColor Yellow
Write-Host "   Execute:" -ForegroundColor Gray
Write-Host ""
Write-Host "   az containerapp update --name medvision-backend --resource-group $ResourceGroup --set-env-vars `"CORS_ORIGINS=['$frontendUrl','http://localhost:5173']`"" -ForegroundColor White
Write-Host ""
Write-Host "Testando aplicação:" -ForegroundColor Cyan
Write-Host "   1. Acesse: $frontendUrl" -ForegroundColor White
Write-Host "   2. Faça upload de um vídeo cirúrgico" -ForegroundColor White
Write-Host "   3. Verifique análise YOLOv8 + Gemini AI" -ForegroundColor White
Write-Host ""
