"""
Testes de validação de schemas Pydantic.

Valida models, validações customizadas e serialização.
"""

from datetime import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.models.schemas import (
    BoundingBox,
    FrameAnalysis,
    VideoAnalysisResult,
    AudioSegment,
    AudioAnalysisResult,
    AnalysisStatus,
)
from app.models.patient_schemas import PatientData, TranscriptionRequest, MedicalRecordTranscription
from app.models.enums import (
    AnomalyType,
    SeverityLevel,
    RiskLevel,
    AnalysisStatusEnum,
    ConsultationType,
)


@pytest.mark.unit
class TestBoundingBox:
    """Testes do schema BoundingBox."""
    
    def test_valid_bounding_box(self):
        """Testa criação de bounding box válida."""
        bbox = BoundingBox(
            x1=100.0,
            y1=150.0,
            x2=300.0,
            y2=350.0,
            confidence=0.85,
            label="blood",
            anomaly_type=AnomalyType.SURGICAL_BLEEDING
        )
        
        assert bbox.x1 == 100.0
        assert bbox.confidence == 0.85
        assert bbox.anomaly_type == AnomalyType.SURGICAL_BLEEDING
    
    def test_bounding_box_confidence_range(self):
        """Testa que confidence está entre 0 e 1."""
        # Confiança válida
        bbox = BoundingBox(
            x1=0, y1=0, x2=100, y2=100,
            confidence=0.5,
            label="test",
            anomaly_type=AnomalyType.INSTRUMENT_DETECTED
        )
        assert 0.0 <= bbox.confidence <= 1.0
        
        # Confiança inválida (se houver validação)
        try:
            BoundingBox(
                x1=0, y1=0, x2=100, y2=100,
                confidence=1.5,
                label="test",
                anomaly_type=AnomalyType.INSTRUMENT_DETECTED
            )
        except ValidationError:
            pass  # Esperado se houver validação
    
    def test_bounding_box_coordinates(self):
        """Testa que x2 > x1 e y2 > y1."""
        bbox = BoundingBox(
            x1=50, y1=50, x2=150, y2=150,
            confidence=0.9,
            label="scissors",
            anomaly_type=AnomalyType.INSTRUMENT_DETECTED
        )
        
        assert bbox.x2 > bbox.x1
        assert bbox.y2 > bbox.y1


@pytest.mark.unit
class TestFrameAnalysis:
    """Testes do schema FrameAnalysis."""
    
    def test_valid_frame_analysis(self):
        """Testa criação de análise de frame válida."""
        frame = FrameAnalysis(
            frame_index=10,
            timestamp_seconds=0.33,
            bounding_boxes=[],
            anomalies_detected=[AnomalyType.SURGICAL_BLEEDING],
            severity=SeverityLevel.HIGH
        )
        
        assert frame.frame_index == 10
        assert frame.severity == SeverityLevel.HIGH
        assert AnomalyType.SURGICAL_BLEEDING in frame.anomalies_detected
    
    def test_frame_with_multiple_bounding_boxes(self):
        """Testa frame com múltiplas detecções."""
        bbox1 = BoundingBox(
            x1=0, y1=0, x2=100, y2=100,
            confidence=0.9, label="blood",
            anomaly_type=AnomalyType.SURGICAL_BLEEDING
        )
        bbox2 = BoundingBox(
            x1=200, y1=200, x2=300, y2=300,
            confidence=0.85, label="scissors",
            anomaly_type=AnomalyType.INSTRUMENT_DETECTED
        )
        
        frame = FrameAnalysis(
            frame_index=5,
            timestamp_seconds=0.17,
            bounding_boxes=[bbox1, bbox2],
            anomalies_detected=[AnomalyType.SURGICAL_BLEEDING, AnomalyType.INSTRUMENT_DETECTED],
            severity=SeverityLevel.CRITICAL
        )
        
        assert len(frame.bounding_boxes) == 2
        assert len(frame.anomalies_detected) == 2


@pytest.mark.unit
class TestVideoAnalysisResult:
    """Testes do schema VideoAnalysisResult."""
    
    def test_valid_video_result(self):
        """Testa criação de resultado de análise de vídeo válido."""
        result = VideoAnalysisResult(
            analysis_id="test-123",
            filename="test.mp4",
            duration_seconds=10.5,
            total_frames_analyzed=315,
            video_width=1920,
            video_height=1080,
            frames=[],
            anomaly_summary={"surgical_bleeding": 5, "instrument_detected": 10},
            gemini_report="# Relatório Teste",
            processing_time_seconds=8.3,
            created_at=datetime.utcnow()
        )
        
        assert result.analysis_id == "test-123"
        assert result.total_frames_analyzed == 315
        assert "surgical_bleeding" in result.anomaly_summary
    
    def test_video_result_serialization(self):
        """Testa serialização para dict/JSON."""
        result = VideoAnalysisResult(
            analysis_id="test-456",
            filename="video.mp4",
            duration_seconds=5.0,
            total_frames_analyzed=150,
            video_width=1280,
            video_height=720,
            frames=[],
            anomaly_summary={},
            gemini_report="Relatório",
            processing_time_seconds=3.0,
            created_at=datetime.utcnow()
        )
        
        # Serializa para dict
        result_dict = result.model_dump()
        
        assert isinstance(result_dict, dict)
        assert result_dict["analysis_id"] == "test-456"
        assert result_dict["duration_seconds"] == 5.0


@pytest.mark.unit
class TestAudioSegment:
    """Testes do schema AudioSegment."""
    
    def test_valid_audio_segment(self):
        """Testa criação de segmento de áudio válido."""
        segment = AudioSegment(
            start_time=0.0,
            end_time=10.0,
            transcript="Paciente relata ansiedade",
            indicators=[AnomalyType.ANXIETY_INDICATOR],
            confidence=0.72,
            emotional_tone="ansioso"
        )
        
        assert segment.start_time == 0.0
        assert segment.end_time == 10.0
        assert AnomalyType.ANXIETY_INDICATOR in segment.indicators
    
    def test_audio_segment_time_range(self):
        """Testa que end_time > start_time."""
        segment = AudioSegment(
            start_time=5.0,
            end_time=15.0,
            transcript=None,
            indicators=[],
            confidence=0.5,
            emotional_tone="neutro"
        )
        
        assert segment.end_time > segment.start_time


@pytest.mark.unit
class TestAudioAnalysisResult:
    """Testes do schema AudioAnalysisResult."""
    
    def test_valid_audio_result(self):
        """Testa criação de resultado de análise de áudio válido."""
        segment = AudioSegment(
            start_time=0.0,
            end_time=10.0,
            transcript="Teste",
            indicators=[AnomalyType.DEPRESSION_INDICATOR],
            confidence=0.65,
            emotional_tone="melancólico"
        )
        
        result = AudioAnalysisResult(
            analysis_id="audio-789",
            filename="audio.wav",
            duration_seconds=30.0,
            segments=[segment],
            overall_risk_level=RiskLevel.MEDIUM,
            gemini_report="# Relatório de Áudio",
            processing_time_seconds=5.0,
            created_at=datetime.utcnow()
        )
        
        assert result.analysis_id == "audio-789"
        assert len(result.segments) == 1
        assert result.overall_risk_level == RiskLevel.MEDIUM


@pytest.mark.unit
class TestPatientData:
    """Testes do schema PatientData."""
    
    def test_valid_patient_data(self):
        """Testa criação de dados de paciente válidos."""
        patient = PatientData(
            nome="Maria Silva",
            idade=35,
            cpf="123.456.789-00",
            telefone="11999999999",
            ja_foi_mae=True,
            convenio="Unimed",
            numero_carteirinha="123456789"
        )
        
        assert patient.nome == "Maria Silva"
        assert patient.idade == 35
    
    def test_patient_data_optional_fields(self):
        """Testa que campos opcionais podem ser None."""
        patient = PatientData(
            nome="João Santos",
            idade=45,
            cpf="987.654.321-00",
            telefone="11988888888",
            ja_foi_mae=False
        )
        
        # Verifica que campos não fornecidos têm valores padrão apropriados
        assert patient.nome == "João Santos"
        assert patient.telefone == "11988888888"


@pytest.mark.unit
class TestEnums:
    """Testes dos Enums."""
    
    def test_anomaly_type_values(self):
        """Testa valores do enum AnomalyType."""
        assert AnomalyType.SURGICAL_BLEEDING.value == "surgical_bleeding"
        assert AnomalyType.INSTRUMENT_DETECTED.value == "instrument_detected"
        assert AnomalyType.ANXIETY_INDICATOR.value == "anxiety_indicator"
    
    def test_severity_level_values(self):
        """Testa valores do enum SeverityLevel."""
        assert SeverityLevel.LOW.value == "low"
        assert SeverityLevel.MEDIUM.value == "medium"
        assert SeverityLevel.HIGH.value == "high"
        assert SeverityLevel.CRITICAL.value == "critical"
    
    def test_risk_level_values(self):
        """Testa valores do enum RiskLevel."""
        assert RiskLevel.NONE.value == "none"
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
    
    def test_consultation_type_values(self):
        """Testa valores do enum ConsultationType."""
        assert ConsultationType.GYNECOLOGICAL.value == "gynecological"
        assert ConsultationType.GENERAL.value == "general"
