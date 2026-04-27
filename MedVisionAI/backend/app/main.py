"""
Aplicação principal FastAPI — MedVision AI.

Este é o ponto de entrada da API backend. Configura a aplicação FastAPI,
registra routers, middlewares, CORS, logging e gerencia o ciclo de vida.
"""

import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logging_config import setup_logging, get_logger, RequestLogger
from app.core.security import SecurityHeaders
from app.services import get_yolo_service
from app.api.routes import video, audio, reports, websocket

# Configura logging
setup_logging()
logger = get_logger(__name__)

# Singleton do modelo YOLO (carregado na startup)
_yolo_model_loaded = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação.
    
    Startup:
    - Carrega modelo YOLOv8 antecipadamente (evita cold start)
    - Inicializa conexões necessárias
    
    Shutdown:
    - Libera recursos
    """
    # === STARTUP ===
    global _yolo_model_loaded
    
    logger.info("=" * 60)
    logger.info(f"Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Ambiente: {settings.APP_ENV}")
    logger.info("=" * 60)
    
    # Carrega modelo YOLO na startup para evitar cold start
    try:
        logger.info("Carregando modelo YOLOv8...")
        yolo_service = get_yolo_service()
        model_info = yolo_service.get_model_info()
        _yolo_model_loaded = True
        logger.info(f"Modelo YOLOv8 carregado: {model_info['model_type']}")
        logger.info(f"Classes detectáveis: {model_info['num_classes']}")
    except Exception as e:
        logger.error(f"ERRO ao carregar modelo YOLOv8: {e}")
        logger.warning("API iniciará sem modelo YOLOv8 - análises de vídeo falharão")
    
    logger.info(f"API pronta em http://0.0.0.0:8000")
    logger.info(f"Documentação: http://0.0.0.0:8000/docs")
    logger.info("=" * 60)
    
    yield
    
    # === SHUTDOWN ===
    logger.info("Encerrando aplicação...")
    logger.info("Recursos liberados com sucesso")


# Inicializa FastAPI
app = FastAPI(
    title="MedVision AI — Análise Multimodal Ginecológica",
    description=(
        "Sistema de análise multimodal para procedimentos cirúrgicos ginecológicos "
        "com detecção de anomalias em tempo real, geração de relatórios automáticos "
        "e análise psicológica de áudio."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# === MIDDLEWARES ===

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Compressão Gzip
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Middleware de logging de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware para logging de todas as requisições HTTP.
    
    Registra: método, path, status code, duração e IP do cliente.
    """
    start_time = time.time()
    
    # Processa requisição
    response = await call_next(request)
    
    # Calcula duração
    duration_ms = (time.time() - start_time) * 1000
    
    # Log estruturado
    request_logger = RequestLogger(logger)
    request_logger.log_request(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
        client_ip=request.client.host if request.client else "unknown"
    )
    
    # Adiciona headers de segurança
    for header_name, header_value in SecurityHeaders.get_headers().items():
        response.headers[header_name] = header_value
    
    return response


# === EXCEPTION HANDLERS ===

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handler para exceções HTTP padrão."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler para erros de validação Pydantic."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Erro de validação",
            "details": exc.errors(),
            "body": exc.body
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para exceções não tratadas."""
    logger.error(
        f"Exceção não tratada em {request.method} {request.url.path}: {exc}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Erro interno do servidor",
            "message": str(exc) if settings.is_development else "Erro inesperado",
            "path": request.url.path
        }
    )


# === ROUTERS ===

# Registra routers de API
app.include_router(video.router)
app.include_router(audio.router)
app.include_router(reports.router)
app.include_router(websocket.router)


# === ENDPOINTS ROOT ===

@app.get("/", tags=["root"])
async def root():
    """Endpoint raiz com informações da API."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "status": "operational",
        "docs": "/docs",
        "endpoints": {
            "video_analysis": "/api/v1/video",
            "audio_analysis": "/api/v1/audio",
            "reports": "/api/v1/reports",
            "websocket": "/ws"
        }
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint para monitoramento.
    
    Retorna status da aplicação e serviços críticos.
    """
    from app.services import get_yolo_service
    
    health_status = {
        "status": "ok",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "services": {
            "yolo_model": _yolo_model_loaded,
            "gemini_api": True,  # TODO: verificar conexão real
        }
    }
    
    # Se modelo não está carregado, status é degradado
    if not _yolo_model_loaded:
        health_status["status"] = "degraded"
        health_status["warnings"] = ["Modelo YOLOv8 não carregado"]
    
    status_code = (
        status.HTTP_200_OK if health_status["status"] == "ok"
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    
    return JSONResponse(
        status_code=status_code,
        content=health_status
    )


@app.get("/model-info", tags=["info"])
async def get_model_info():
    """
    Retorna informações sobre os modelos de IA carregados.
    
    Útil para debugging e verificação de configuração.
    """
    try:
        from app.services import get_yolo_service
        
        yolo_service = get_yolo_service()
        yolo_info = yolo_service.get_model_info()
        
        return {
            "yolo": yolo_info,
            "gemini": {
                "model": settings.GEMINI_MODEL,
                "max_retries": settings.GEMINI_MAX_RETRIES
            }
        }
    except Exception as e:
        logger.error(f"Erro ao obter informações do modelo: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e)}
        )


if __name__ == "__main__":
    # Permite rodar com `python -m app.main` para desenvolvimento local
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.lower()
    )
