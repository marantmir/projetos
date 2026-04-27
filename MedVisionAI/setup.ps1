# =========================================
# Script de Inicialização Rápida - Windows
# MedVision AI - Setup Completo
# =========================================

Write-Host "🏥 MedVision AI - Inicialização Rápida" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

function Log-Success {
    param($message)
    Write-Host "✓ $message" -ForegroundColor Green
}

function Log-Warning {
    param($message)
    Write-Host "⚠ $message" -ForegroundColor Yellow
}

function Log-Error {
    param($message)
    Write-Host "✗ $message" -ForegroundColor Red
}

# Verifica pré-requisitos
Write-Host "🔍 Verificando pré-requisitos..."

try {
    $pythonVersion = python --version 2>&1
    Log-Success "Python encontrado: $pythonVersion"
} catch {
    Log-Error "Python não encontrado. Instale Python 3.11+"
    exit 1
}

try {
    $nodeVersion = node --version
    Log-Success "Node.js encontrado: $nodeVersion"
} catch {
    Log-Error "Node.js não encontrado. Instale Node.js 20+"
    exit 1
}

$USE_DOCKER = $false
try {
    $dockerVersion = docker --version
    Log-Success "Docker encontrado: $dockerVersion"
    $USE_DOCKER = $true
} catch {
    Log-Warning "Docker não encontrado. Modo manual será usado."
}

Write-Host ""

# Pergunta ao usuário o método de setup
Write-Host "Escolha o método de inicialização:"
Write-Host "  1) Docker Compose (recomendado)"
Write-Host "  2) Manual (desenvolvimento)"
$setup_choice = Read-Host "Opção [1-2]"

if ($setup_choice -eq "1" -and $USE_DOCKER) {
    Write-Host ""
    Write-Host "🐳 Iniciando com Docker Compose..."
    
    # Verifica se .env existe
    if (-not (Test-Path "backend\.env")) {
        Log-Warning "Arquivo backend\.env não encontrado"
        $gemini_key = Read-Host "Digite sua chave API do Google Gemini"
        
        @"
ENVIRONMENT=development
LOG_LEVEL=DEBUG
GEMINI_API_KEY=$gemini_key
YOLO_MODEL_PATH=/app/data/models/yolov8n.pt
STORAGE_TYPE=local
STORAGE_LOCAL_PATH=/app/data/uploads
REDIS_URL=redis://redis:6379/0
"@ | Out-File -FilePath "backend\.env" -Encoding UTF8
        Log-Success "Arquivo backend\.env criado"
    }
    
    # Build e start
    Write-Host ""
    Write-Host "🏗️  Fazendo build das imagens (pode levar alguns minutos)..."
    docker-compose build
    
    Write-Host ""
    Write-Host "🚀 Iniciando serviços..."
    docker-compose up -d
    
    Write-Host ""
    Log-Success "MedVision AI iniciado com sucesso!"
    Write-Host ""
    Write-Host "📍 URLs dos serviços:"
    Write-Host "   Frontend:  http://localhost:5173"
    Write-Host "   Backend:   http://localhost:8000"
    Write-Host "   API Docs:  http://localhost:8000/docs"
    Write-Host "   Redis:     localhost:6379"
    Write-Host ""
    Write-Host "Para ver logs:"
    Write-Host "   docker-compose logs -f"
    Write-Host ""
    Write-Host "Para parar:"
    Write-Host "   docker-compose down"

} elseif ($setup_choice -eq "2") {
    Write-Host ""
    Write-Host "🔧 Configuração Manual..."
    
    # Backend setup
    Write-Host ""
    Write-Host "📦 Configurando Backend..."
    Set-Location backend
    
    if (-not (Test-Path "venv")) {
        Log-Warning "Criando ambiente virtual Python..."
        python -m venv venv
    }
    
    Log-Success "Ativando ambiente virtual..."
    .\venv\Scripts\Activate.ps1
    
    Log-Success "Instalando dependências Python..."
    python -m pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt
    
    if (-not (Test-Path ".env")) {
        Log-Warning "Arquivo .env não encontrado"
        $gemini_key = Read-Host "Digite sua chave API do Google Gemini"
        
        @"
ENVIRONMENT=development
LOG_LEVEL=DEBUG
GEMINI_API_KEY=$gemini_key
YOLO_MODEL_PATH=./data/models/yolov8n.pt
STORAGE_TYPE=local
STORAGE_LOCAL_PATH=./data/uploads
REDIS_URL=redis://localhost:6379/0
"@ | Out-File -FilePath ".env" -Encoding UTF8
        Log-Success "Arquivo .env criado"
    }
    
    Set-Location ..
    
    # Frontend setup
    Write-Host ""
    Write-Host "📦 Configurando Frontend..."
    Set-Location frontend
    
    Log-Success "Instalando dependências Node.js..."
    npm install --silent
    
    if (-not (Test-Path ".env")) {
        @"
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
"@ | Out-File -FilePath ".env" -Encoding UTF8
        Log-Success "Arquivo .env criado"
    }
    
    Set-Location ..
    
    # Criar diretórios necessários
    New-Item -ItemType Directory -Force -Path "backend\data\models" | Out-Null
    New-Item -ItemType Directory -Force -Path "backend\data\uploads" | Out-Null
    
    Write-Host ""
    Log-Success "Configuração concluída!"
    Write-Host ""
    Write-Host "🚀 Para iniciar os serviços:"
    Write-Host ""
    Write-Host "Terminal 1 (Backend):"
    Write-Host "  cd backend"
    Write-Host "  .\venv\Scripts\Activate.ps1"
    Write-Host "  uvicorn app.main:app --reload --port 8000"
    Write-Host ""
    Write-Host "Terminal 2 (Frontend):"
    Write-Host "  cd frontend"
    Write-Host "  npm run dev"
    Write-Host ""
    Write-Host "📍 URLs dos serviços:"
    Write-Host "   Frontend:  http://localhost:5173"
    Write-Host "   Backend:   http://localhost:8000"
    Write-Host "   API Docs:  http://localhost:8000/docs"

} else {
    Log-Error "Opção inválida ou Docker não disponível"
    exit 1
}

Write-Host ""
Write-Host "✨ Setup completo! Boa análise! ✨" -ForegroundColor Magenta
