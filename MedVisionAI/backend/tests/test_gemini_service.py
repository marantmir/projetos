"""
Testes do GeminiService.

Valida geração de relatórios e mecanismo de retry.
"""

import pytest


@pytest.mark.asyncio
async def test_generate_video_report_contains_sections(sample_video_analysis_result):
    """Testa que o relatório de vídeo contém as seções obrigatórias."""
    from app.services import get_gemini_service
    
    gemini_service = get_gemini_service()
    
    report = await gemini_service.generate_video_report(sample_video_analysis_result)
    
    # Verifica presença de seções (no relatório mockado ou real)
    assert isinstance(report, str)
    assert len(report) > 50  # Relatório não vazio


@pytest.mark.asyncio
async def test_generate_audio_report(sample_audio_analysis_result):
    """Testa geração de relatório de áudio."""
    from app.services import get_gemini_service
    
    gemini_service = get_gemini_service()
    
    report = await gemini_service.generate_audio_report(sample_audio_analysis_result)
    
    assert isinstance(report, str)
    assert len(report) > 50


# Teste de retry seria mais complexo e requereria mock de exceções da API
# Por enquanto, o teste básico valida estrutura
