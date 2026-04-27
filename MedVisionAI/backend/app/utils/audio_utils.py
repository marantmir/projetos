"""
Utilitários para manipulação de arquivos de áudio.

Funções auxiliares para carregamento, conversão e extração de metadados de áudio.
"""

from pathlib import Path
from typing import Optional, Tuple

import librosa
import numpy as np
import soundfile as sf

from app.core.logging_config import get_logger

logger = get_logger(__name__)


def get_audio_info(audio_path: str) -> dict:
    """
    Extrai informações de um arquivo de áudio.
    
    Args:
        audio_path: Caminho do arquivo de áudio.
    
    Returns:
        Dicionário com metadados:
        - duration: Duração em segundos
        - sample_rate: Taxa de amostragem
        - channels: Número de canais
        - samples: Total de amostras
        - size_bytes: Tamanho do arquivo
        - format: Formato do arquivo
    """
    try:
        # Carrega áudio
        y, sr = librosa.load(audio_path, sr=None, mono=False)
        
        # Determina número de canais
        if y.ndim == 1:
            channels = 1
            samples = len(y)
        else:
            channels = y.shape[0]
            samples = y.shape[1]
        
        duration = librosa.get_duration(y=y, sr=sr)
        
        # Tamanho do arquivo
        file_size = Path(audio_path).stat().st_size
        
        # Formato
        file_format = Path(audio_path).suffix[1:].upper()
        
        info = {
            "duration": duration,
            "sample_rate": sr,
            "channels": channels,
            "samples": samples,
            "size_bytes": file_size,
            "size_mb": file_size / (1024 * 1024),
            "format": file_format
        }
        
        return info
    
    except Exception as e:
        logger.error(f"Erro ao extrair info do áudio: {e}")
        raise


def validate_audio_file(audio_path: str) -> Tuple[bool, str]:
    """
    Valida se um arquivo de áudio é válido e pode ser processado.
    
    Args:
        audio_path: Caminho do arquivo de áudio.
    
    Returns:
        Tupla (is_valid, error_message).
    """
    path = Path(audio_path)
    
    # Verifica existência
    if not path.exists():
        return False, "Arquivo não encontrado"
    
    # Verifica se é arquivo
    if not path.is_file():
        return False, "Caminho não é um arquivo"
    
    # Verifica extensão
    allowed_extensions = [".mp3", ".wav", ".m4a", ".ogg", ".webm"]
    if path.suffix.lower() not in allowed_extensions:
        return False, f"Extensão não suportada: {path.suffix}. Use: {', '.join(allowed_extensions)}"
    
    # Verifica tamanho mínimo (pelo menos 1KB)
    file_size = path.stat().st_size
    if file_size < 1024:
        return False, "Arquivo de áudio muito pequeno (< 1KB)"
    
    # Para arquivos .webm, não tenta validar com librosa (requer FFmpeg)
    # O Gemini API tem suporte nativo para webm e fará a validação durante transcrição
    if path.suffix.lower() == ".webm":
        logger.info(f"Arquivo WebM detectado: {path.name} ({file_size / 1024:.1f} KB) - validação básica aprovada")
        return True, "Áudio WebM válido (validação básica)"
    
    # Para outros formatos, tenta carregar com librosa
    try:
        y, sr = librosa.load(audio_path, sr=None, duration=1.0)  # Carrega apenas 1s para validação
        
        if len(y) == 0:
            return False, "Arquivo de áudio vazio"
        
        if sr <= 0:
            return False, "Sample rate inválido"
        
        return True, "Áudio válido"
    
    except Exception as e:
        error_msg = str(e)
        return False, f"Erro ao carregar áudio: {error_msg}"


def convert_to_mono(y: np.ndarray) -> np.ndarray:
    """
    Converte áudio para mono se for estéreo.
    
    Args:
        y: Array de áudio (pode ser 1D ou 2D).
    
    Returns:
        Array 1D de áudio mono.
    """
    if y.ndim == 1:
        return y
    elif y.ndim == 2:
        # Se for estéreo (2 canais), faz média
        return np.mean(y, axis=0)
    else:
        raise ValueError(f"Formato de áudio não suportado: {y.ndim} dimensões")


def trim_silence(
    y: np.ndarray,
    sr: int,
    top_db: float = 20.0
) -> np.ndarray:
    """
    Remove silêncio do início e fim do áudio.
    
    Args:
        y: Array de áudio.
        sr: Sample rate.
        top_db: Threshold de dB para considerar silêncio.
    
    Returns:
        Array de áudio sem silêncio nas extremidades.
    """
    # Usa librosa para detectar e remover silêncio
    trimmed, _ = librosa.effects.trim(y, top_db=top_db)
    
    duration_original = len(y) / sr
    duration_trimmed = len(trimmed) / sr
    
    logger.debug(
        f"Silêncio removido: {duration_original:.2f}s -> {duration_trimmed:.2f}s "
        f"({duration_original - duration_trimmed:.2f}s removido)"
    )
    
    return trimmed


def normalize_audio(y: np.ndarray, target_db: float = -20.0) -> np.ndarray:
    """
    Normaliza o nível de volume do áudio.
    
    Args:
        y: Array de áudio.
        target_db: dB alvo de normalização.
    
    Returns:
        Array de áudio normalizado.
    """
    # Calcula RMS atual
    rms = np.sqrt(np.mean(y**2))
    
    if rms == 0:
        return y
    
    # Calcula fator de normalização
    current_db = 20 * np.log10(rms)
    gain_db = target_db - current_db
    gain_linear = 10 ** (gain_db / 20)
    
    # Aplica ganho
    normalized = y * gain_linear
    
    # Clipa para evitar distorção
    normalized = np.clip(normalized, -1.0, 1.0)
    
    logger.debug(f"Áudio normalizado: {current_db:.1f}dB -> {target_db:.1f}dB")
    
    return normalized


def extract_audio_segment(
    audio_path: str,
    start_time: float,
    end_time: float,
    sr: Optional[int] = None
) -> Tuple[np.ndarray, int]:
    """
    Extrai um segmento específico de um arquivo de áudio.
    
    Args:
        audio_path: Caminho do arquivo de áudio.
        start_time: Tempo de início em segundos.
        end_time: Tempo de fim em segundos.
        sr: Sample rate desejado (None = original).
    
    Returns:
        Tupla (segmento_audio, sample_rate).
    """
    # Calcula offset e duração
    offset = start_time
    duration = end_time - start_time
    
    # Carrega segmento
    y, sr_loaded = librosa.load(
        audio_path,
        sr=sr,
        offset=offset,
        duration=duration
    )
    
    return y, sr_loaded


def save_audio(
    y: np.ndarray,
    sr: int,
    output_path: str,
    format: Optional[str] = None
) -> bool:
    """
    Salva array de áudio em arquivo.
    
    Args:
        y: Array de áudio.
        sr: Sample rate.
        output_path: Caminho do arquivo de saída.
        format: Formato (WAV, MP3, etc.). Inferido da extensão se None.
    
    Returns:
        True se salvo com sucesso, False caso contrário.
    """
    try:
        sf.write(output_path, y, sr, format=format)
        logger.info(f"Áudio salvo: {output_path}")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao salvar áudio: {e}")
        return False


def compute_audio_fingerprint(y: np.ndarray, sr: int) -> np.ndarray:
    """
    Calcula fingerprint (assinatura) de áudio para comparação.
    
    Usa chromagram como fingerprint simplificado.
    
    Args:
        y: Array de áudio.
        sr: Sample rate.
    
    Returns:
        Array de fingerprint.
    """
    # Calcula chromagram
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    
    # Reduz dimensionalidade com média temporal
    fingerprint = np.mean(chroma, axis=1)
    
    return fingerprint
