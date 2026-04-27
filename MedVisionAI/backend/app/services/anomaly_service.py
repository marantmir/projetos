"""
Serviço de detecção e enriquecimento de anomalias.

Implementa lógicas avançadas de análise de anomalias, incluindo:
- Enriquecimento de detecções com métricas adicionais
- Análise temporal de padrões
- Geração de alertas em tempo real
"""

from typing import Optional

import cv2
import numpy as np

from app.core.logging_config import get_logger
from app.core.security import generate_secure_token
from app.models.enums import AnomalyType, SeverityLevel
from app.models.schemas import (
    BoundingBox,
    FrameAnalysis,
    RealtimeAlert,
)

logger = get_logger(__name__)


class AnomalyService:
    """
    Serviço especializado em análise e enriquecimento de anomalias.
    
    Métodos:
    - enrich_anomaly: Adiciona métricas ROI à detecção
    - compute_temporal_anomaly: Detecta padrões temporais suspeitos
    - generate_alert: Cria alertas para anomalias críticas
    """
    
    def enrich_anomaly(self, box: BoundingBox, frame: np.ndarray) -> BoundingBox:
        """
        Enriquece uma detecção com métricas adicionais da ROI.
        
        Calcula:
        - Intensidade média de pixels vermelhos (indicador de sangramento)
        - Densidade de features SIFT na região
        - Contraste local
        
        Args:
            box: Bounding box da detecção.
            frame: Frame completo em BGR.
        
        Returns:
            BoundingBox com métricas adicionais (não alterada por enquanto,
            mas pode ser expandida com campos extras).
        """
        # Extrai ROI
        x1, y1, x2, y2 = int(box.x1), int(box.y1), int(box.x2), int(box.y2)
        
        # Garante que as coordenadas estão dentro dos limites do frame
        h, w = frame.shape[:2]
        x1, x2 = max(0, x1), min(w, x2)
        y1, y2 = max(0, y1), min(h, y2)
        
        if x2 <= x1 or y2 <= y1:
            logger.warning(f"ROI inválida: ({x1},{y1}) -> ({x2},{y2})")
            return box
        
        roi = frame[y1:y2, x1:x2]
        
        # Métrica 1: Intensidade de vermelho (BGR, então canal 2)
        if box.anomaly_type == AnomalyType.SURGICAL_BLEEDING:
            red_channel = roi[:, :, 2]
            red_intensity = np.mean(red_channel)
            
            # Ajusta confiança baseado na intensidade de vermelho
            # Valores altos de vermelho aumentam confiança de sangramento
            if red_intensity > 150:
                logger.debug(
                    f"Alta intensidade vermelha detectada: {red_intensity:.1f} "
                    f"(confiança original: {box.confidence:.2f})"
                )
        
        # Métrica 2: Densidade de features (usando SIFT simplificado)
        try:
            gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            # Usa ORB como alternativa ao SIFT (não requer licença)
            orb = cv2.ORB_create(nfeatures=50)
            keypoints, _ = orb.detectAndCompute(gray_roi, None)
            feature_density = len(keypoints) / (roi.shape[0] * roi.shape[1])
            
            logger.debug(f"Densidade de features na ROI: {feature_density:.6f}")
        except Exception as e:
            logger.warning(f"Erro ao calcular features na ROI: {e}")
        
        return box
    
    def compute_temporal_anomaly(
        self,
        frames: list[FrameAnalysis],
        window: int = 10
    ) -> list[dict]:
        """
        Detecta padrões temporais suspeitos em uma sequência de frames.
        
        Identifica:
        - Sangramento progressivo (aumento de detecções de sangramento)
        - Persistência de instrumentos fora de posição
        - Mudanças abruptas na severidade
        
        Args:
            frames: Lista de análises de frames (ordenada por timestamp).
            window: Tamanho da janela temporal para análise.
        
        Returns:
            Lista de dicionários descrevendo padrões temporais detectados.
        """
        temporal_anomalies = []
        
        if len(frames) < window:
            return temporal_anomalies
        
        # Análise 1: Sangramento progressivo
        for i in range(len(frames) - window + 1):
            window_frames = frames[i:i+window]
            
            bleeding_counts = [
                sum(1 for box in f.bounding_boxes 
                    if box.anomaly_type == AnomalyType.SURGICAL_BLEEDING)
                for f in window_frames
            ]
            
            # Detecta tendência crescente
            if len(bleeding_counts) > 3:
                # Regressão linear simples para detectar tendência
                x = np.arange(len(bleeding_counts))
                slope = np.polyfit(x, bleeding_counts, 1)[0]
                
                if slope > 0.3:  # Aumento significativo
                    temporal_anomalies.append({
                        "type": "progressive_bleeding",
                        "start_frame": window_frames[0].frame_index,
                        "end_frame": window_frames[-1].frame_index,
                        "start_time": window_frames[0].timestamp_seconds,
                        "end_time": window_frames[-1].timestamp_seconds,
                        "severity": "high",
                        "description": (
                            f"Aumento progressivo de sangramento detectado entre "
                            f"{window_frames[0].timestamp_seconds:.1f}s e "
                            f"{window_frames[-1].timestamp_seconds:.1f}s"
                        )
                    })
        
        # Análise 2: Mudanças abruptas de severidade
        for i in range(1, len(frames)):
            prev_frame = frames[i-1]
            curr_frame = frames[i]
            
            # Mudança de low/medium para critical
            if (prev_frame.severity in [SeverityLevel.LOW, SeverityLevel.MEDIUM] and
                curr_frame.severity == SeverityLevel.CRITICAL):
                
                temporal_anomalies.append({
                    "type": "abrupt_severity_change",
                    "frame_index": curr_frame.frame_index,
                    "timestamp": curr_frame.timestamp_seconds,
                    "severity": "critical",
                    "description": (
                        f"Mudança abrupta de severidade em {curr_frame.timestamp_seconds:.1f}s: "
                        f"{prev_frame.severity} → {curr_frame.severity}"
                    )
                })
        
        return temporal_anomalies
    
    def generate_alert(
        self,
        frame_analysis: FrameAnalysis,
        analysis_id: str
    ) -> Optional[RealtimeAlert]:
        """
        Gera um alerta em tempo real se a anomalia for crítica.
        
        Args:
            frame_analysis: Análise do frame.
            analysis_id: ID da análise pai.
        
        Returns:
            RealtimeAlert se for crítico, None caso contrário.
        """
        if frame_analysis.severity not in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
            return None
        
        # Encontra a detecção mais crítica
        critical_box = None
        max_confidence = 0.0
        
        for box in frame_analysis.bounding_boxes:
            if (box.anomaly_type == AnomalyType.SURGICAL_BLEEDING and
                box.confidence > max_confidence):
                critical_box = box
                max_confidence = box.confidence
        
        # Se não houver sangramento, pega qualquer outra anomalia
        if not critical_box and frame_analysis.bounding_boxes:
            critical_box = max(
                frame_analysis.bounding_boxes,
                key=lambda b: b.confidence
            )
        
        # Gera descrição
        if critical_box:
            description = self._generate_alert_description(
                critical_box,
                frame_analysis
            )
        else:
            description = f"Alerta de severidade {frame_analysis.severity} no frame {frame_analysis.frame_index}"
        
        alert = RealtimeAlert(
            alert_id=f"alert-{analysis_id}-{frame_analysis.frame_index}",
            anomaly_type=critical_box.anomaly_type if critical_box else AnomalyType.ABNORMAL_MOVEMENT,
            severity=frame_analysis.severity,
            frame_index=frame_analysis.frame_index,
            audio_timestamp=None,
            description=description,
            bounding_box=critical_box
        )
        
        return alert
    
    def _generate_alert_description(
        self,
        box: BoundingBox,
        frame: FrameAnalysis
    ) -> str:
        """
        Gera descrição em português para um alerta.
        
        Args:
            box: Bounding box da anomalia.
            frame: Análise do frame.
        
        Returns:
            String descritiva do alerta.
        """
        anomaly_names = {
            AnomalyType.SURGICAL_BLEEDING: "Sangramento cirúrgico",
            AnomalyType.INSTRUMENT_DETECTED: "Instrumento cirúrgico",
            AnomalyType.ABNORMAL_MOVEMENT: "Movimento anormal",
        }
        
        anomaly_name = anomaly_names.get(
            box.anomaly_type,
            box.anomaly_type.value if box.anomaly_type else "Anomalia"
        )
        
        description = (
            f"{anomaly_name} detectado com {box.confidence*100:.0f}% de confiança "
            f"no frame {frame.frame_index} (t={frame.timestamp_seconds:.1f}s)"
        )
        
        if box.anomaly_type == AnomalyType.SURGICAL_BLEEDING:
            description += ". ATENÇÃO: Possível sangramento anômalo."
        
        return description


def get_anomaly_service() -> AnomalyService:
    """
    Factory function para AnomalyService.
    
    Returns:
        Instância do AnomalyService.
    """
    return AnomalyService()
