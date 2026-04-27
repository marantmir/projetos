"""
Rotas da API para análise de vídeos cirúrgicos.

Endpoints:
- POST /analyze: Upload e análise de vídeo
- GET /status/{id}: Status da análise
- GET /result/{id}: Resultado completo
- GET /frames/{id}: Frames anotados
- DELETE /{id}: Remove análise
"""

import asyncio
from pathlib import Path
from typing import Dict, Optional
import uuid
import json

from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse

from app.core.config import settings
from app.core.logging_config import get_logger
from app.core.security import validate_upload_file, sanitize_filename, generate_analysis_id
from app.models.schemas import VideoAnalysisResult, AnalysisStatus
from app.models.patient_schemas import PatientData
from app.models.enums import AnalysisStatusEnum
from app.services import get_video_service, get_report_service, get_storage_service, get_anomaly_service
from app.utils import FrameAnnotator, validate_video_file
from app.api.routes.websocket import connection_manager

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/video", tags=["video"])

# Armazenamento em memória de status de análises
# Em produção, usar Redis ou banco de dados
analysis_statuses: Dict[str, dict] = {}
analysis_results: Dict[str, VideoAnalysisResult] = {}


async def process_video_task(
    analysis_id: str,
    file_path: str,
    filename: str
):
    """
    Task assíncrona para processar vídeo em background.
    
    Args:
        analysis_id: ID da análise.
        file_path: Caminho do arquivo temporário.
        filename: Nome original do arquivo.
    """
    try:
        logger.info(f"Iniciando processamento de vídeo: {analysis_id}")
        
        # Atualiza status
        analysis_statuses[analysis_id] = {
            "status": AnalysisStatusEnum.PROCESSING,
            "progress_percent": 0.0,
            "current_stage": "Inicializando análise...",
            "error_message": None
        }
        
        # Serviço de anomalias para gerar alertas
        anomaly_service = get_anomaly_service()
        
        # Callback de progresso e alertas
        async def progress_callback_async(percent: float, stage: str, frame_analysis=None):
            # Atualiza status local
            analysis_statuses[analysis_id].update({
                "progress_percent": percent,
                "current_stage": stage
            })
            
            # Envia progresso via WebSocket
            await connection_manager.broadcast_progress(
                analysis_id,
                percent,
                stage
            )
            
            # Se houver frame crítico, gera e envia alerta
            if frame_analysis and frame_analysis.severity in ["high", "critical"]:
                alert = anomaly_service.generate_alert(frame_analysis, analysis_id)
                if alert:
                    # Converte para dicionário
                    alert_dict = {
                        "alert_id": alert.alert_id,
                        "anomaly_type": alert.anomaly_type.value,
                        "severity": alert.severity.value,
                        "frame_number": alert.frame_index,
                        "frame_timestamp": frame_analysis.timestamp_seconds,
                        "timestamp": alert.timestamp.isoformat(),
                        "message": alert.description,
                        "confidence": alert.bounding_box.confidence if alert.bounding_box else None
                    }
                    
                    # Envia alerta via WebSocket
                    await connection_manager.broadcast_alert(analysis_id, alert_dict)
                    logger.info(f"🚨 Alerta crítico enviado: {alert.alert_id}")
        
        # Wrapper síncrono para o callback assíncrono
        def progress_callback(percent: float, stage: str, frame_analysis=None):
            asyncio.create_task(progress_callback_async(percent, stage, frame_analysis))
        
        # Processa vídeo
        video_service = get_video_service()
        result = await video_service.process_video(
            file_path=file_path,
            analysis_id=analysis_id,
            progress_callback=progress_callback
        )
        
        # Salva resultado
        report_service = get_report_service()
        report_service.save_report(result)
        
        # Armazena na memória
        analysis_results[analysis_id] = result
        
        # Atualiza status final
        analysis_statuses[analysis_id] = {
            "status": AnalysisStatusEnum.COMPLETED,
            "progress_percent": 100.0,
            "current_stage": "Concluído",
            "error_message": None
        }
        
        # Envia notificação de conclusão via WebSocket
        await connection_manager.broadcast_completed(analysis_id, {
            "total_frames": result.total_frames_analyzed,
            "anomaly_count": sum(result.anomaly_summary.values()),
            "processing_time": result.processing_time_seconds
        })
        
        logger.info(f"Análise de vídeo concluída: {analysis_id}")
    
    except Exception as e:
        logger.error(f"Erro ao processar vídeo {analysis_id}: {e}", exc_info=True)
        
        analysis_statuses[analysis_id] = {
            "status": AnalysisStatusEnum.FAILED,
            "progress_percent": 0.0,
            "current_stage": "Falha no processamento",
            "error_message": str(e)
        }
    
    finally:
        # Cleanup: remove arquivo temporário
        # NOTA: Mantém arquivo para streaming/download do vídeo pela interface
        # TODO: Implementar limpeza periódica de arquivos antigos
        # try:
        #     Path(file_path).unlink(missing_ok=True)
        # except Exception as e:
        #     logger.warning(f"Erro ao remover arquivo temporário {file_path}: {e}")
        pass


@router.post("/analyze", status_code=status.HTTP_202_ACCEPTED)
async def analyze_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Arquivo de vídeo para análise"),
    patient_data: Optional[str] = Form(None, description="Dados do paciente em formato JSON")
) -> JSONResponse:
    """
    Upload e análise assíncrona de vídeo cirúrgico.
    
    O processamento é executado em background. Use o endpoint /status/{analysis_id}
    para acompanhar o progresso.
    
    Args:
        file: Arquivo de vídeo para análise
        patient_data: Dados do paciente (JSON string opcional)
    
    Returns:
        JSON com analysis_id e status inicial.
    """
    # Valida arquivo
    await validate_upload_file(file, file_type="video")
    
    # Gera ID da análise
    analysis_id = generate_analysis_id()
    
    # Sanitiza nome do arquivo
    safe_filename = sanitize_filename(file.filename)
    
    # Salva arquivo temporariamente
    storage_service = get_storage_service()
    temp_dir = Path("./storage/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    temp_path = temp_dir / f"{analysis_id}_{safe_filename}"
    
    try:
        # Salva upload
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Valida vídeo
        is_valid, error_msg = validate_video_file(str(temp_path))
        if not is_valid:
            temp_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Vídeo inválido: {error_msg}"
            )
        
        # Inicializa status
        analysis_statuses[analysis_id] = {
            "status": AnalysisStatusEnum.QUEUED,
            "progress_percent": 0.0,
            "current_stage": "Na fila para processamento",
            "error_message": None
        }
        
        # Adiciona task em background
        background_tasks.add_task(
            process_video_task,
            analysis_id,
            str(temp_path),
            safe_filename
        )
        
        logger.info(f"Vídeo enviado para análise: {analysis_id} ({safe_filename})")
        
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={
                "analysis_id": analysis_id,
                "filename": safe_filename,
                "status": "queued",
                "message": "Vídeo recebido e em fila para processamento"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar upload: {e}")
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar upload: {str(e)}"
        )


@router.get("/status/{analysis_id}")
async def get_analysis_status(analysis_id: str) -> AnalysisStatus:
    """
    Obtém o status atual de uma análise.
    
    Args:
        analysis_id: ID da análise.
    
    Returns:
        Status atual do processamento.
    """
    if analysis_id not in analysis_statuses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Análise não encontrada: {analysis_id}"
        )
    
    status_data = analysis_statuses[analysis_id]
    
    return AnalysisStatus(
        analysis_id=analysis_id,
        status=status_data["status"],
        progress_percent=status_data["progress_percent"],
        current_stage=status_data["current_stage"],
        error_message=status_data.get("error_message")
    )


@router.get("/result/{analysis_id}")
async def get_analysis_result(analysis_id: str) -> VideoAnalysisResult:
    """
    Obtém o resultado completo de uma análise concluída.
    
    Args:
        analysis_id: ID da análise.
    
    Returns:
        Resultado completo da análise com frames e relatório.
    """
    # Verifica status
    if analysis_id not in analysis_statuses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Análise não encontrada: {analysis_id}"
        )
    
    status_data = analysis_statuses[analysis_id]
    
    if status_data["status"] != AnalysisStatusEnum.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Análise ainda não concluída. Status: {status_data['status']}"
        )
    
    # Retorna resultado
    if analysis_id in analysis_results:
        return analysis_results[analysis_id]
    
    # Tenta carregar do disco
    try:
        report_service = get_report_service()
        result_data = report_service.load_report(analysis_id, "video")
        return VideoAnalysisResult(**result_data)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resultado não encontrado"
        )


@router.get("/download/{analysis_id}")
async def download_video(analysis_id: str, request: Request):
    """
    Baixa o vídeo original associado a uma análise.
    Suporta Range requests para streaming HTML5.
    
    Args:
        analysis_id: ID da análise.
        request: Request HTTP para acessar headers.
    
    Returns:
        Arquivo de vídeo ou StreamingResponse com range parcial.
    """
    from pathlib import Path
    from fastapi.responses import StreamingResponse
    import os
    
    storage_path = Path("storage/temp")
    logger.info(f"Buscando vídeo para análise {analysis_id} em {storage_path.absolute()}")
    
    # Tenta encontrar o vídeo com qualquer extensão comum
    video_extensions = ["mp4", "avi", "mov", "mkv", "webm", "flv", "wmv"]
    video_files = []
    
    # Lista todos os arquivos no diretório
    all_files = list(storage_path.iterdir()) if storage_path.exists() else []
    logger.info(f"Arquivos no storage/temp: {[f.name for f in all_files]}")
    
    for ext in video_extensions:
        pattern = f"{analysis_id}_*.{ext}"
        found = list(storage_path.glob(pattern))
        logger.info(f"Buscando padrão {pattern}: {[f.name for f in found]}")
        if found:
            video_files = found
            break
    
    if not video_files:
        logger.error(f"Vídeo não encontrado para análise {analysis_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Arquivo de vídeo não encontrado para análise {analysis_id}"
        )
    
    video_path = video_files[0]
    file_size = os.path.getsize(video_path)
    
    logger.info(f"Arquivo encontrado: {video_path.name}, tamanho: {file_size} bytes")
    
    # Detecta tipo MIME baseado na extensão
    mime_types = {
        'mp4': 'video/mp4',
        'avi': 'video/x-msvideo',
        'mov': 'video/quicktime',
        'mkv': 'video/x-matroska',
        'webm': 'video/webm',
        'flv': 'video/x-flv',
        'wmv': 'video/x-ms-wmv'
    }
    
    ext = video_path.suffix.lower().lstrip('.')
    media_type = mime_types.get(ext, 'video/mp4')
    
    logger.info(f"Extensão: {ext}, MIME type: {media_type}")
    
    # Verifica se é uma requisição Range
    range_header = request.headers.get('range')
    
    logger.info(f"Range header: {range_header}")
    
    if not range_header:
        # Sem range, retorna arquivo completo
        response = FileResponse(
            path=str(video_path),
            media_type=media_type,
            filename=video_path.name
        )
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Accept-Ranges'] = 'bytes'
        return response
    
    # Parse do range header (formato: "bytes=start-end")
    try:
        range_str = range_header.replace('bytes=', '')
        range_parts = range_str.split('-')
        start = int(range_parts[0]) if range_parts[0] else 0
        end = int(range_parts[1]) if len(range_parts) > 1 and range_parts[1] else file_size - 1
        
        # Garante que end não exceda o tamanho do arquivo
        end = min(end, file_size - 1)
        chunk_size = end - start + 1
        
        # Função geradora para streaming
        def iter_file():
            with open(video_path, 'rb') as f:
                f.seek(start)
                remaining = chunk_size
                while remaining > 0:
                    read_size = min(8192, remaining)  # 8KB chunks
                    data = f.read(read_size)
                    if not data:
                        break
                    remaining -= len(data)
                    yield data
        
        headers = {
            'Content-Range': f'bytes {start}-{end}/{file_size}',
            'Accept-Ranges': 'bytes',
            'Content-Length': str(chunk_size),
            'Content-Type': media_type,
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Expose-Headers': 'Content-Range, Content-Length, Accept-Ranges'
        }
        
        logger.info(f"Retornando Range: bytes {start}-{end}/{file_size} ({chunk_size} bytes)")
        
        return StreamingResponse(
            iter_file(),
            status_code=206,  # Partial Content
            headers=headers,
            media_type=media_type
        )
        
    except (ValueError, IndexError) as e:
        # Range header inválido
        raise HTTPException(
            status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
            detail=f"Range inválido: {range_header}"
        )


@router.get("/frames/{analysis_id}")
async def get_annotated_frames(
    analysis_id: str,
    limit: int = 10
) -> JSONResponse:
    """
    Obtém frames anotados com bounding boxes.
    
    Args:
        analysis_id: ID da análise.
        limit: Número máximo de frames a retornar.
    
    Returns:
        JSON com lista de frames em base64.
    """
    # Obtém resultado
    if analysis_id not in analysis_results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resultado não encontrado"
        )
    
    result = analysis_results[analysis_id]
    
    # Seleciona frames críticos e de alta severidade
    critical_frames = [
        f for f in result.frames 
        if f.severity in ["critical", "high"]
    ][:limit]
    
    # TODO: Recuperar frames originais e anotar
    # Por enquanto, retorna apenas metadados
    frames_data = [
        {
            "frame_index": f.frame_index,
            "timestamp": f.timestamp_seconds,
            "severity": f.severity,
            "anomalies": [a.value for a in f.anomalies_detected],
            "bounding_boxes": [box.model_dump() for box in f.bounding_boxes]
        }
        for f in critical_frames
    ]
    
    return JSONResponse(content={"frames": frames_data})


@router.delete("/{analysis_id}")
async def delete_analysis(analysis_id: str) -> JSONResponse:
    """
    Remove uma análise e seus arquivos associados.
    
    Args:
        analysis_id: ID da análise.
    
    Returns:
        Mensagem de confirmação.
    """
    if analysis_id not in analysis_statuses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Análise não encontrada: {analysis_id}"
        )
    
    # Remove do cache em memória
    analysis_statuses.pop(analysis_id, None)
    analysis_results.pop(analysis_id, None)
    
    # Remove relatório do disco
    try:
        report_service = get_report_service()
        report_path = report_service.storage_dir / f"{analysis_id}_video.json"
        if report_path.exists():
            report_path.unlink()
    except Exception as e:
        logger.warning(f"Erro ao remover relatório {analysis_id}: {e}")
    
    logger.info(f"Análise removida: {analysis_id}")
    
    return JSONResponse(
        content={"message": f"Análise {analysis_id} removida com sucesso"}
    )
