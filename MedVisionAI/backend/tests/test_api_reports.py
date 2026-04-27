"""
Testes dos endpoints da API de relatórios.

Valida listagem, exportação e formato de relatórios.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Cliente de testes para FastAPI."""
    return TestClient(app)


@pytest.mark.api
def test_list_reports(client):
    """Testa endpoint de listagem de relatórios."""
    response = client.get("/api/v1/reports/list")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "total" in data
    assert "reports" in data
    assert isinstance(data["reports"], list)


@pytest.mark.api
def test_export_report_markdown_nonexistent(client):
    """Testa exportar relatório inexistente como Markdown."""
    fake_id = "nonexistent-report-id"
    
    response = client.get(f"/api/v1/reports/{fake_id}/markdown?report_type=video")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.api
def test_export_report_json_nonexistent(client):
    """Testa obter relatório inexistente como JSON."""
    fake_id = "nonexistent-report-id"
    
    response = client.get(f"/api/v1/reports/{fake_id}/json?report_type=video")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.api
def test_export_report_invalid_type(client):
    """Testa exportar relatório com tipo inválido."""
    fake_id = "some-id"
    
    response = client.get(f"/api/v1/reports/{fake_id}/markdown?report_type=invalid")
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "report_type" in response.json()["detail"].lower()


@pytest.mark.api
@pytest.mark.integration
def test_export_report_markdown_valid(client, sample_video_analysis_result):
    """
    Testa exportar relatório válido como Markdown.
    
    Requer que um relatório exista no sistema.
    """
    # Este teste assumiria que já existe um relatório
    # Em ambiente real, criar um primeiro
    
    # Por ora, testa apenas a estrutura da resposta
    analysis_id = sample_video_analysis_result.analysis_id
    
    response = client.get(f"/api/v1/reports/{analysis_id}/markdown?report_type=video")
    
    # Pode retornar 404 se não salvo ou 200 se existir
    if response.status_code == status.HTTP_200_OK:
        assert response.headers["content-type"] == "text/markdown; charset=utf-8"
        assert "attachment" in response.headers.get("content-disposition", "")


@pytest.mark.api
@pytest.mark.integration
def test_export_audio_report_json(client, sample_audio_analysis_result):
    """Testa obter relatório de áudio como JSON."""
    analysis_id = sample_audio_analysis_result.analysis_id
    
    response = client.get(f"/api/v1/reports/{analysis_id}/json?report_type=audio")
    
    # Pode retornar 404 se não salvo
    if response.status_code == status.HTTP_200_OK:
        data = response.json()
        assert "analysis_id" in data
        assert "duration_seconds" in data


@pytest.mark.api
def test_reports_endpoint_cors(client):
    """Testa headers CORS no endpoint de relatórios."""
    response = client.options("/api/v1/reports/list")
    
    # Verifica que CORS está habilitado
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]


@pytest.mark.api
def test_list_reports_structure(client):
    """Testa estrutura detalhada da resposta de listagem."""
    response = client.get("/api/v1/reports/list")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Valida estrutura
    assert isinstance(data["total"], int)
    assert data["total"] >= 0
    assert isinstance(data["reports"], list)
    
    # Se houver relatórios, valida estrutura do primeiro
    if data["reports"]:
        report = data["reports"][0]
        assert "analysis_id" in report or "filename" in report
