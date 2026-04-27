"""
Testes do ReportService.

Valida persistência, carregamento e exportação de relatórios.
"""

from datetime import datetime
from pathlib import Path

import pytest

from app.services.report_service import ReportService
from app.models.schemas import VideoAnalysisResult, AudioAnalysisResult, AudioSegment
from app.models.enums import RiskLevel, SeverityLevel, AnomalyType


@pytest.mark.unit
class TestReportService:
    """Testes do serviço de relatórios."""
    
    def test_init_creates_directory(self, tmp_path):
        """Testa que inicialização cria diretório de storage."""
        storage_dir = tmp_path / "reports"
        service = ReportService(storage_dir=str(storage_dir))
        
        assert storage_dir.exists()
        assert service.storage_dir == storage_dir
    
    def test_save_video_report(self, tmp_path, sample_video_analysis_result):
        """Testa salvar relatório de vídeo."""
        service = ReportService(storage_dir=str(tmp_path))
        
        file_path = service.save_report(sample_video_analysis_result)
        
        assert Path(file_path).exists()
        assert sample_video_analysis_result.analysis_id in file_path
        assert "video" in file_path
    
    def test_save_audio_report(self, tmp_path, sample_audio_analysis_result):
        """Testa salvar relatório de áudio."""
        service = ReportService(storage_dir=str(tmp_path))
        
        file_path = service.save_report(sample_audio_analysis_result)
        
        assert Path(file_path).exists()
        assert sample_audio_analysis_result.analysis_id in file_path
        assert "audio" in file_path
    
    def test_load_video_report(self, tmp_path, sample_video_analysis_result):
        """Testa carregar relatório de vídeo salvo."""
        service = ReportService(storage_dir=str(tmp_path))
        
        # Salva primeiro
        service.save_report(sample_video_analysis_result)
        
        # Carrega
        loaded_data = service.load_report(
            sample_video_analysis_result.analysis_id,
            "video"
        )
        
        assert loaded_data["analysis_id"] == sample_video_analysis_result.analysis_id
        assert loaded_data["filename"] == sample_video_analysis_result.filename
    
    def test_load_nonexistent_report_raises_error(self, tmp_path):
        """Testa que carregar relatório inexistente levanta FileNotFoundError."""
        service = ReportService(storage_dir=str(tmp_path))
        
        with pytest.raises(FileNotFoundError, match="Relatório não encontrado"):
            service.load_report("nonexistent-id", "video")
    
    def test_list_reports_empty(self, tmp_path):
        """Testa listar relatórios em diretório vazio."""
        service = ReportService(storage_dir=str(tmp_path))
        
        reports = service.list_reports()
        
        assert isinstance(reports, list)
        assert len(reports) == 0
    
    def test_list_reports_with_multiple(self, tmp_path, sample_video_analysis_result, sample_audio_analysis_result):
        """Testa listar múltiplos relatórios."""
        service = ReportService(storage_dir=str(tmp_path))
        
        # Salva dois relatórios
        service.save_report(sample_video_analysis_result)
        service.save_report(sample_audio_analysis_result)
        
        reports = service.list_reports()
        
        assert len(reports) == 2
        assert all("analysis_id" in r for r in reports)
        assert all("report_type" in r for r in reports)
        assert all("file_size_bytes" in r for r in reports)
    
    def test_export_video_as_markdown(self, sample_video_analysis_result):
        """Testa exportar relatório de vídeo como Markdown."""
        service = ReportService()
        
        markdown = service.export_as_markdown(sample_video_analysis_result)
        
        assert isinstance(markdown, str)
        assert len(markdown) > 0
        assert "#" in markdown  # Deve conter headers Markdown
        assert sample_video_analysis_result.analysis_id in markdown
    
    def test_export_audio_as_markdown(self, sample_audio_analysis_result):
        """Testa exportar relatório de áudio como Markdown."""
        service = ReportService()
        
        markdown = service.export_as_markdown(sample_audio_analysis_result)
        
        assert isinstance(markdown, str)
        assert len(markdown) > 0
        assert "#" in markdown
    
    def test_report_json_structure(self, tmp_path, sample_video_analysis_result):
        """Testa estrutura do JSON salvo."""
        service = ReportService(storage_dir=str(tmp_path))
        
        file_path = service.save_report(sample_video_analysis_result)
        
        import json
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Verifica campos essenciais
        assert "analysis_id" in data
        assert "filename" in data
        assert "duration_seconds" in data
        assert "total_frames_analyzed" in data
    
    def test_reports_sorted_by_date(self, tmp_path):
        """Testa que list_reports retorna ordenado por data (mais recente primeiro)."""
        service = ReportService(storage_dir=str(tmp_path))
        
        # Cria múltiplos relatórios
        for i in range(3):
            result = VideoAnalysisResult(
                analysis_id=f"test-{i}",
                filename=f"video{i}.mp4",
                duration_seconds=10.0,
                total_frames_analyzed=100,
                frames=[],
                anomaly_summary={},
                gemini_report="Test",
                processing_time_seconds=1.0,
                created_at=datetime.utcnow()
            )
            service.save_report(result)
        
        reports = service.list_reports()
        
        # Verifica que está ordenado (mais recente primeiro)
        if len(reports) > 1:
            assert reports[0]["created_at"] >= reports[-1]["created_at"]
    
    def test_custom_output_dir(self, tmp_path):
        """Testa salvar relatório em diretório customizado."""
        service = ReportService(storage_dir=str(tmp_path / "default"))
        custom_dir = tmp_path / "custom"
        
        result = VideoAnalysisResult(
            analysis_id="custom-test",
            filename="test.mp4",
            duration_seconds=5.0,
            total_frames_analyzed=50,
            frames=[],
            anomaly_summary={},
            gemini_report="Test",
            processing_time_seconds=1.0,
            created_at=datetime.utcnow()
        )
        
        file_path = service.save_report(result, output_dir=str(custom_dir))
        
        assert custom_dir.exists()
        assert str(custom_dir) in file_path
