"""
Serviço de gerenciamento de relatórios.

Responsável por salvar, carregar, listar e exportar relatórios
de análises de vídeo e áudio.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Literal, Union

from app.core.config import settings
from app.core.logging_config import get_logger
from app.models.schemas import VideoAnalysisResult, AudioAnalysisResult

logger = get_logger(__name__)


class ReportService:
    """
    Serviço de persistência e exportação de relatórios.
    
    Funcionalidades:
    - Salvar relatórios como JSON
    - Carregar relatórios por ID
    - Listar todos os relatórios
    - Exportar como Markdown
    """
    
    def __init__(self, storage_dir: str = "./storage/reports"):
        """
        Inicializa o serviço de relatórios.
        
        Args:
            storage_dir: Diretório para armazenar relatórios.
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"ReportService inicializado. Diretório: {self.storage_dir}")
    
    def save_report(
        self,
        result: Union[VideoAnalysisResult, AudioAnalysisResult],
        output_dir: str = None
    ) -> str:
        """
        Salva um relatório como JSON.
        
        Args:
            result: Resultado da análise (vídeo ou áudio).
            output_dir: Diretório customizado (usa storage_dir se None).
        
        Returns:
            Caminho do arquivo salvo.
        """
        save_dir = Path(output_dir) if output_dir else self.storage_dir
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Determina tipo e nome do arquivo
        if isinstance(result, VideoAnalysisResult):
            report_type = "video"
        else:
            report_type = "audio"
        
        filename = f"{result.analysis_id}_{report_type}.json"
        file_path = save_dir / filename
        
        # Serializa como JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result.model_dump(mode='json'), f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Relatório salvo: {file_path}")
        return str(file_path)
    
    def load_report(
        self,
        analysis_id: str,
        report_type: Literal["video", "audio"]
    ) -> dict:
        """
        Carrega um relatório salvo pelo ID.
        
        Args:
            analysis_id: ID da análise.
            report_type: Tipo do relatório ("video" ou "audio").
        
        Returns:
            Dicionário com os dados do relatório.
        
        Raises:
            FileNotFoundError: Se o relatório não existir.
        """
        filename = f"{analysis_id}_{report_type}.json"
        file_path = self.storage_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Relatório não encontrado: {analysis_id}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Relatório carregado: {analysis_id}")
        return data
    
    def list_reports(self) -> list[dict]:
        """
        Lista todos os relatórios salvos com metadados resumidos.
        
        Returns:
            Lista de dicionários com:
            - analysis_id
            - report_type
            - filename
            - created_at
            - file_size_bytes
        """
        reports = []
        
        for file_path in self.storage_dir.glob("*.json"):
            try:
                # Extrai metadados do nome do arquivo
                parts = file_path.stem.split('_')
                if len(parts) >= 2:
                    analysis_id = '_'.join(parts[:-1])
                    report_type = parts[-1]
                else:
                    continue
                
                # Obtém estatísticas do arquivo
                stat = file_path.stat()
                
                reports.append({
                    "analysis_id": analysis_id,
                    "report_type": report_type,
                    "filename": file_path.name,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "file_size_bytes": stat.st_size
                })
            except Exception as e:
                logger.warning(f"Erro ao processar arquivo {file_path.name}: {e}")
        
        # Ordena por data de criação (mais recente primeiro)
        reports.sort(key=lambda r: r["created_at"], reverse=True)
        
        return reports
    
    def export_as_markdown(
        self,
        result: Union[VideoAnalysisResult, AudioAnalysisResult]
    ) -> str:
        """
        Exporta um relatório em formato Markdown para download.
        
        Args:
            result: Resultado da análise.
        
        Returns:
            String com conteúdo Markdown formatado.
        """
        if isinstance(result, VideoAnalysisResult):
            return self._export_video_markdown(result)
        else:
            return self._export_audio_markdown(result)
    
    def _export_video_markdown(self, result: VideoAnalysisResult) -> str:
        """Exporta relatório de vídeo como Markdown."""
        total_anomalies = sum(result.anomaly_summary.values())
        critical_frames = [f for f in result.frames if f.severity == "critical"]
        
        md = f"""# Relatório de Análise de Vídeo Cirúrgico

**ID da Análise:** `{result.analysis_id}`  
**Arquivo:** {result.filename}  
**Data:** {result.created_at.strftime('%d/%m/%Y %H:%M:%S')}  
**Duração:** {result.duration_seconds:.1f}s  
**Frames Analisados:** {result.total_frames_analyzed}  
**Tempo de Processamento:** {result.processing_time_seconds:.1f}s  

---

## Sumário de Anomalias

Total de anomalias detectadas: **{total_anomalies}**

"""
        
        # Tabela de anomalias por tipo
        if result.anomaly_summary:
            md += "| Tipo de Anomalia | Ocorrências |\n"
            md += "|-----------------|-------------|\n"
            for anomaly_type, count in result.anomaly_summary.items():
                md += f"| {anomaly_type.replace('_', ' ').title()} | {count} |\n"
        else:
            md += "*Nenhuma anomalia detectada.*\n"
        
        md += "\n---\n\n"
        
        # Momentos críticos
        if critical_frames:
            md += "## Momentos Críticos\n\n"
            for frame in critical_frames[:10]:  # Top 10
                md += f"- **Frame {frame.frame_index}** (t={frame.timestamp_seconds:.1f}s): "
                md += f"{len(frame.bounding_boxes)} detecção(ões)\n"
        
        md += "\n---\n\n"
        
        # Relatório Gemini
        md += "## Relatório Técnico (IA)\n\n"
        md += result.gemini_report
        
        md += "\n\n---\n\n"
        md += "*Relatório gerado automaticamente por MedVision AI*\n"
        
        return md
    
    def _export_audio_markdown(self, result: AudioAnalysisResult) -> str:
        """Exporta relatório de áudio como Markdown."""
        segments_with_indicators = [s for s in result.segments if s.indicators]
        
        md = f"""# Relatório de Análise de Áudio — Consulta Médica

**ID da Análise:** `{result.analysis_id}`  
**Arquivo:** {result.filename}  
**Data:** {result.created_at.strftime('%d/%m/%Y %H:%M:%S')}  
**Duração:** {result.duration_seconds:.1f}s  
**Segmentos Analisados:** {len(result.segments)}  
**Nível de Risco Geral:** **{result.overall_risk_level.upper()}**  
**Tempo de Processamento:** {result.processing_time_seconds:.1f}s  

---

## Segmentos com Indicadores

Total de segmentos com indicadores: **{len(segments_with_indicators)}**

"""
        
        if segments_with_indicators:
            for i, segment in enumerate(segments_with_indicators[:10], 1):
                md += f"### Segmento {i} ({segment.start_time:.1f}s - {segment.end_time:.1f}s)\n\n"
                md += f"- **Tom Emocional:** {segment.emotional_tone}\n"
                md += f"- **Confiança:** {segment.confidence*100:.0f}%\n"
                md += f"- **Indicadores:** {', '.join([i.value for i in segment.indicators])}\n"
                if segment.transcript:
                    md += f"- **Transcrição:** \"{segment.transcript[:150]}...\"\n"
                md += "\n"
        else:
            md += "*Nenhum indicador de risco detectado.*\n"
        
        md += "\n---\n\n"
        
        # Relatório Gemini
        md += "## Relatório Psicológico (IA)\n\n"
        md += result.gemini_report
        
        md += "\n\n---\n\n"
        md += "*Relatório gerado automaticamente por MedVision AI*\n"
        md += "*Este relatório não substitui avaliação clínica profissional.*\n"
        
        return md


def get_report_service() -> ReportService:
    """
    Factory function para ReportService.
    
    Returns:
        Instância do ReportService.
    """
    return ReportService()
