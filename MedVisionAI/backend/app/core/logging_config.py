"""
Configuração centralizada de logging para a aplicação.

Define formatters, handlers e configuração estruturada de logs
para desenvolvimento e produção.
"""

import logging
import sys
from typing import Any

from .config import settings


class ColoredFormatter(logging.Formatter):
    """
    Formatter customizado que adiciona cores aos logs no terminal.
    
    Usado apenas em desenvolvimento para melhor visualização.
    """
    
    # Códigos de cores ANSI
    COLORS = {
        "DEBUG": "\033[36m",      # Ciano
        "INFO": "\033[32m",       # Verde
        "WARNING": "\033[33m",    # Amarelo
        "ERROR": "\033[31m",      # Vermelho
        "CRITICAL": "\033[35m",   # Magenta
    }
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        """Formata o log record com cores se estiver em development."""
        if settings.is_development:
            levelname = record.levelname
            if levelname in self.COLORS:
                record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        return super().format(record)


def setup_logging() -> None:
    """
    Configura o sistema de logging da aplicação.
    
    Em desenvolvimento: logs coloridos no console com formato detalhado.
    Em produção: logs estruturados em JSON para integração com sistemas de monitoramento.
    """
    
    # Remove handlers existentes para evitar duplicação
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Define o nível de log global
    log_level = getattr(logging, settings.LOG_LEVEL)
    root_logger.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    if settings.is_production:
        # Formato JSON estruturado para produção
        formatter = logging.Formatter(
            '{"time":"%(asctime)s", "level":"%(levelname)s", "name":"%(name)s", '
            '"message":"%(message)s", "module":"%(module)s", "function":"%(funcName)s", '
            '"line":%(lineno)d}',
            datefmt="%Y-%m-%dT%H:%M:%S"
        )
    else:
        # Formato legível para desenvolvimento
        formatter = ColoredFormatter(
            "[%(asctime)s] %(levelname)-8s [%(name)s:%(funcName)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Silencia logs muito verbosos de bibliotecas externas
    logging.getLogger("ultralytics").setLevel(logging.WARNING)
    logging.getLogger("google.generativeai").setLevel(logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    logging.info(f"Logging configurado - Nível: {settings.LOG_LEVEL}, Ambiente: {settings.APP_ENV}")


def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger com o nome especificado.
    
    Args:
        name: Nome do logger (geralmente __name__ do módulo).
    
    Returns:
        Instância de Logger configurada.
    """
    return logging.getLogger(name)


class RequestLogger:
    """
    Classe auxiliar para logging estruturado de requisições HTTP.
    
    Pode ser expandida para incluir tracing distribuído e métricas.
    """
    
    def __init__(self, logger: logging.Logger):
        """
        Inicializa o request logger.
        
        Args:
            logger: Logger pai a ser usado.
        """
        self.logger = logger
    
    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        **extra: Any
    ) -> None:
        """
        Registra uma requisição HTTP.
        
        Args:
            method: Método HTTP (GET, POST, etc.).
            path: Caminho da requisição.
            status_code: Código de status HTTP.
            duration_ms: Duração da requisição em milissegundos.
            **extra: Campos adicionais para logging.
        """
        log_msg = f"{method} {path} - {status_code} ({duration_ms:.2f}ms)"
        
        if status_code >= 500:
            self.logger.error(log_msg, extra=extra)
        elif status_code >= 400:
            self.logger.warning(log_msg, extra=extra)
        else:
            self.logger.info(log_msg, extra=extra)
