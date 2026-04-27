#!/bin/bash

# =========================================
# Script de Inicialização Rápida
# MedVision AI - Setup Completo
# =========================================

set -e

echo "🏥 MedVision AI - Inicialização Rápida"
echo "======================================"
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função de log
log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Verifica pré-requisitos
echo "🔍 Verificando pré-requisitos..."

if ! command -v python &> /dev/null; then
    log_error "Python não encontrado. Instale Python 3.11+"
    exit 1
fi
log_success "Python encontrado: $(python --version)"

if ! command -v node &> /dev/null; then
    log_error "Node.js não encontrado. Instale Node.js 20+"
    exit 1
fi
log_success "Node.js encontrado: $(node --version)"

if ! command -v docker &> /dev/null; then
    log_warning "Docker não encontrado. Modo manual será usado."
    USE_DOCKER=false
else
    log_success "Docker encontrado: $(docker --version)"
    USE_DOCKER=true
fi

echo ""

# Pergunta ao usuário o método de setup
echo "Escolha o método de inicialização:"
echo "  1) Docker Compose (recomendado)"
echo "  2) Manual (desenvolvimento)"
read -p "Opção [1-2]: " setup_choice

if [ "$setup_choice" == "1" ] && [ "$USE_DOCKER" == true ]; then
    echo ""
    echo "🐳 Iniciando com Docker Compose..."
    
    # Verifica se .env existe
    if [ ! -f backend/.env ]; then
        log_warning "Arquivo backend/.env não encontrado"
        echo "Digite sua chave API do Google Gemini:"
        read -p "GEMINI_API_KEY: " gemini_key
        
        cat > backend/.env << EOF
ENVIRONMENT=development
LOG_LEVEL=DEBUG
GEMINI_API_KEY=${gemini_key}
YOLO_MODEL_PATH=/app/data/models/yolov8n.pt
STORAGE_TYPE=local
STORAGE_LOCAL_PATH=/app/data/uploads
REDIS_URL=redis://redis:6379/0
EOF
        log_success "Arquivo backend/.env criado"
    fi
    
    # Build e start
    echo ""
    echo "🏗️  Fazendo build das imagens (pode levar alguns minutos)..."
    docker-compose build
    
    echo ""
    echo "🚀 Iniciando serviços..."
    docker-compose up -d
    
    echo ""
    log_success "MedVision AI iniciado com sucesso!"
    echo ""
    echo "📍 URLs dos serviços:"
    echo "   Frontend:  http://localhost:5173"
    echo "   Backend:   http://localhost:8000"
    echo "   API Docs:  http://localhost:8000/docs"
    echo "   Redis:     localhost:6379"
    echo ""
    echo "Para ver logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "Para parar:"
    echo "   docker-compose down"

elif [ "$setup_choice" == "2" ]; then
    echo ""
    echo "🔧 Configuração Manual..."
    
    # Backend setup
    echo ""
    echo "📦 Configurando Backend..."
    cd backend
    
    if [ ! -d "venv" ]; then
        log_warning "Criando ambiente virtual Python..."
        python -m venv venv
    fi
    
    log_success "Ativando ambiente virtual..."
    source venv/bin/activate
    
    log_success "Instalando dependências Python..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    
    if [ ! -f .env ]; then
        log_warning "Arquivo .env não encontrado"
        echo "Digite sua chave API do Google Gemini:"
        read -p "GEMINI_API_KEY: " gemini_key
        
        cat > .env << EOF
ENVIRONMENT=development
LOG_LEVEL=DEBUG
GEMINI_API_KEY=${gemini_key}
YOLO_MODEL_PATH=./data/models/yolov8n.pt
STORAGE_TYPE=local
STORAGE_LOCAL_PATH=./data/uploads
REDIS_URL=redis://localhost:6379/0
EOF
        log_success "Arquivo .env criado"
    fi
    
    cd ..
    
    # Frontend setup
    echo ""
    echo "📦 Configurando Frontend..."
    cd frontend
    
    log_success "Instalando dependências Node.js..."
    npm install --silent
    
    if [ ! -f .env ]; then
        cat > .env << EOF
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
EOF
        log_success "Arquivo .env criado"
    fi
    
    cd ..
    
    # Criar diretórios necessários
    mkdir -p backend/data/models
    mkdir -p backend/data/uploads
    
    echo ""
    log_success "Configuração concluída!"
    echo ""
    echo "🚀 Para iniciar os serviços:"
    echo ""
    echo "Terminal 1 (Backend):"
    echo "  cd backend"
    echo "  source venv/bin/activate"
    echo "  uvicorn app.main:app --reload --port 8000"
    echo ""
    echo "Terminal 2 (Frontend):"
    echo "  cd frontend"
    echo "  npm run dev"
    echo ""
    echo "Terminal 3 (Redis - opcional):"
    echo "  redis-server"
    echo ""
    echo "📍 URLs dos serviços:"
    echo "   Frontend:  http://localhost:5173"
    echo "   Backend:   http://localhost:8000"
    echo "   API Docs:  http://localhost:8000/docs"

else
    log_error "Opção inválida ou Docker não disponível"
    exit 1
fi

echo ""
echo "✨ Setup completo! Boa análise! ✨"
