"""
Módulo de segurança para autenticação, autorização e sanitização de dados.

Funções para validação de uploads, geração de tokens seguros e verificação
de integridade de arquivos.
"""

import hashlib
import secrets
import uuid
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, UploadFile, status

from .config import settings


def generate_analysis_id() -> str:
    """
    Gera um ID único para uma análise usando UUID4.
    
    Returns:
        String UUID formatada.
    """
    return str(uuid.uuid4())


def generate_secure_token(length: int = 32) -> str:
    """
    Gera um token seguro criptograficamente.
    
    Args:
        length: Comprimento do token em bytes.
    
    Returns:
        Token hexadecimal.
    """
    return secrets.token_hex(length)


def validate_file_extension(filename: str, allowed_extensions: list[str]) -> bool:
    """
    Valida se a extensão do arquivo está na lista de permitidas.
    
    Args:
        filename: Nome do arquivo a validar.
        allowed_extensions: Lista de extensões permitidas (incluindo o ponto).
    
    Returns:
        True se a extensão é válida, False caso contrário.
    """
    file_path = Path(filename)
    extension = file_path.suffix.lower()
    return extension in [ext.lower() for ext in allowed_extensions]


def validate_file_size(file_size: int, max_size_bytes: int) -> bool:
    """
    Valida se o tamanho do arquivo está dentro do limite.
    
    Args:
        file_size: Tamanho do arquivo em bytes.
        max_size_bytes: Tamanho máximo permitido em bytes.
    
    Returns:
        True se o tamanho é válido, False caso contrário.
    """
    return 0 < file_size <= max_size_bytes


async def validate_upload_file(
    file: UploadFile,
    file_type: str = "video"
) -> None:
    """
    Valida um arquivo de upload quanto a extensão e tamanho.
    
    Args:
        file: Arquivo de upload do FastAPI.
        file_type: Tipo de arquivo ("video" ou "audio").
    
    Raises:
        HTTPException: Se o arquivo não passar na validação.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome de arquivo não fornecido"
        )
    
    # Valida extensão
    if file_type == "video":
        allowed = settings.ALLOWED_VIDEO_EXTENSIONS
        file_type_name = "vídeo"
    elif file_type == "audio":
        allowed = settings.ALLOWED_AUDIO_EXTENSIONS
        file_type_name = "áudio"
    else:
        raise ValueError(f"Tipo de arquivo inválido: {file_type}")
    
    if not validate_file_extension(file.filename, allowed):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extensão de arquivo inválida. Permitidas: {', '.join(allowed)}"
        )
    
    # Valida tamanho (se disponível no header)
    if file.size:
        max_size = settings.max_upload_size_bytes
        if not validate_file_size(file.size, max_size):
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Arquivo muito grande. Máximo: {settings.MAX_UPLOAD_SIZE_MB}MB"
            )


def compute_file_hash(file_path: Path, algorithm: str = "sha256") -> str:
    """
    Calcula o hash de um arquivo para verificação de integridade.
    
    Args:
        file_path: Caminho do arquivo.
        algorithm: Algoritmo de hash (md5, sha1, sha256, etc.).
    
    Returns:
        Hash hexadecimal do arquivo.
    """
    hash_func = hashlib.new(algorithm)
    
    with open(file_path, "rb") as f:
        # Lê em chunks para não sobrecarregar memória com arquivos grandes
        for chunk in iter(lambda: f.read(8192), b""):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza um nome de arquivo removendo caracteres perigosos.
    
    Args:
        filename: Nome do arquivo original.
    
    Returns:
        Nome de arquivo seguro.
    """
    # Remove caracteres especiais perigosos
    dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    safe_name = filename
    
    for char in dangerous_chars:
        safe_name = safe_name.replace(char, '_')
    
    # Limita comprimento
    if len(safe_name) > 255:
        path = Path(safe_name)
        name = path.stem[:200]
        ext = path.suffix
        safe_name = name + ext
    
    return safe_name


class SecurityHeaders:
    """
    Headers de segurança para respostas HTTP.
    
    Pode ser expandido para incluir CSP, HSTS, etc.
    """
    
    @staticmethod
    def get_headers() -> dict[str, str]:
        """
        Retorna headers de segurança recomendados.
        
        Returns:
            Dicionário de headers HTTP.
        """
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        }
