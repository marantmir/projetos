"""
Serviço de orquestração para análise completa de vídeos cirúrgicos.

Coordena o pipeline end-to-end: extração de frames, detecção YOLOv8,
classificação de anomalias e geração de relatório com Gemini.
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Generator, Optional

import cv2
import numpy as np

from app.core.config import settings
from app.core.logging_config import get_logger
from app.core.security import generate_analysis_id
from app.models.enums import AnomalyType, SeverityLevel
from app.models.schemas import (
    VideoAnalysisResult,
    FrameAnalysis,
    BoundingBox,
)
from app.services.yolo_service import YOLOService
from app.services.gemini_service import GeminiService

logger = get_logger(__name__)


class VideoService:
    """
    Serviço de análise de vídeos cirúrgicos ginecológicos.
    
    Pipeline:
    1. Extração de frames com sampling adaptativo
    2. Detecção de anomalias com YOLOv8
    3. Classificação de severidade
    4. Geração de relatório com Gemini
    5. Notificações de progresso via callback
    
    Attributes:
        yolo_service: Serviço de detecção de objetos.
        gemini_service: Serviço de geração de relatórios.
    """
    
    def __init__(
        self,
        yolo_service: YOLOService,
        gemini_service: GeminiService
    ):
        """
        Inicializa o serviço de análise de vídeo.
        
        Args:
            yolo_service: Instância do YOLOService.
            gemini_service: Instância do GeminiService.
        """
        self.yolo_service = yolo_service
        self.gemini_service = gemini_service
    
    async def process_video(
        self,
        file_path: str,
        analysis_id: Optional[str] = None,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> VideoAnalysisResult:
        """
        Processa um vídeo cirúrgico completo.
        
        Args:
            file_path: Caminho do arquivo de vídeo.
            analysis_id: ID único da análise (gerado automaticamente se None).
            progress_callback: Função chamada com (percent, stage) para updates.
        
        Returns:
            Resultado completo da análise com frames, anomalias e relatório.
        """
        start_time = time.time()
        
        if analysis_id is None:
            analysis_id = generate_analysis_id()
        
        logger.info(f"Iniciando análise de vídeo: {file_path} (ID: {analysis_id})")
        
        video_path = Path(file_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Arquivo de vídeo não encontrado: {file_path}")
        
        # Obtém metadados do vídeo
        duration, total_frames, fps, video_width, video_height = self._get_video_metadata(file_path)
        logger.info(
            f"Vídeo: {duration:.1f}s, {total_frames} frames totais, {fps:.1f} FPS, {video_width}x{video_height}"
        )
        
        # Determina taxa de amostragem baseada na duração
        sample_rate = self._calculate_sample_rate(duration)
        logger.info(f"Taxa de amostragem: 1 frame a cada {sample_rate}")
        
        if progress_callback:
            progress_callback(0, "Iniciando extração de frames...")
        
        # Processa frames
        frames_analyzed = []
        frame_count = 0
        total_to_process = total_frames // sample_rate
        
        for frame_index, timestamp, frame in self._extract_frames(file_path, sample_rate):
            frame_count += 1
            
            # Detecção com YOLO
            bounding_boxes = self.yolo_service.detect_frame(frame)
            
            # Extrai tipos de anomalias únicas
            anomalies_detected = list(set(
                bbox.anomaly_type 
                for bbox in bounding_boxes 
                if bbox.anomaly_type is not None
            ))
            
            # Classifica severidade do frame
            severity = self.yolo_service.classify_severity(bounding_boxes)
            
            # Cria análise do frame
            frame_analysis = FrameAnalysis(
                frame_index=frame_index,
                timestamp_seconds=timestamp,
                bounding_boxes=bounding_boxes,
                anomalies_detected=anomalies_detected,
                severity=severity
            )
            
            frames_analyzed.append(frame_analysis)
            
            # Callback de progresso a cada 10% ou quando crítico
            if progress_callback:
                should_report_progress = (frame_count % max(1, total_to_process // 10) == 0)
                is_critical = severity == SeverityLevel.CRITICAL
                
                if should_report_progress or is_critical:
                    progress_percent = (frame_count / total_to_process) * 80  # 80% para análise
                    stage = f"Analisando frames ({frame_count}/{total_to_process})"
                    if is_critical:
                        stage += f" - ALERTA CRÍTICO em {timestamp:.1f}s"
                    
                    # Passa frame_analysis se for crítico para gerar alerta
                    if is_critical:
                        progress_callback(progress_percent, stage, frame_analysis)
                    else:
                        progress_callback(progress_percent, stage)
        
        logger.info(f"Processados {len(frames_analyzed)} frames")
        
        if progress_callback:
            progress_callback(80, "Gerando sumário de anomalias...")
        
        # Computa sumário de anomalias
        anomaly_summary = self._compute_anomaly_summary(frames_analyzed)
        
        if progress_callback:
            progress_callback(85, "Gerando relatório com Gemini...")
        
        # Cria resultado temporário para gerar relatório
        temp_result = VideoAnalysisResult(
            analysis_id=analysis_id,
            filename=video_path.name,
            duration_seconds=duration,
            video_width=video_width,
            video_height=video_height,
            total_frames_analyzed=len(frames_analyzed),
            frames=frames_analyzed,
            anomaly_summary=anomaly_summary,
            gemini_report="",  # Será preenchido
            processing_time_seconds=0.0,
            created_at=datetime.utcnow()
        )
        
        # Gera relatório com Gemini
        try:
            logger.info(f"🤖 Iniciando geração de relatório Gemini para análise {analysis_id}")
            logger.info(f"📊 Frames analisados: {len(frames_analyzed)}, Anomalias: {sum(anomaly_summary.values())}")
            gemini_report = await self.gemini_service.generate_video_report(temp_result)
            logger.info(f"✅ Relatório Gemini gerado com sucesso: {len(gemini_report)} caracteres")
        except Exception as e:
            logger.error(f"❌ FALHA ao gerar relatório Gemini: {type(e).__name__}: {e}", exc_info=True)
            gemini_report = f"❌ Relatório indisponível - Erro: {type(e).__name__}: {str(e)}"
        
        if progress_callback:
            progress_callback(95, "Finalizando análise...")
        
        processing_time = time.time() - start_time
        
        # Resultado final
        result = VideoAnalysisResult(
            analysis_id=analysis_id,
            filename=video_path.name,
            duration_seconds=duration,
            video_width=video_width,
            video_height=video_height,
            total_frames_analyzed=len(frames_analyzed),
            frames=frames_analyzed,
            anomaly_summary=anomaly_summary,
            gemini_report=gemini_report,
            processing_time_seconds=processing_time,
            created_at=datetime.utcnow()
        )
        
        if progress_callback:
            progress_callback(100, "Análise concluída")
        
        logger.info(
            f"Análise concluída: {analysis_id} em {processing_time:.2f}s "
            f"({len(frames_analyzed)} frames, {sum(anomaly_summary.values())} anomalias)"
        )
        
        return result
    
    def _get_video_metadata(self, video_path: str) -> tuple[float, int, float, int, int]:
        """
        Extrai metadados do vídeo.
        
        Args:
            video_path: Caminho do arquivo de vídeo.
        
        Returns:
            Tupla (duração_segundos, total_frames, fps, width, height).
        """
        cap = cv2.VideoCapture(video_path)
        
        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = total_frames / fps if fps > 0 else 0
            
            return duration, total_frames, fps, width, height
        finally:
            cap.release()
    
    def _calculate_sample_rate(self, duration: float) -> int:
        """
        Calcula a taxa de amostragem adaptativa baseada na duração do vídeo.
        
        Vídeos curtos (<60s) usam amostragem mais densa para capturar mais detalhes.
        
        Args:
            duration: Duração do vídeo em segundos.
        
        Returns:
            Taxa de amostragem (processar 1 frame a cada N).
        """
        if duration < settings.VIDEO_SHORT_DURATION_THRESHOLD:
            return settings.VIDEO_SHORT_SAMPLE_RATE
        return settings.VIDEO_FRAME_SAMPLE_RATE
    
    def _extract_frames(
        self,
        video_path: str,
        sample_rate: int
    ) -> Generator[tuple[int, float, np.ndarray], None, None]:
        """
        Gerador que extrai frames do vídeo com taxa de amostragem.
        
        Usa gerador para não sobrecarregar memória com vídeos longos.
        
        Args:
            video_path: Caminho do arquivo de vídeo.
            sample_rate: Processar 1 frame a cada N frames.
        
        Yields:
            Tuplas (frame_index, timestamp_seconds, frame_array).
        """
        cap = cv2.VideoCapture(video_path)
        
        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_index = 0
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # Amostragem: processa apenas frames específicos
                if frame_index % sample_rate == 0:
                    timestamp = frame_index / fps if fps > 0 else 0
                    yield frame_index, timestamp, frame
                
                frame_index += 1
        
        finally:
            cap.release()
    
    def _compute_anomaly_summary(self, frames: list[FrameAnalysis]) -> dict[str, int]:
        """
        Contabiliza anomalias por tipo em todos os frames.
        
        Args:
            frames: Lista de análises de frames.
        
        Returns:
            Dicionário {tipo_anomalia: contagem}.
        """
        summary: dict[str, int] = {}
        
        for frame in frames:
            for anomaly in frame.anomalies_detected:
                anomaly_key = anomaly.value  # Usa o valor do enum
                summary[anomaly_key] = summary.get(anomaly_key, 0) + 1
        
        return summary


def get_video_service() -> VideoService:
    """
    Factory function para criar VideoService com dependências injetadas.
    
    Returns:
        Instância configurada do VideoService.
    """
    from app.services.yolo_service import get_yolo_service
    from app.services.gemini_service import get_gemini_service
    
    return VideoService(
        yolo_service=get_yolo_service(),
        gemini_service=get_gemini_service()
    )
