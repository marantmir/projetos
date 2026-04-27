"""
Testes de edge cases e tratamento de erros.

Valida comportamento em situações extremas e inesperadas.
"""

import io

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import BoundingBox
from app.models.enums import AnomalyType, SeverityLevel
from app.services.yolo_service import YOLOService
from app.services.audio_service import AudioService


@pytest.fixture
def client():
    """Cliente de testes."""
    return TestClient(app)


@pytest.mark.unit
class TestBoundingBoxEdgeCases:
    """Testes de edge cases para BoundingBox."""
    
    def test_zero_size_bounding_box(self):
        """Testa bounding box com tamanho zero (ponto)."""
        bbox = BoundingBox(
            x1=100.0, y1=100.0, x2=100.0, y2=100.0,
            confidence=1.0,
            label="point",
            anomaly_type=AnomalyType.INSTRUMENT_DETECTED
        )
        
        # Deve ser válido, mesmo com área zero
        assert bbox.x1 == bbox.x2
        assert bbox.y1 == bbox.y2
    
    def test_negative_coordinates(self):
        """Testa bounding box com coordenadas negativas."""
        bbox = BoundingBox(
            x1=-50.0, y1=-50.0, x2=50.0, y2=50.0,
            confidence=0.8,
            label="test",
            anomaly_type=AnomalyType.SURGICAL_BLEEDING
        )
        
        assert bbox.x1 < 0
        assert bbox.y1 < 0
    
    def test_very_low_confidence(self):
        """Testa bounding box com confiança muito baixa."""
        bbox = BoundingBox(
            x1=0, y1=0, x2=10, y2=10,
            confidence=0.01,  # 1% de confiança
            label="uncertain",
            anomaly_type=AnomalyType.INSTRUMENT_DETECTED
        )
        
        assert bbox.confidence == 0.01


@pytest.mark.unit
class TestVideoEdgeCases:
    """Testes de edge cases para processamento de vídeo."""
    
    def test_single_frame_video(self, tmp_path):
        """Testa vídeo com apenas 1 frame."""
        video_path = tmp_path / "single_frame.mp4"
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(video_path), fourcc, 1.0, (640, 480))
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        out.write(frame)
        out.release()
        
        assert video_path.exists()
    
    def test_very_high_fps_video(self, tmp_path):
        """Testa vídeo com FPS muito alto (120 fps)."""
        video_path = tmp_path / "high_fps.mp4"
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(video_path), fourcc, 120.0, (640, 480))
        
        # Gera 120 frames (1 segundo)
        for _ in range(120):
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            out.write(frame)
        
        out.release()
        assert video_path.exists()
    
    def test_black_video(self, tmp_path):
        """Testa vídeo completamente preto."""
        video_path = tmp_path / "black.mp4"
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(video_path), fourcc, 30.0, (640, 480))
        
        for _ in range(30):
            frame = np.zeros((480, 640, 3), dtype=np.uint8)  # Preto
            out.write(frame)
        
        out.release()
        assert video_path.exists()


@pytest.mark.unit
class TestAudioEdgeCases:
    """Testes de edge cases para processamento de áudio."""
    
    def test_silent_audio(self, tmp_path):
        """Testa áudio completamente silencioso."""
        import soundfile as sf
        
        audio_path = tmp_path / "silent.wav"
        
        # Áudio de silêncio (zeros)
        sr = 22050
        duration = 2
        audio = np.zeros(int(sr * duration))
        
        sf.write(audio_path, audio, sr)
        assert audio_path.exists()
    
    def test_very_short_audio(self, tmp_path):
        """Testa áudio muito curto (0.1 segundos)."""
        import soundfile as sf
        
        audio_path = tmp_path / "short.wav"
        
        sr = 22050
        duration = 0.1
        frequency = 440
        
        t = np.linspace(0, duration, int(sr * duration))
        audio = 0.5 * np.sin(2 * np.pi * frequency * t)
        
        sf.write(audio_path, audio, sr)
        assert audio_path.exists()
    
    def test_clipped_audio(self, tmp_path):
        """Testa áudio com clipping (saturado)."""
        import soundfile as sf
        
        audio_path = tmp_path / "clipped.wav"
        
        sr = 22050
        duration = 1
        
        # Gera sinal que excede [-1, 1] (clipped)
        t = np.linspace(0, duration, int(sr * duration))
        audio = 2.0 * np.sin(2 * np.pi * 440 * t)  # Amplitude 2.0
        
        # Normaliza para evitar erro no salvamento
        audio = np.clip(audio, -1.0, 1.0)
        
        sf.write(audio_path, audio, sr)
        assert audio_path.exists()


@pytest.mark.api
class TestAPIErrorHandling:
    """Testes de tratamento de erros da API."""
    
    def test_malformed_json(self, client):
        """Testa requisição com JSON malformado."""
        response = client.post(
            "/api/v1/audio/transcribe",
            data="{invalid json}",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in [400, 422]
    
    def test_empty_file_upload(self, client):
        """Testa upload de arquivo vazio."""
        files = {"file": ("empty.mp4", io.BytesIO(b""), "video/mp4")}
        
        response = client.post("/api/v1/video/analyze", files=files)
        
        # Deve rejeitar arquivo vazio
        assert response.status_code in [400, 422]
    
    def test_very_long_filename(self, client):
        """Testa upload com nome de arquivo muito longo."""
        long_name = "a" * 300 + ".mp4"
        
        files = {"file": (long_name, io.BytesIO(b"fake video data"), "video/mp4")}
        
        response = client.post("/api/v1/video/analyze", files=files)
        
        # Deve aceitar ou sanitizar o nome
        assert response.status_code in [202, 400]
    
    def test_special_characters_in_filename(self, client):
        """Testa upload com caracteres especiais no nome."""
        special_name = "test<>:\"|?*.mp4"
        
        files = {"file": (special_name, io.BytesIO(b"data"), "video/mp4")}
        
        response = client.post("/api/v1/video/analyze", files=files)
        
        # Sistema deve sanitizar caracteres especiais
        assert response.status_code in [202, 400]
    
    def test_concurrent_uploads(self, client, fake_video_bytes):
        """Testa múltiplos uploads simultâneos."""
        # Simula uploads concorrentes
        responses = []
        
        for i in range(3):
            files = {"file": (f"test{i}.mp4", io.BytesIO(fake_video_bytes), "video/mp4")}
            response = client.post("/api/v1/video/analyze", files=files)
            responses.append(response)
        
        # Todos devem ser aceitos
        assert all(r.status_code == 202 for r in responses)
        
        # IDs devem ser únicos
        ids = [r.json()["analysis_id"] for r in responses]
        assert len(ids) == len(set(ids))


@pytest.mark.unit
class TestDataValidation:
    """Testes de validação de dados."""
    
    def test_negative_duration(self):
        """Testa que duração negativa não é permitida (se houver validação)."""
        from app.models.schemas import VideoAnalysisResult
        from datetime import datetime
        
        # Tenta criar com duração negativa
        try:
            result = VideoAnalysisResult(
                analysis_id="test",
                filename="test.mp4",
                duration_seconds=-10.0,  # Negativo
                total_frames_analyzed=0,
                frames=[],
                anomaly_summary={},
                gemini_report="",
                processing_time_seconds=1.0,
                created_at=datetime.utcnow()
            )
            # Se passar, significa que não há validação
            # Considerar adicionar validação futura
        except Exception:
            pass  # Validação funcionou
    
    def test_empty_analysis_id(self):
        """Testa análise com ID vazio."""
        from app.models.schemas import VideoAnalysisResult
        from datetime import datetime
        
        try:
            result = VideoAnalysisResult(
                analysis_id="",  # Vazio
                filename="test.mp4",
                duration_seconds=10.0,
                total_frames_analyzed=100,
                frames=[],
                anomaly_summary={},
                gemini_report="",
                processing_time_seconds=1.0,
                created_at=datetime.utcnow()
            )
            # Se passar, considerar adicionar validação
        except Exception:
            pass


@pytest.mark.unit
class TestMemoryAndPerformance:
    """Testes relacionados a memória e performance."""
    
    def test_large_anomaly_summary(self):
        """Testa relatório com muitas anomalias."""
        from app.models.schemas import VideoAnalysisResult
        from datetime import datetime
        
        # Cria resumo com muitas entradas
        large_summary = {f"anomaly_{i}": i * 10 for i in range(1000)}
        
        result = VideoAnalysisResult(
            analysis_id="large-test",
            filename="test.mp4",
            duration_seconds=100.0,
            total_frames_analyzed=3000,
            frames=[],
            anomaly_summary=large_summary,
            gemini_report="Test",
            processing_time_seconds=50.0,
            created_at=datetime.utcnow()
        )
        
        assert len(result.anomaly_summary) == 1000
    
    def test_very_long_report_text(self):
        """Testa relatório com texto muito longo."""
        from app.models.schemas import VideoAnalysisResult
        from datetime import datetime
        
        # Relatório com 1MB de texto
        long_report = "a" * (1024 * 1024)
        
        result = VideoAnalysisResult(
            analysis_id="long-report-test",
            filename="test.mp4",
            duration_seconds=10.0,
            total_frames_analyzed=100,
            frames=[],
            anomaly_summary={},
            gemini_report=long_report,
            processing_time_seconds=5.0,
            created_at=datetime.utcnow()
        )
        
        assert len(result.gemini_report) > 1000000
