# =========================================
# Script de Deploy Automatizado - Azure
# MedVision AI - Azure Container Apps
# =========================================

param(
    [string]$ResourceGroup = "medvision-rg",
    [string]$Location = "brazilsouth",
    [string]$AcrName = "medvisionacr",
    [string]$BackendAppName = "medvision-backend",
    [string]$EnvironmentName = "medvision-env",
    [string]$GeminiApiKey = $env:GEMINI_API_KEY
)

Write-Host "MedVision AI - Deploy no Azure Container Apps" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Funcao de log
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

# Verificar se Azure CLI está instalado
try {
    $azVersion = az --version 2>&1 | Select-Object -First 1
    Log-Success "Azure CLI instalado"
} catch {
    Log-Error "Azure CLI não está instalado!"
    Write-Host "Instale via: https://aka.ms/installazurecliwindows" -ForegroundColor Yellow
    exit 1
}

# Verificar se está logado
Log-Step "Verificando login no Azure..."
$account = az account show 2>&1
if ($LASTEXITCODE -ne 0) {
    Log-Error "Você não está logado no Azure!"
    Write-Host "Execute: az login" -ForegroundColor Yellow
    exit 1
}
Log-Success "Login verificado"

# Verificar variável de ambiente GEMINI_API_KEY
if (-not $GeminiApiKey) {
    Log-Error "GEMINI_API_KEY não está definida!"
    Write-Host "Defina a variável: `$env:GEMINI_API_KEY = 'sua-chave-aqui'" -ForegroundColor Yellow
    exit 1
}

# Criar Resource Group
Log-Step "Criando Resource Group: $ResourceGroup"
az group create --name $ResourceGroup --location $Location --output none
if ($LASTEXITCODE -eq 0) {
    Log-Success "Resource Group criado/verificado"
} else {
    Log-Error "Erro ao criar Resource Group"
    exit 1
}

# Criar Azure Container Registry
Log-Step "Criando Azure Container Registry: $AcrName"
$acrExists = az acr show --name $AcrName --resource-group $ResourceGroup 2>&1
if ($LASTEXITCODE -ne 0) {
    az acr create `
        --resource-group $ResourceGroup `
        --name $AcrName `
        --sku Basic `
        --admin-enabled true `
        --output none
    
    if ($LASTEXITCODE -eq 0) {
        Log-Success "ACR criado com sucesso"
    } else {
        Log-Error "Erro ao criar ACR"
        exit 1
    }
} else {
    Log-Success "ACR já existe"
}

# Login no ACR
Log-Step "Fazendo login no Azure Container Registry..."
az acr login --name $AcrName
if ($LASTEXITCODE -eq 0) {
    Log-Success "Login no ACR realizado"
} else {
    Log-Error "Erro ao fazer login no ACR"
    exit 1
}

# Build da imagem Docker
Log-Step "Building imagem Docker do backend..."
Push-Location backend
$imageName = "$AcrName.azurecr.io/$BackendAppName`:latest"

docker build -t $imageName .
if ($LASTEXITCODE -eq 0) {
    Log-Success "Build da imagem concluído"
} else {
    Log-Error "Erro no build da imagem"
    Pop-Location
    exit 1
}

# Push da imagem para ACR
Log-Step "Enviando imagem para ACR..."
docker push $imageName
if ($LASTEXITCODE -eq 0) {
    Log-Success "Imagem enviada para ACR"
} else {
    Log-Error "Erro ao enviar imagem"
    Pop-Location
    exit 1
}
Pop-Location

# Instalar extensão Container Apps
Log-Step "Verificando extensão Container Apps..."
az extension add --name containerapp --upgrade --only-show-errors 2>&1 | Out-Null
Log-Success "Extensão Container Apps pronta"

# Criar Container App Environment
Log-Step "Criando Container App Environment..."
$envExists = az containerapp env show --name $EnvironmentName --resource-group $ResourceGroup 2>&1
if ($LASTEXITCODE -ne 0) {
    az containerapp env create `
        --name $EnvironmentName `
        --resource-group $ResourceGroup `
        --location $Location `
        --output none
    
    if ($LASTEXITCODE -eq 0) {
        Log-Success "Environment criado"
    } else {
        Log-Error "Erro ao criar Environment"
        exit 1
    }
} else {
    Log-Success "Environment já existe"
}

# Obter credenciais do ACR
Log-Step "Obtendo credenciais do ACR..."
$acrPassword = az acr credential show --name $AcrName --query "passwords[0].value" -o tsv

# Deploy Container App (criar ou atualizar)
Log-Step "Fazendo deploy do Container App..."
$appExists = az containerapp show --name $BackendAppName --resource-group $ResourceGroup 2>&1

if ($LASTEXITCODE -ne 0) {
    # Criar novo
    az containerapp create `
        --name $BackendAppName `
        --resource-group $ResourceGroup `
        --environment $EnvironmentName `
        --image $imageName `
        --registry-server "$AcrName.azurecr.io" `
        --registry-username $AcrName `
        --registry-password $acrPassword `
        --target-port 8000 `
        --ingress 'external' `
        --min-replicas 1 `
        --max-replicas 3 `
        --cpu 1.0 `
        --memory 2.0Gi `
        --env-vars `
            "ENVIRONMENT=production" `
            "GOOGLE_API_KEY=$GeminiApiKey" `
            "STORAGE_TYPE=local" `
            "LOG_LEVEL=INFO" `
        --output none
} else {
    # Atualizar existente
    az containerapp update `
        --name $BackendAppName `
        --resource-group $ResourceGroup `
        --image $imageName `
        --set-env-vars `
            "ENVIRONMENT=production" `
            "GOOGLE_API_KEY=$GeminiApiKey" `
            "STORAGE_TYPE=local" `
            "LOG_LEVEL=INFO" `
        --output none
}

if ($LASTEXITCODE -eq 0) {
    Log-Success "Container App implantado com sucesso!"
} else {
    Log-Error "Erro ao implantar Container App"
    exit 1
}

# Obter URL do backend
Log-Step "Obtendo URL da aplicação..."
$backendUrl = az containerapp show `
    --name $BackendAppName `
    --resource-group $ResourceGroup `
    --query "properties.configuration.ingress.fqdn" `
    -o tsv

Write-Host ""
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "[SUCESSO] Deploy concluido com sucesso!" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend URL: https://$backendUrl" -ForegroundColor White
Write-Host "API Docs: https://$backendUrl/docs" -ForegroundColor White
Write-Host "Health: https://$backendUrl/health" -ForegroundColor White
Write-Host ""
Write-Host "Ver logs:" -ForegroundColor Yellow
Write-Host "   az containerapp logs show --name $BackendAppName --resource-group $ResourceGroup --follow" -ForegroundColor Gray
Write-Host ""
Write-Host "PROXIMO PASSO: Deploy do Frontend" -ForegroundColor Cyan
Write-Host "   1. Edite frontend/.env.production com a URL do backend:" -ForegroundColor White
Write-Host "      VITE_API_URL=https://$backendUrl" -ForegroundColor Gray
Write-Host "   2. Execute: cd frontend && npm run build" -ForegroundColor White
Write-Host ""
