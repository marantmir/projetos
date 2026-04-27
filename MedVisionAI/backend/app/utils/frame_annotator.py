"""
Utilitários para anotação e visualização de frames de vídeo.

Desenha bounding boxes, labels e cria thumbnails com detecções.
"""

import base64
from typing import Optional

import cv2
import numpy as np

from app.models.enums import AnomalyType
from app.models.schemas import BoundingBox


class FrameAnnotator:
    """
    Classe para anotação visual de frames com detecções.
    
    Funcionalidades:
    - Desenhar bounding boxes coloridas por tipo
    - Adicionar labels com confiança
    - Criar grids de frames críticos
    - Codificar frames em base64
    """
    
    # Esquema de cores BGR para cada tipo de anomalia
    COLOR_SCHEME = {
        AnomalyType.SURGICAL_BLEEDING: (0, 0, 255),        # Vermelho
        AnomalyType.INSTRUMENT_DETECTED: (255, 0, 0),      # Azul
        AnomalyType.ABNORMAL_MOVEMENT: (0, 255, 255),      # Amarelo
        AnomalyType.VOCAL_DISTRESS: (0, 165, 255),         # Laranja
        AnomalyType.DEPRESSION_INDICATOR: (128, 0, 128),   # Roxo
        AnomalyType.ANXIETY_INDICATOR: (0, 255, 128),      # Verde-claro
        AnomalyType.DOMESTIC_VIOLENCE_INDICATOR: (128, 128, 128),  # Cinza
    }
    
    DEFAULT_COLOR = (0, 165, 255)  # Laranja para tipos não mapeados
    
    @staticmethod
    def draw_detections(
        frame: np.ndarray,
        boxes: list[BoundingBox],
        thickness: int = 2,
        font_scale: float = 0.6
    ) -> np.ndarray:
        """
        Desenha bounding boxes e labels em um frame.
        
        Args:
            frame: Frame original em BGR.
            boxes: Lista de detecções a desenhar.
            thickness: Espessura das linhas da box.
            font_scale: Escala da fonte para labels.
        
        Returns:
            Frame anotado (cópia, não modifica o original).
        """
        annotated = frame.copy()
        
        for box in boxes:
            # Determina cor baseada no tipo de anomalia
            color = FrameAnnotator.COLOR_SCHEME.get(
                box.anomaly_type,
                FrameAnnotator.DEFAULT_COLOR
            )
            
            # Coordenadas da box
            x1, y1 = int(box.x1), int(box.y1)
            x2, y2 = int(box.x2), int(box.y2)
            
            # Desenha retângulo
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, thickness)
            
            # Prepara label com confiança
            label = f"{box.label} {box.confidence*100:.0f}%"
            
            # Calcula tamanho do texto para background
            (text_width, text_height), baseline = cv2.getTextSize(
                label,
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                thickness=1
            )
            
            # Desenha background para o texto
            label_y = y1 - 10 if y1 - 10 > text_height else y1 + text_height + 10
            cv2.rectangle(
                annotated,
                (x1, label_y - text_height - baseline),
                (x1 + text_width, label_y + baseline),
                color,
                -1  # Preenchimento
            )
            
            # Desenha texto
            cv2.putText(
                annotated,
                label,
                (x1, label_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                (255, 255, 255),  # Branco
                thickness=1,
                lineType=cv2.LINE_AA
            )
        
        return annotated
    
    @staticmethod
    def frame_to_base64(frame: np.ndarray, quality: int = 85) -> str:
        """
        Codifica um frame como JPEG base64.
        
        Args:
            frame: Frame em BGR.
            quality: Qualidade JPEG (0-100).
        
        Returns:
            String base64 do frame.
        """
        # Codifica como JPEG
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        _, buffer = cv2.imencode('.jpg', frame, encode_param)
        
        # Converte para base64
        b64_str = base64.b64encode(buffer).decode('utf-8')
        
        return b64_str
    
    @staticmethod
    def create_summary_thumbnail(
        frames: list[np.ndarray],
        boxes_per_frame: list[list[BoundingBox]],
        grid_size: tuple[int, int] = (3, 3),
        thumbnail_size: tuple[int, int] = (320, 240)
    ) -> np.ndarray:
        """
        Cria uma grade (grid) com os frames mais críticos anotados.
        
        Args:
            frames: Lista de frames (ordenados por criticidade).
            boxes_per_frame: Lista de detecções para cada frame correspondente.
            grid_size: Tupla (linhas, colunas) da grade.
            thumbnail_size: Tamanho de cada thumbnail individual.
        
        Returns:
            Imagem grid com frames anotados.
        """
        rows, cols = grid_size
        thumb_w, thumb_h = thumbnail_size
        
        # Cria canvas vazio
        grid_h = rows * thumb_h
        grid_w = cols * thumb_w
        grid = np.zeros((grid_h, grid_w, 3), dtype=np.uint8)
        
        # Preenche grid
        for i in range(min(len(frames), rows * cols)):
            row = i // cols
            col = i % cols
            
            # Redimensiona e anota frame
            frame_resized = cv2.resize(frames[i], thumbnail_size)
            frame_annotated = FrameAnnotator.draw_detections(
                frame_resized,
                boxes_per_frame[i],
                thickness=1,
                font_scale=0.4
            )
            
            # Posiciona no grid
            y_start = row * thumb_h
            y_end = y_start + thumb_h
            x_start = col * thumb_w
            x_end = x_start + thumb_w
            
            grid[y_start:y_end, x_start:x_end] = frame_annotated
        
        return grid
    
    @staticmethod
    def add_timestamp_overlay(
        frame: np.ndarray,
        timestamp: float,
        position: tuple[int, int] = (10, 30)
    ) -> np.ndarray:
        """
        Adiciona overlay de timestamp no frame.
        
        Args:
            frame: Frame original.
            timestamp: Timestamp em segundos.
            position: Posição (x, y) do texto.
        
        Returns:
            Frame com timestamp sobreposto.
        """
        annotated = frame.copy()
        
        # Formata timestamp como MM:SS.ms
        minutes = int(timestamp // 60)
        seconds = timestamp % 60
        time_str = f"{minutes:02d}:{seconds:05.2f}"
        
        # Desenha background semi-transparente
        overlay = annotated.copy()
        cv2.rectangle(overlay, (5, 5), (150, 45), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, annotated, 0.4, 0, annotated)
        
        # Desenha texto
        cv2.putText(
            annotated,
            time_str,
            position,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            thickness=2,
            lineType=cv2.LINE_AA
        )
        
        return annotated
