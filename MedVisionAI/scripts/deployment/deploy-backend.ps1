# Script para deploy do backend no Google Cloud Run
# Uso: .\deploy-backend.ps1

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,
    
    [Parameter(Mandatory=$true)]
    [string]$GeminiApiKey,
    
    [string]$Region = "us-central1",
    [string]$ServiceName = "medvision-backend"
)

Write-Host "Deploy MedVision Backend para Cloud Run" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Configurar projeto
Write-Host "Configurando projeto GCP: $ProjectId" -ForegroundColor Yellow
gcloud config set project $ProjectId

# Navegar para diretório do backend
Write-Host "Navegando para diretorio backend..." -ForegroundColor Yellow
Set-Location -Path "$PSScriptRoot\backend"

# Build da imagem Docker
Write-Host "Building Docker image..." -ForegroundColor Yellow
$imageName = "gcr.io/$ProjectId/$ServiceName:latest"
docker build -t $imageName .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro no build da imagem!" -ForegroundColor Red
    exit 1
}

# Configurar Docker para GCR
Write-Host "Configurando autenticacao Docker..." -ForegroundColor Yellow
gcloud auth configure-docker --quiet

# Push da imagem
Write-Host "Pushing imagem para Google Container Registry..." -ForegroundColor Yellow
docker push $imageName

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro no push da imagem!" -ForegroundColor Red
    exit 1
}

# Deploy no Cloud Run
Write-Host "Deploying para Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $ServiceName `
    --image $imageName `
    --platform managed `
    --region $Region `
    --memory 4Gi `
    --cpu 2 `
    --timeout 3600 `
    --max-instances 10 `
    --min-instances 0 `
    --allow-unauthenticated `
    --set-env-vars "GEMINI_API_KEY=$GeminiApiKey,ENVIRONMENT=production,LOG_LEVEL=INFO"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro no deploy!" -ForegroundColor Red
    exit 1
}

# Obter URL do serviço
Write-Host ""
Write-Host "Deploy concluido com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "Obtendo URL do servico..." -ForegroundColor Yellow
$serviceUrl = gcloud run services describe $ServiceName --region $Region --format "value(status.url)"

Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host "BACKEND DEPLOYADO COM SUCESSO!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
Write-Host "URL do Backend: $serviceUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "Links uteis:" -ForegroundColor Yellow
Write-Host "   Console: https://console.cloud.google.com/run/detail/$Region/$ServiceName" -ForegroundColor White
Write-Host "   Logs: gcloud run logs read $ServiceName --region $Region" -ForegroundColor White
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Yellow
Write-Host "   1. Copie a URL acima" -ForegroundColor White
Write-Host "   2. Configure no frontend/.env.production:" -ForegroundColor White
Write-Host "      VITE_API_URL=$serviceUrl" -ForegroundColor Cyan
$wsUrl = $serviceUrl.Replace("https://", "wss://")
Write-Host "      VITE_WS_URL=$wsUrl" -ForegroundColor Cyan
Write-Host ""
