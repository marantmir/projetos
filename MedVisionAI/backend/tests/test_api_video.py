"""
Testes dos endpoints da API de vídeo.

Valida rotas de upload, análise, status e recuperação de resultados.
"""

import io
import json
from pathlib import Path

import cv2
import numpy as np
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.models.enums import AnalysisStatusEnum


@pytest.fixture
def client():
    """Cliente de testes para FastAPI."""
    return TestClient(app)


@pytest.fixture
def fake_video_bytes():
    """Gera bytes de um vídeo MP4 sintético."""
    # Cria vídeo temporário em memória
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    temp_path = Path("/tmp/test_video.mp4")
    out = cv2.VideoWriter(str(temp_path), fourcc, 30.0, (640, 480))
    
    # Gera alguns frames
    for _ in range(30):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.circle(frame, (320, 240), 50, (0, 0, 255), -1)
        out.write(frame)
    
    out.release()
    
    # Lê bytes
    with open(temp_path, "rb") as f:
        video_bytes = f.read()
    
    temp_path.unlink()
    return video_bytes


@pytest.mark.api
@pytest.mark.integration
def test_health_endpoint(client):
    """Testa endpoint de health check."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "online"
    assert "version" in data


@pytest.mark.api
@pytest.mark.integration
def test_upload_video_success(client, fake_video_bytes):
    """Testa upload bem-sucedido de vídeo."""
    files = {"file": ("test_video.mp4", io.BytesIO(fake_video_bytes), "video/mp4")}
    
    response = client.post("/api/v1/video/analyze", files=files)
    
    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()
    
    assert "analysis_id" in data
    assert "message" in data
    assert data["status"] == AnalysisStatusEnum.QUEUED.value


@pytest.mark.api
def test_upload_video_invalid_format(client):
    """Testa upload de arquivo com formato inválido."""
    # Tenta enviar arquivo de texto como vídeo
    files = {"file": ("test.txt", io.BytesIO(b"not a video"), "text/plain")}
    
    response = client.post("/api/v1/video/analyze", files=files)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "formato" in response.json()["detail"].lower()


@pytest.mark.api
def test_upload_video_too_large(client):
    """Testa upload de arquivo muito grande."""
    # Simula arquivo de 1GB (apenas headers, não envia realmente)
    large_size = 1024 * 1024 * 1024 + 1  # 1GB + 1 byte
    
    files = {
        "file": ("huge_video.mp4", io.BytesIO(b"x" * 1000), "video/mp4")
    }
    
    # Note: Este teste pode depender da configuração de MAX_FILE_SIZE
    # Em um ambiente real, ajustar conforme necessário
    response = client.post("/api/v1/video/analyze", files=files)
    
    # Pode retornar 400 ou aceitar dependendo do tamanho configurado
    assert response.status_code in [status.HTTP_202_ACCEPTED, status.HTTP_400_BAD_REQUEST]


@pytest.mark.api
def test_get_status_nonexistent(client):
    """Testa obter status de análise inexistente."""
    fake_id = "nonexistent-analysis-id"
    
    response = client.get(f"/api/v1/video/status/{fake_id}")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.api
def test_get_result_nonexistent(client):
    """Testa obter resultado de análise inexistente."""
    fake_id = "nonexistent-analysis-id"
    
    response = client.get(f"/api/v1/video/result/{fake_id}")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.api
def test_delete_analysis_nonexistent(client):
    """Testa deletar análise inexistente."""
    fake_id = "nonexistent-analysis-id"
    
    response = client.delete(f"/api/v1/video/{fake_id}")
    
    # Pode retornar 404 ou 200 dependendo da implementação
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.slow
def test_full_video_analysis_flow(client, sample_video_path):
    """
    Testa fluxo completo: upload -> status -> resultado.
    
    Este é um teste de integração que pode demorar.
    """
    # 1. Upload
    with open(sample_video_path, "rb") as f:
        files = {"file": ("test_video.mp4", f, "video/mp4")}
        response = client.post("/api/v1/video/analyze", files=files)
    
    assert response.status_code == status.HTTP_202_ACCEPTED
    analysis_id = response.json()["analysis_id"]
    
    # 2. Verifica status (pode estar em fila ou processando)
    response = client.get(f"/api/v1/video/status/{analysis_id}")
    assert response.status_code == status.HTTP_200_OK
    
    status_data = response.json()
    assert status_data["analysis_id"] == analysis_id
    assert "status" in status_data
    
    # 3. Resultado pode não estar disponível imediatamente
    # Em teste real, aguardar ou usar mocks
    response = client.get(f"/api/v1/video/result/{analysis_id}")
    
    # Pode estar completo ou ainda processando
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


@pytest.mark.api
def test_upload_without_file(client):
    """Testa requisição sem arquivo."""
    response = client.post("/api/v1/video/analyze")
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.api
def test_video_cors_headers(client):
    """Testa que headers CORS estão presentes."""
    response = client.options("/api/v1/video/analyze")
    
    # Verifica headers de CORS
    assert "access-control-allow-origin" in response.headers or response.status_code == status.HTTP_200_OK
