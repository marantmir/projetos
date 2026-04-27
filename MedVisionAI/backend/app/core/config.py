"""
Configuração centralizada da aplicação usando Pydantic Settings.

Carrega variáveis de ambiente do arquivo .env e fornece valores padrão
seguros. Todas as configurações críticas devem ser definidas aqui.
"""

from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações da aplicação MedVision AI.
    
    Carrega automaticamente do arquivo .env na raiz do backend.
    Use settings = get_settings() para obter a instância singleton.
    """
    
    # Google Gemini API
    GOOGLE_API_KEY: str = Field(..., description="API key do Google Gemini")
    GEMINI_MODEL: str = Field(
        default="gemini-2.5-flash",
        description="Modelo Gemini a usar (ex: gemini-2.5-flash, gemini-2.5-pro, gemini-flash-latest)"
    )
    
    # YOLOv8 Configuration
    YOLO_MODEL_PATH: str = Field(
        default="models_weights/yolov8_gyneco.pt",
        description="Caminho do modelo YOLOv8 customizado"
    )
    ANOMALY_CONFIDENCE_THRESHOLD: float = Field(
        default=0.45,
        ge=0.0,
        le=1.0,
        description="Limiar de confiança para detecção de anomalias"
    )
    
    # Upload Configuration
    MAX_UPLOAD_SIZE_MB: int = Field(
        default=500,
        ge=1,
        description="Tamanho máximo de upload em megabytes"
    )
    ALLOWED_VIDEO_EXTENSIONS: list[str] = Field(
        default=[".mp4", ".avi", ".mov", ".mkv"],
        description="Extensões de vídeo permitidas"
    )
    ALLOWED_AUDIO_EXTENSIONS: list[str] = Field(
        default=[".mp3", ".wav", ".m4a", ".ogg", ".webm"],
        description="Extensões de áudio permitidas"
    )
    
    # WebSocket Configuration
    WEBSOCKET_HEARTBEAT_INTERVAL: int = Field(
        default=30,
        ge=5,
        description="Intervalo do heartbeat WebSocket em segundos"
    )
    
    # Storage Configuration
    STORAGE_BACKEND: str = Field(
        default="local",
        description="Backend de armazenamento: local, s3 ou gcs"
    )
    STORAGE_LOCAL_PATH: str = Field(
        default="./storage",
        description="Diretório local para armazenamento"
    )
    AWS_S3_BUCKET: Optional[str] = Field(
        default=None,
        description="Nome do bucket S3 (se STORAGE_BACKEND=s3)"
    )
    AWS_ACCESS_KEY_ID: Optional[str] = Field(
        default=None,
        description="AWS Access Key ID"
    )
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(
        default=None,
        description="AWS Secret Access Key"
    )
    AWS_REGION: str = Field(
        default="us-east-1",
        description="Região AWS"
    )
    GCS_BUCKET: Optional[str] = Field(
        default=None,
        description="Nome do bucket GCS (se STORAGE_BACKEND=gcs)"
    )
    GCS_PROJECT_ID: Optional[str] = Field(
        default=None,
        description="ID do projeto Google Cloud"
    )
    
    # CORS Configuration
    CORS_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:5174,http://localhost:3000",
        description="Origens permitidas para CORS (separadas por vírgula)"
    )
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Retorna CORS_ORIGINS como lista."""
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    # Application Configuration
    APP_ENV: str = Field(
        default="development",
        description="Ambiente: development, staging ou production"
    )
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Nível de log: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )
    APP_NAME: str = Field(
        default="MedVision AI",
        description="Nome da aplicação"
    )
    APP_VERSION: str = Field(
        default="1.0.0",
        description="Versão da aplicação"
    )
    
    # Processing Configuration
    VIDEO_FRAME_SAMPLE_RATE: int = Field(
        default=30,
        ge=1,
        description="Processar 1 frame a cada N frames"
    )
    VIDEO_SHORT_DURATION_THRESHOLD: int = Field(
        default=60,
        ge=1,
        description="Vídeos menores que isso (segundos) usam sample rate menor"
    )
    VIDEO_SHORT_SAMPLE_RATE: int = Field(
        default=10,
        ge=1,
        description="Sample rate para vídeos curtos"
    )
    AUDIO_SEGMENT_DURATION: float = Field(
        default=10.0,
        ge=1.0,
        description="Duração dos segmentos de áudio em segundos"
    )
    AUDIO_SEGMENT_OVERLAP: float = Field(
        default=2.0,
        ge=0.0,
        description="Overlap entre segmentos de áudio em segundos"
    )
    
    # Redis Configuration (para fila de tasks)
    REDIS_HOST: str = Field(default="redis", description="Host do Redis")
    REDIS_PORT: int = Field(default=6379, ge=1, le=65535, description="Porta do Redis")
    REDIS_DB: int = Field(default=0, ge=0, description="Banco de dados Redis")
    
    # Gemini API Configuration
    GEMINI_MAX_RETRIES: int = Field(
        default=3,
        ge=1,
        description="Número máximo de tentativas para chamadas à API Gemini"
    )
    GEMINI_RETRY_DELAY: float = Field(
        default=1.0,
        ge=0.1,
        description="Delay inicial para retry exponencial (segundos)"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @field_validator("STORAGE_BACKEND")
    @classmethod
    def validate_storage_backend(cls, v: str) -> str:
        """Valida que o storage backend é um dos suportados."""
        allowed = ["local", "s3", "gcs"]
        if v not in allowed:
            raise ValueError(f"STORAGE_BACKEND deve ser um de: {', '.join(allowed)}")
        return v
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Valida que o log level é válido."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed:
            raise ValueError(f"LOG_LEVEL deve ser um de: {', '.join(allowed)}")
        return v_upper
    
    @property
    def max_upload_size_bytes(self) -> int:
        """Retorna o tamanho máximo de upload em bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    
    @property
    def is_production(self) -> bool:
        """Verifica se está em ambiente de produção."""
        return self.APP_ENV.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Verifica se está em ambiente de desenvolvimento."""
        return self.APP_ENV.lower() == "development"


# Singleton para garantir que as configurações sejam carregadas uma única vez
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Obtém a instância singleton das configurações.
    
    Returns:
        Instância configurada de Settings.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Atalho para uso direto
settings = get_settings()
