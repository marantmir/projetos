"""
Configuração de fixtures do pytest para testes.

Define fixtures reutilizáveis para mockar serviços, criar dados de teste
e configurar ambiente de testes.
"""

import asyncio
from pathlib import Path
from typing import Generator

import cv2
import numpy as np
import pytest
import soundfile as sf
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.models.enums import AnomalyType
from app.models.schemas import BoundingBox, VideoAnalysisResult, AudioAnalysisResult
from app.services.yolo_service import YOLOService
from app.services.gemini_service import GeminiService


@pytest.fixture(scope="session")
def event_loop():
    """Cria event loop para testes assíncronos."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client() -> TestClient:
    """Cliente de testes síncrono para FastAPI."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncClient:
    """Cliente de testes assíncrono para FastAPI."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_bounding_box() -> BoundingBox:
    """Bounding box de exemplo."""
    return BoundingBox(
        x1=100.0,
        y1=150.0,
        x2=300.0,
        y2=350.0,
        confidence=0.87,
        label="blood",
        anomaly_type=AnomalyType.SURGICAL_BLEEDING
    )


@pytest.fixture
def mock_yolo_detections() -> list[BoundingBox]:
    """Lista de detecções YOLOv8 mockadas."""
    return [
        BoundingBox(
            x1=50.0, y1=50.0, x2=150.0, y2=150.0,
            confidence=0.92,
            label="scissors",
            anomaly_type=AnomalyType.INSTRUMENT_DETECTED
        ),
        BoundingBox(
            x1=200.0, y1=100.0, x2=350.0, y2=250.0,
            confidence=0.78,
            label="blood",
            anomaly_type=AnomalyType.SURGICAL_BLEEDING
        )
    ]


@pytest.fixture
def sample_video_path(tmp_path: Path) -> str:
    """
    Cria um vídeo sintético de teste.
    
    Vídeo simples com círculo vermelho em movimento.
    """
    video_path = tmp_path / "test_video.mp4"
    
    # Parâmetros do vídeo
    width, height = 640, 480
    fps = 30.0
    duration = 2  # segundos
    total_frames = int(fps * duration)
    
    # Codec e writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(video_path), fourcc, fps, (width, height))
    
    try:
        for i in range(total_frames):
            # Cria frame preto
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Desenha círculo vermelho em movimento
            x = int((i / total_frames) * width)
            y = height // 2
            cv2.circle(frame, (x, y), 30, (0, 0, 255), -1)
            
            out.write(frame)
    finally:
        out.release()
    
    return str(video_path)


@pytest.fixture
def sample_audio_path(tmp_path: Path) -> str:
    """
    Cria um arquivo de áudio sintético de teste.
    
    Áudio com tom puro de 440Hz (Lá4) por 3 segundos.
    """
    audio_path = tmp_path / "test_audio.wav"
    
    # Gera sinal de áudio
    sr = 22050  # Sample rate
    duration = 3  # segundos
    frequency = 440  # Hz (Lá4)
    
    t = np.linspace(0, duration, int(sr * duration))
    audio_signal = 0.5 * np.sin(2 * np.pi * frequency * t)
    
    # Salva como WAV
    sf.write(audio_path, audio_signal, sr)
    
    return str(audio_path)


@pytest.fixture
def mock_yolo_service(monkeypatch, mock_yolo_detections):
    """Mocka YOLOService para retornar detecções fixas."""
    
    class MockYOLOService:
        def __init__(self, *args, **kwargs):
            self.is_custom_model = False
        
        def detect_frame(self, frame):
            return mock_yolo_detections
        
        def classify_severity(self, bounding_boxes):
            from app.models.enums import SeverityLevel
            if any(b.anomaly_type == AnomalyType.SURGICAL_BLEEDING for b in bounding_boxes):
                return SeverityLevel.CRITICAL
            return SeverityLevel.MEDIUM
        
        def get_model_info(self):
            return {
                "model_type": "mock",
                "num_classes": 10,
                "class_names": ["mock_class"]
            }
    
    monkeypatch.setattr("app.services.yolo_service.YOLOService", MockYOLOService)
    
    return MockYOLOService


@pytest.fixture
def mock_gemini_service(monkeypatch):
    """Mocka GeminiService para retornar relatório fixo."""
    
    class MockGeminiService:
        async def generate_video_report(self, analysis_result):
            return "# Relatório de Teste\n\nEste é um relatório mockado para testes."
        
        async def generate_audio_report(self, analysis_result):
            return "# Relatório de Áudio\n\nRelatório mockado para testes."
    
    monkeypatch.setattr("app.services.gemini_service.GeminiService", MockGeminiService)
    
    return MockGeminiService


@pytest.fixture
def sample_video_analysis_result() -> VideoAnalysisResult:
    """Resultado de análise de vídeo de exemplo."""
    from datetime import datetime
    from app.models.schemas import FrameAnalysis
    from app.models.enums import SeverityLevel
    
    return VideoAnalysisResult(
        analysis_id="test-video-123",
        filename="test_video.mp4",
        duration_seconds=10.0,
        total_frames_analyzed=10,
        frames=[
            FrameAnalysis(
                frame_index=0,
                timestamp_seconds=0.0,
                bounding_boxes=[],
                anomalies_detected=[],
                severity=SeverityLevel.LOW
            )
        ],
        anomaly_summary={"surgical_bleeding": 2},
        gemini_report="Relatório de teste",
        processing_time_seconds=5.0,
        created_at=datetime.utcnow()
    )


@pytest.fixture
def sample_audio_analysis_result() -> AudioAnalysisResult:
    """Resultado de análise de áudio de exemplo."""
    from datetime import datetime
    from app.models.schemas import AudioSegment
    from app.models.enums import RiskLevel
    
    return AudioAnalysisResult(
        analysis_id="test-audio-456",
        filename="test_audio.wav",
        duration_seconds=30.0,
        segments=[
            AudioSegment(
                start_time=0.0,
                end_time=10.0,
                transcript="Teste de transcrição",
                indicators=[AnomalyType.ANXIETY_INDICATOR],
                confidence=0.65,
                emotional_tone="ansioso"
            )
        ],
        overall_risk_level=RiskLevel.MEDIUM,
        gemini_report="Relatório de áudio de teste",
        processing_time_seconds=3.0,
        created_at=datetime.utcnow()
    )
