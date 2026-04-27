"""
Rotas da API para gerenciamento de relatórios.

Endpoints:
- GET /list: Lista todos os relatórios
- GET /{id}/markdown: Exporta relatório como Markdown
- GET /{id}/json: Obtém relatório completo em JSON
"""

from fastapi import APIRouter, HTTPException, status, Response
from fastapi.responses import JSONResponse

from app.core.logging_config import get_logger
from app.services import get_report_service
from app.models.schemas import VideoAnalysisResult, AudioAnalysisResult

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.get("/list")
async def list_reports() -> JSONResponse:
    """
    Lista todos os relatórios salvos.
    
    Returns:
        JSON com lista de relatórios e metadados.
    """
    report_service = get_report_service()
    reports = report_service.list_reports()
    
    return JSONResponse(content={
        "total": len(reports),
        "reports": reports
    })


@router.get("/{analysis_id}/markdown")
async def export_report_markdown(
    analysis_id: str,
    report_type: str = "video"
) -> Response:
    """
    Exporta relatório em formato Markdown para download.
    
    Args:
        analysis_id: ID da análise.
        report_type: Tipo do relatório ("video" ou "audio").
    
    Returns:
        Arquivo Markdown para download.
    """
    if report_type not in ["video", "audio"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="report_type deve ser 'video' ou 'audio'"
        )
    
    report_service = get_report_service()
    
    try:
        # Carrega relatório
        result_data = report_service.load_report(analysis_id, report_type)
        
        # Converte para objeto
        if report_type == "video":
            result = VideoAnalysisResult(**result_data)
        else:
            result = AudioAnalysisResult(**result_data)
        
        # Exporta como Markdown
        markdown_content = report_service.export_as_markdown(result)
        
        # Retorna como arquivo para download
        return Response(
            content=markdown_content,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename={analysis_id}_relatorio.md"
            }
        )
    
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relatório não encontrado: {analysis_id}"
        )
    except Exception as e:
        logger.error(f"Erro ao exportar relatório {analysis_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao exportar relatório"
        )


@router.get("/{analysis_id}/json")
async def get_report_json(
    analysis_id: str,
    report_type: str = "video"
) -> JSONResponse:
    """
    Obtém relatório completo em JSON.
    
    Args:
        analysis_id: ID da análise.
        report_type: Tipo do relatório ("video" ou "audio").
    
    Returns:
        Relatório completo em JSON.
    """
    if report_type not in ["video", "audio"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="report_type deve ser 'video' ou 'audio'"
        )
    
    report_service = get_report_service()
    
    try:
        result_data = report_service.load_report(analysis_id, report_type)
        return JSONResponse(content=result_data)
    
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relatório não encontrado: {analysis_id}"
        )
