"""
Testes do AudioService.

Valida extração de features, classificação de indicadores e geração de relatório.
"""

import pytest
import numpy as np

from app.services.audio_service import AudioService
from app.models.enums import AnomalyType, RiskLevel


@pytest.mark.asyncio
async def test_process_audio_returns_result(
    sample_audio_path,
    mock_gemini_service
):
    """Testa que process_audio retorna AudioAnalysisResult válido."""
    from app.services import get_gemini_service
    
    audio_service = AudioService(gemini_service=get_gemini_service())
    
    result = await audio_service.process_audio(
        file_path=sample_audio_path,
        analysis_id="test-audio-789"
    )
    
    assert result.analysis_id == "test-audio-789"
    assert result.duration_seconds > 0
    assert len(result.segments) > 0
    assert result.overall_risk_level in [RiskLevel.NONE, RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH]
    assert result.gemini_report != ""


def test_classify_segment_depression():
    """Testa classificação de indicador de depressão."""
    from app.services import get_audio_service, get_gemini_service
    
    audio_service = AudioService(gemini_service=get_gemini_service())
    
    # Features simulando depressão: pitch baixo, energia baixa, alta taxa de silêncio
    features = {
        "pitch_mean": 140.0,  # Baixo
        "pitch_std": 10.0,
        "rms_mean": 0.015,    # Baixa energia
        "rms_std": 0.005,
        "silence_rate": 0.45,  # Alta taxa de silêncio
        "zcr_std": 0.02
    }
    
    indicators, confidence = audio_service._classify_segment(features, transcript=None)
    
    assert AnomalyType.DEPRESSION_INDICATOR in indicators
    assert confidence > 0.0


def test_compute_overall_risk():
    """Testa cálculo de risco geral."""
    from app.services import get_audio_service, get_gemini_service
    from app.models.schemas import AudioSegment
    
    audio_service = AudioService(gemini_service=get_gemini_service())
    
    # Segmentos com indicadores de depressão
    segments = [
        AudioSegment(
            start_time=0.0,
            end_time=10.0,
            transcript=None,
            indicators=[AnomalyType.DEPRESSION_INDICATOR],
            confidence=0.7,
            emotional_tone="melancólico"
        ),
        AudioSegment(
            start_time=10.0,
            end_time=20.0,
            transcript=None,
            indicators=[AnomalyType.DEPRESSION_INDICATOR],
            confidence=0.65,
            emotional_tone="melancólico"
        )
    ]
    
    risk = audio_service._compute_overall_risk(segments)
    
    # Com 100% dos segmentos com depressão, deve ser HIGH ou MEDIUM
    assert risk in [RiskLevel.MEDIUM, RiskLevel.HIGH]
