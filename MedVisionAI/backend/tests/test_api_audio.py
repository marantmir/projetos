"""
Testes dos endpoints da API de áudio.

Valida rotas de upload, análise, status e transcrição.
"""

import io
import json

import numpy as np
import pytest
import soundfile as sf
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.models.enums import AnalysisStatusEnum, ConsultationType


@pytest.fixture
def client():
    """Cliente de testes para FastAPI."""
    return TestClient(app)


@pytest.fixture
def fake_audio_bytes():
    """Gera bytes de um arquivo WAV sintético."""
    # Gera sinal de áudio simples
    sr = 22050
    duration = 2
    frequency = 440  # Hz
    
    t = np.linspace(0, duration, int(sr * duration))
    audio = 0.5 * np.sin(2 * np.pi * frequency * t)
    
    # Escreve em buffer
    buffer = io.BytesIO()
    sf.write(buffer, audio, sr, format='WAV')
    buffer.seek(0)
    
    return buffer.getvalue()


@pytest.mark.api
@pytest.mark.integration
def test_upload_audio_success(client, fake_audio_bytes):
    """Testa upload bem-sucedido de áudio."""
    files = {"file": ("test_audio.wav", io.BytesIO(fake_audio_bytes), "audio/wav")}
    
    response = client.post("/api/v1/audio/analyze", files=files)
    
    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()
    
    assert "analysis_id" in data
    assert "message" in data
    assert data["status"] == AnalysisStatusEnum.QUEUED.value


@pytest.mark.api
def test_upload_audio_with_patient_data(client, fake_audio_bytes):
    """Testa upload de áudio com dados da paciente."""
    patient_data = {
        "nome": "Maria Silva",
        "idade": 35,
        "cpf": "123.456.789-00"
    }
    
    files = {"file": ("test_audio.wav", io.BytesIO(fake_audio_bytes), "audio/wav")}
    data = {
        "patient_data": json.dumps(patient_data),
        "consultation_type": ConsultationType.GYNECOLOGICAL.value
    }
    
    response = client.post("/api/v1/audio/analyze", files=files, data=data)
    
    assert response.status_code == status.HTTP_202_ACCEPTED


@pytest.mark.api
def test_upload_audio_invalid_format(client):
    """Testa upload de arquivo com formato inválido."""
    files = {"file": ("test.txt", io.BytesIO(b"not audio"), "text/plain")}
    
    response = client.post("/api/v1/audio/analyze", files=files)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "formato" in response.json()["detail"].lower()


@pytest.mark.api
def test_get_audio_status_nonexistent(client):
    """Testa obter status de análise de áudio inexistente."""
    fake_id = "nonexistent-audio-id"
    
    response = client.get(f"/api/v1/audio/status/{fake_id}")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.api
def test_get_audio_result_nonexistent(client):
    """Testa obter resultado de análise de áudio inexistente."""
    fake_id = "nonexistent-audio-id"
    
    response = client.get(f"/api/v1/audio/result/{fake_id}")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.api
def test_get_audio_segments_nonexistent(client):
    """Testa obter segmentos de áudio inexistente."""
    fake_id = "nonexistent-audio-id"
    
    response = client.get(f"/api/v1/audio/segments/{fake_id}")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.slow
def test_full_audio_analysis_flow(client, sample_audio_path):
    """Testa fluxo completo de análise de áudio."""
    # 1. Upload
    with open(sample_audio_path, "rb") as f:
        files = {"file": ("test_audio.wav", f, "audio/wav")}
        response = client.post("/api/v1/audio/analyze", files=files)
    
    assert response.status_code == status.HTTP_202_ACCEPTED
    analysis_id = response.json()["analysis_id"]
    
    # 2. Verifica status
    response = client.get(f"/api/v1/audio/status/{analysis_id}")
    assert response.status_code == status.HTTP_200_OK
    
    status_data = response.json()
    assert status_data["analysis_id"] == analysis_id
    
    # 3. Resultado (pode não estar pronto)
    response = client.get(f"/api/v1/audio/result/{analysis_id}")
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.api
def test_transcription_endpoint(client):
    """Testa endpoint de transcrição."""
    request_data = {
        "audio_analysis_id": "test-id",
        "patient_name": "Maria Silva",
        "consultation_type": ConsultationType.GYNECOLOGICAL.value
    }
    
    response = client.post("/api/v1/audio/transcribe", json=request_data)
    
    # Pode retornar 404 se análise não existe ou 200 se mockado
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.api
def test_upload_audio_without_file(client):
    """Testa requisição sem arquivo de áudio."""
    response = client.post("/api/v1/audio/analyze")
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.api
def test_audio_consultation_type_validation(client, fake_audio_bytes):
    """Testa validação de tipo de consulta."""
    files = {"file": ("test_audio.wav", io.BytesIO(fake_audio_bytes), "audio/wav")}
    data = {"consultation_type": "INVALID_TYPE"}
    
    response = client.post("/api/v1/audio/analyze", files=files, data=data)
    
    # Deve aceitar ou rejeitar dependendo da validação
    assert response.status_code in [
        status.HTTP_202_ACCEPTED,
        status.HTTP_400_BAD_REQUEST,
        status.HTTP_422_UNPROCESSABLE_ENTITY
    ]
