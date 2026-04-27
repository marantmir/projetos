"""
Serviço de detecção de objetos usando YOLOv8 para análise de vídeos cirúrgicos.

Implementa a lógica de detecção de instrumentos ginecológicos, sangramento
e anomalias em frames de vídeo usando o modelo YOLOv8 customizado ou genérico.
"""

import logging
from pathlib import Path
from typing import Optional

import numpy as np
from ultralytics import YOLO

from app.core.config import settings
from app.core.logging_config import get_logger
from app.models.enums import AnomalyType, SeverityLevel
from app.models.schemas import BoundingBox

logger = get_logger(__name__)


# Mapeamento de classes YOLOv8 para tipos de anomalia médica
# NOTA: Este mapeamento deve ser atualizado quando o modelo especializado for treinado
# com o dataset ginecológico rotulado. Por enquanto, usamos aproximações com COCO classes.
YOLO_CLASS_TO_ANOMALY = {
    "scissors": AnomalyType.INSTRUMENT_DETECTED,
    "knife": AnomalyType.INSTRUMENT_DETECTED,
    "forceps": AnomalyType.INSTRUMENT_DETECTED,
    "retractor": AnomalyType.INSTRUMENT_DETECTED,
    "blood": AnomalyType.SURGICAL_BLEEDING,
    "person": AnomalyType.ABNORMAL_MOVEMENT,  # Movimento inesperado no campo cirúrgico
    # Quando o modelo customizado estiver disponível, incluir:
    # "speculum", "tenaculum", "curette", "uterine_manipulator", etc.
}


class YOLOService:
    """
    Serviço de visão computacional para detecção de anomalias em vídeos cirúrgicos.
    
    Utiliza YOLOv8 para detecção em tempo real de:
    - Instrumentos ginecológicos
    - Sangramento anômalo
    - Movimentos ou objetos inesperados
    
    Attributes:
        model: Instância do modelo YOLO carregada.
        model_path: Caminho do arquivo de weights usado.
        is_custom_model: Flag indicando se é o modelo customizado ou genérico.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Inicializa o serviço YOLOv8.
        
        Tenta carregar o modelo customizado do path configurado. Se não existir,
        faz fallback automático para o modelo genérico yolov8n.pt.
        
        Args:
            model_path: Caminho customizado do modelo (opcional, usa settings por padrão).
        """
        self.model_path = model_path or settings.YOLO_MODEL_PATH
        self.is_custom_model = False
        self.model: Optional[YOLO] = None
        
        self._load_model()
    
    def _load_model(self) -> None:
        """
        Carrega o modelo YOLOv8 com fallback automático.
        
        Prioridade:
        1. Modelo customizado em YOLO_MODEL_PATH
        2. Modelo genérico yolov8n.pt (download automático)
        """
        custom_model_path = Path(self.model_path)
        
        try:
            if custom_model_path.exists():
                logger.info(f"Carregando modelo YOLOv8 customizado: {self.model_path}")
                self.model = YOLO(str(custom_model_path))
                self.is_custom_model = True
                logger.info(
                    f"Modelo customizado carregado com sucesso. Classes: {len(self.model.names)}"
                )
            else:
                logger.warning(
                    f"Modelo customizado não encontrado em {self.model_path}. "
                    "Usando modelo genérico yolov8n.pt como fallback."
                )
                self.model = YOLO("yolov8n.pt")  # Download automático se necessário
                self.is_custom_model = False
                logger.info(
                    "Modelo genérico YOLOv8n carregado. "
                    "AVISO: Para melhores resultados em contexto médico, "
                    "treine um modelo customizado com dataset ginecológico."
                )
        except Exception as e:
            logger.error(f"Erro ao carregar modelo YOLOv8: {e}")
            raise RuntimeError(f"Falha ao inicializar YOLOService: {e}")
    
    def detect_frame(self, frame: np.ndarray) -> list[BoundingBox]:
        """
        Detecta objetos e anomalias em um único frame.
        
        Args:
            frame: Frame de vídeo como array NumPy (H, W, C) em BGR.
        
        Returns:
            Lista de bounding boxes detectadas com confiança acima do threshold.
        """
        if self.model is None:
            raise RuntimeError("Modelo YOLOv8 não inicializado")
        
        # Executa inferência
        results = self.model(frame, verbose=False)
        
        bounding_boxes = []
        
        # Processa detecções
        for result in results:
            boxes = result.boxes
            for i in range(len(boxes)):
                confidence = float(boxes.conf[i])
                
                # Filtra por threshold de confiança
                if confidence < settings.ANOMALY_CONFIDENCE_THRESHOLD:
                    continue
                
                # Extrai coordenadas da bounding box (xyxy format)
                x1, y1, x2, y2 = boxes.xyxy[i].tolist()
                
                # Obtém o label da classe
                class_id = int(boxes.cls[i])
                label = self.model.names[class_id]
                
                # Mapeia para tipo de anomalia
                anomaly_type = self._map_label_to_anomaly(label)
                
                bbox = BoundingBox(
                    x1=x1,
                    y1=y1,
                    x2=x2,
                    y2=y2,
                    confidence=confidence,
                    label=label,
                    anomaly_type=anomaly_type
                )
                
                bounding_boxes.append(bbox)
        
        return bounding_boxes
    
    def _map_label_to_anomaly(self, label: str) -> Optional[AnomalyType]:
        """
        Mapeia um label YOLOv8 para um tipo de anomalia médica.
        
        Args:
            label: Nome da classe detectada pelo YOLO.
        
        Returns:
            Tipo de anomalia correspondente ou None se não mapeado.
        """
        return YOLO_CLASS_TO_ANOMALY.get(label.lower())
    
    def classify_severity(self, bounding_boxes: list[BoundingBox]) -> SeverityLevel:
        """
        Classifica a severidade de um frame baseado nas detecções.
        
        Regras de severidade:
        - CRITICAL: Sangramento detectado com alta confiança (>0.7)
        - HIGH: Múltiplos instrumentos ou anomalias de movimento
        - MEDIUM: Detecções únicas de instrumentos
        - LOW: Confiança abaixo do threshold ou nenhuma anomalia crítica
        
        Args:
            bounding_boxes: Lista de detecções no frame.
        
        Returns:
            Nível de severidade calculado.
        """
        if not bounding_boxes:
            return SeverityLevel.LOW
        
        # Contadores por tipo de anomalia
        bleeding_count = 0
        instrument_count = 0
        abnormal_movement_count = 0
        max_bleeding_confidence = 0.0
        
        for bbox in bounding_boxes:
            if bbox.anomaly_type == AnomalyType.SURGICAL_BLEEDING:
                bleeding_count += 1
                max_bleeding_confidence = max(max_bleeding_confidence, bbox.confidence)
            elif bbox.anomaly_type == AnomalyType.INSTRUMENT_DETECTED:
                instrument_count += 1
            elif bbox.anomaly_type == AnomalyType.ABNORMAL_MOVEMENT:
                abnormal_movement_count += 1
        
        # Regra 1: Sangramento com alta confiança é sempre crítico
        if bleeding_count > 0 and max_bleeding_confidence > 0.7:
            return SeverityLevel.CRITICAL
        
        # Regra 2: Sangramento ou múltiplas anomalias de movimento
        if bleeding_count > 0 or abnormal_movement_count >= 2:
            return SeverityLevel.HIGH
        
        # Regra 3: Múltiplos instrumentos podem indicar momento crítico da cirurgia
        if instrument_count >= 3:
            return SeverityLevel.HIGH
        
        # Regra 4: Detecções únicas de instrumentos são normais
        if instrument_count > 0 or abnormal_movement_count == 1:
            return SeverityLevel.MEDIUM
        
        # Default: baixa severidade
        return SeverityLevel.LOW
    
    def get_model_info(self) -> dict:
        """
        Retorna metadados do modelo carregado.
        
        Returns:
            Dicionário com informações do modelo:
            - model_type: Tipo do modelo (custom/generic)
            - model_path: Caminho do arquivo de weights
            - num_classes: Número de classes que o modelo detecta
            - class_names: Lista de nomes das classes
            - input_shape: Shape de entrada esperada
        """
        if self.model is None:
            return {"error": "Modelo não inicializado"}
        
        return {
            "model_type": "custom" if self.is_custom_model else "generic",
            "model_path": self.model_path,
            "num_classes": len(self.model.names),
            "class_names": list(self.model.names.values()),
            "input_shape": "640x640" if hasattr(self.model, "imgsz") else "unknown",
            "confidence_threshold": settings.ANOMALY_CONFIDENCE_THRESHOLD,
        }


# Singleton global para evitar recarregar o modelo em cada requisição
_yolo_service_instance: Optional[YOLOService] = None


def get_yolo_service() -> YOLOService:
    """
    Obtém a instância singleton do YOLOService.
    
    Returns:
        Instância inicializada do YOLOService.
    """
    global _yolo_service_instance
    if _yolo_service_instance is None:
        _yolo_service_instance = YOLOService()
    return _yolo_service_instance
