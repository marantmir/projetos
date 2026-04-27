"""
Utilitários para manipulação de arquivos de vídeo.

Funções auxiliares para extração de metadados, conversão de formatos,
e operações comuns de vídeo.
"""

from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np

from app.core.logging_config import get_logger

logger = get_logger(__name__)


def get_video_info(video_path: str) -> dict:
    """
    Extrai informações completas de um arquivo de vídeo.
    
    Args:
        video_path: Caminho do arquivo de vídeo.
    
    Returns:
        Dicionário com metadados:
        - width, height: Dimensões
        - fps: Frames por segundo
        - total_frames: Total de frames
        - duration: Duração em segundos
        - codec: Codec do vídeo
        - size_bytes: Tamanho do arquivo
    """
    cap = cv2.VideoCapture(video_path)
    
    try:
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        # Codec (fourcc)
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
        codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
        
        # Tamanho do arquivo
        file_size = Path(video_path).stat().st_size
        
        info = {
            "width": width,
            "height": height,
            "fps": fps,
            "total_frames": total_frames,
            "duration": duration,
            "codec": codec,
            "size_bytes": file_size,
            "size_mb": file_size / (1024 * 1024)
        }
        
        return info
    
    finally:
        cap.release()


def extract_frame_at_timestamp(
    video_path: str,
    timestamp: float
) -> Optional[np.ndarray]:
    """
    Extrai um frame específico em determinado timestamp.
    
    Args:
        video_path: Caminho do arquivo de vídeo.
        timestamp: Timestamp em segundos.
    
    Returns:
        Frame como array NumPy BGR ou None se falhar.
    """
    cap = cv2.VideoCapture(video_path)
    
    try:
        # Converte timestamp para milissegundos
        timestamp_ms = timestamp * 1000
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp_ms)
        
        ret, frame = cap.read()
        
        if ret:
            return frame
        else:
            logger.warning(f"Falha ao extrair frame em {timestamp}s")
            return None
    
    finally:
        cap.release()


def extract_frames_batch(
    video_path: str,
    timestamps: list[float]
) -> list[Tuple[float, Optional[np.ndarray]]]:
    """
    Extrai múltiplos frames em batch.
    
    Args:
        video_path: Caminho do arquivo de vídeo.
        timestamps: Lista de timestamps desejados.
    
    Returns:
        Lista de tuplas (timestamp, frame).
    """
    cap = cv2.VideoCapture(video_path)
    results = []
    
    try:
        for ts in sorted(timestamps):
            cap.set(cv2.CAP_PROP_POS_MSEC, ts * 1000)
            ret, frame = cap.read()
            results.append((ts, frame if ret else None))
    
    finally:
        cap.release()
    
    return results


def validate_video_file(video_path: str) -> Tuple[bool, str]:
    """
    Valida se um arquivo de vídeo é válido e pode ser processado.
    
    Args:
        video_path: Caminho do arquivo de vídeo.
    
    Returns:
        Tupla (is_valid, error_message).
    """
    path = Path(video_path)
    
    # Verifica existência
    if not path.exists():
        return False, "Arquivo não encontrado"
    
    # Verifica se é arquivo (não diretório)
    if not path.is_file():
        return False, "Caminho não é um arquivo"
    
    # Tenta abrir com OpenCV
    cap = cv2.VideoCapture(video_path)
    
    try:
        if not cap.isOpened():
            return False, "Falha ao abrir o vídeo com OpenCV"
        
        # Verifica se tem pelo menos 1 frame
        ret, _ = cap.read()
        if not ret:
            return False, "Vídeo não contém frames válidos"
        
        # Verifica propriedades básicas
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            return False, "FPS inválido"
        
        return True, "Vídeo válido"
    
    finally:
        cap.release()


def resize_frame_keep_aspect(
    frame: np.ndarray,
    target_size: Tuple[int, int]
) -> np.ndarray:
    """
    Redimensiona frame mantendo aspect ratio.
    
    Args:
        frame: Frame original.
        target_size: Tamanho alvo (width, height).
    
    Returns:
        Frame redimensionado com padding se necessário.
    """
    h, w = frame.shape[:2]
    target_w, target_h = target_size
    
    # Calcula scaling factor mantendo aspect ratio
    scale = min(target_w / w, target_h / h)
    
    new_w = int(w * scale)
    new_h = int(h * scale)
    
    # Redimensiona
    resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    # Adiciona padding preto se necessário
    if new_w != target_w or new_h != target_h:
        # Cria canvas preto
        canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)
        
        # Centraliza frame redimensionado
        y_offset = (target_h - new_h) // 2
        x_offset = (target_w - new_w) // 2
        
        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        
        return canvas
    
    return resized


def create_video_from_frames(
    frames: list[np.ndarray],
    output_path: str,
    fps: float = 30.0,
    codec: str = 'mp4v'
) -> bool:
    """
    Cria um arquivo de vídeo a partir de uma lista de frames.
    
    Args:
        frames: Lista de frames como arrays NumPy.
        output_path: Caminho do vídeo de saída.
        fps: Frames por segundo.
        codec: Codec fourcc (ex: 'mp4v', 'XVID').
    
    Returns:
        True se criado com sucesso, False caso contrário.
    """
    if not frames:
        logger.error("Lista de frames vazia")
        return False
    
    # Obtém dimensões do primeiro frame
    h, w = frames[0].shape[:2]
    
    # Inicializa VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*codec)
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
    
    try:
        for frame in frames:
            out.write(frame)
        
        logger.info(f"Vídeo criado: {output_path} ({len(frames)} frames, {fps} FPS)")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao criar vídeo: {e}")
        return False
    
    finally:
        out.release()
