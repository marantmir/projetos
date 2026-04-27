# 🚀 Guia de Teste Local - MedVision AI

Este guia explica como rodar e testar o sistema localmente passo a passo.

## ✅ Pré-requisitos Verificados

- ✓ Python 3.11+
- ✓ Node.js 20+
- ✓ Chave API do Gemini 2.0 Flash configurada

---

## 📋 Passo a Passo

### 1️⃣ Configurar Backend

```powershell
# Navegar para pasta backend
cd backend

# Criar arquivo .env real (copiar do .env.example)
Copy-Item .env.example .env

# Criar ambiente virtual Python
python -m venv venv

# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Atualizar pip
python -m pip install --upgrade pip

# Instalar dependências (pode demorar 2-3 minutos)
pip install -r requirements.txt

# Criar diretórios necessários
New-Item -ItemType Directory -Force -Path "data\models"
New-Item -ItemType Directory -Force -Path "data\uploads"
New-Item -ItemType Directory -Force -Path "storage"
```

**⚠️ Importante**: O YOLOv8 será baixado automaticamente na primeira execução (~6MB).

---

### 2️⃣ Configurar Frontend

```powershell
# Abrir NOVO terminal PowerShell (deixar backend rodando no outro)
cd frontend

# Criar arquivo .env
Copy-Item .env.example .env

# Instalar dependências (pode demorar 1-2 minutos)
npm install
```

---

### 3️⃣ Iniciar Backend

```powershell
# No terminal do backend (com venv ativado)
cd backend
uvicorn app.main:app --reload --port 8000
```

**Saída esperada:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
INFO:     YOLOv8 model loaded successfully
```

**Testar backend:**
- Abra navegador: http://localhost:8000/health
- Deve retornar: `{"status":"healthy","version":"1.0.0"}`
- API Docs: http://localhost:8000/docs

---

### 4️⃣ Iniciar Frontend

```powershell
# No terminal do frontend
cd frontend
npm run dev
```

**Saída esperada:**
```
VITE v5.3.3  ready in 500 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

**Testar frontend:**
- Abra navegador: http://localhost:5173
- Você deve ver a tela de upload do MedVision AI

---

## 🎥 Testar Upload de Vídeo

### Opção 1: Usar Vídeo de Teste

```powershell
# Criar vídeo de teste simples (10 segundos, 640x480)
cd backend
python -c "
import cv2
import numpy as np

# Criar vídeo sintético
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('test_video.mp4', fourcc, 30.0, (640, 480))

for i in range(300):  # 10 segundos a 30 FPS
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:] = (50, 50, 50)  # Fundo cinza
    
    # Desenhar algo que simula objeto
    cv2.circle(frame, (320, 240), 50, (0, 0, 255), -1)
    cv2.putText(frame, f'Frame {i}', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    out.write(frame)

out.release()
print('Video test_video.mp4 criado!')
"
```

### Opção 2: Usar Vídeo Real

Prepare um vídeo cirúrgico (MP4, AVI ou MOV) com:
- Tamanho máximo: 500 MB
- Formatos aceitos: MP4, AVI, MOV, MKV
- Resolução recomendada: 720p ou 1080p

---

## 🧪 Fluxo de Teste Completo

### 1. Fazer Upload

1. Acesse http://localhost:5173
2. Arraste ou clique para selecionar `test_video.mp4`
3. Clique em "Iniciar Análise"
4. Você será redirecionado para a página de análise

### 2. Monitorar Análise

Na página de análise você verá:

- **✓ Indicador de conexão WebSocket** (topo, em verde)
- **✓ Barra de progresso** mostrando % concluído
- **✓ Painel de alertas** (lado direito) com detecções em tempo real
- **✓ Mensagens** tipo "Frame 45/300" conforme processa

### 3. Visualizar Resultado

Após conclusão (1-3 minutos):

- **✓ Player de vídeo** com controles
- **✓ Bounding boxes** desenhadas sobre objetos detectados
- **✓ Timeline interativa** para navegar pelos frames
- **✓ Relatório Gemini** com análise clínica completa
- **✓ Botão "Baixar Relatório"** para exportar Markdown

---

## 🔍 Verificar Logs

### Backend (terminal backend):
```
INFO:     YOLOv8 model loaded successfully
INFO:     Received video upload: test_video.mp4
INFO:     Starting video analysis: abc123
INFO:     Video analysis completed: abc123
INFO:     Gemini report generated successfully
```

### Frontend (console navegador F12):
```
WebSocket conectado
Mensagem de conexão recebida
Progresso: 25%
Alerta recebido: Objeto detectado
Análise concluída!
```

---

## 📊 Endpoints API para Teste Manual

### Upload Vídeo (cURL)

```powershell
curl -X POST http://localhost:8000/api/v1/video/analyze `
  -F "file=@test_video.mp4" `
  -H "accept: application/json"
```

**Resposta:**
```json
{
  "analysis_id": "abc123-def456-...",
  "status": "processing",
  "message": "Análise de vídeo iniciada"
}
```

### Verificar Status

```powershell
curl http://localhost:8000/api/v1/video/status/abc123-def456-...
```

### Obter Resultado

```powershell
curl http://localhost:8000/api/v1/video/result/abc123-def456-...
```

---

## ❌ Troubleshooting

### Erro: "Module not found"
```powershell
# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

### Erro: "GEMINI_API_KEY not found"
```powershell
# Verificar se .env existe e tem a chave
Get-Content backend\.env | Select-String "GOOGLE_API_KEY"
```

### Erro: "Port 8000 already in use"
```powershell
# Matar processo na porta 8000
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force

# Ou usar outra porta
uvicorn app.main:app --reload --port 8001
```

### Erro: Frontend não conecta ao WebSocket
```powershell
# Verificar se VITE_WS_URL está correto em frontend\.env
# Deve ser: ws://localhost:8000
Get-Content frontend\.env
```

### YOLOv8 não detecta nada
- Isso é normal em vídeos sintéticos
- O modelo yolov8n.pt é treinado no COCO dataset (pessoas, carros, etc.)
- Para detecções cirúrgicas reais, precisa fine-tuning do modelo

---

## 🎯 Próximos Passos Após Teste

1. **✓ Testar upload de vídeo real** (cirurgia ginecológica)
2. **✓ Testar análise de áudio** (endpoint `/api/v1/audio/analyze`)
3. **✓ Verificar relatório Gemini** (qualidade e contexto médico)
4. **✓ Ajustar thresholds** de confiança no `.env`
5. **✓ Fine-tune YOLOv8** com dataset cirúrgico real
6. **✓ Deploy em Docker** quando estiver satisfeito

---

## 📱 Comandos Rápidos

```powershell
# Parar backend: Ctrl+C no terminal
# Parar frontend: Ctrl+C no terminal

# Limpar cache Python
Remove-Item -Recurse -Force backend\__pycache__, backend\app\__pycache__

# Limpar storage local
Remove-Item -Recurse -Force backend\storage\*

# Reiniciar do zero
Remove-Item -Recurse -Force backend\venv, frontend\node_modules
```

---

## ✅ Checklist de Sucesso

- [ ] Backend rodando em http://localhost:8000
- [ ] Frontend rodando em http://localhost:5173
- [ ] API Docs acessível em /docs
- [ ] Upload de vídeo funcional
- [ ] WebSocket conectado (indicador verde)
- [ ] Progresso atualiza em tempo real
- [ ] Alertas aparecem no painel
- [ ] Player de vídeo funciona
- [ ] Bounding boxes aparecem (se houver detecções)
- [ ] Relatório Gemini é gerado
- [ ] Download de relatório funciona

---

**🎉 Pronto para testar! Qualquer erro, consulte a seção Troubleshooting acima.**
