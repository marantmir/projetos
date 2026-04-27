"""
Rotas da API para análise de áudio de consultas médicas.

Endpoints:
- POST /analyze: Upload e análise de áudio
- GET /status/{id}: Status da análise
- GET /result/{id}: Resultado completo
- GET /segments/{id}: Segmentos com indicadores
- POST /transcribe: Gera transcrição para prontuário
"""

import asyncio
from pathlib import Path
from typing import Dict
import json

from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import JSONResponse

from app.core.logging_config import get_logger
from app.core.security import validate_upload_file, sanitize_filename, generate_analysis_id
from app.models.schemas import AudioAnalysisResult, AnalysisStatus
from app.models.patient_schemas import TranscriptionRequest, MedicalRecordTranscription, PatientData
from app.models.enums import AnalysisStatusEnum, ConsultationType
from app.services import get_audio_service, get_report_service
from app.utils import validate_audio_file

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/audio", tags=["audio"])

# Armazenamento em memória
audio_analysis_statuses: Dict[str, dict] = {}
audio_analysis_results: Dict[str, AudioAnalysisResult] = {}


async def process_audio_task(
    analysis_id: str,
    file_path: str,
    filename: str,
    consultation_type: ConsultationType = ConsultationType.GENERAL,
    patient_data_json: str | None = None
):
    """
    Task assíncrona para processar áudio em background.
    
    Args:
        analysis_id: ID da análise.
        file_path: Caminho do arquivo temporário.
        filename: Nome original do arquivo.
        consultation_type: Tipo de consulta médica.
        patient_data_json: Dados do paciente em formato JSON string.
    """
    try:
        logger.info(f"Iniciando processamento de áudio: {analysis_id}")
        
        # Parse patient data se fornecido
        patient_data = None
        if patient_data_json:
            try:
                patient_dict = json.loads(patient_data_json)
                patient_data = PatientData(**patient_dict)
                logger.info(f"Dados da paciente carregados: {patient_data.nome}")
            except Exception as e:
                logger.warning(f"Erro ao parsear dados da paciente: {e}")
        
        # Atualiza status
        audio_analysis_statuses[analysis_id] = {
            "status": AnalysisStatusEnum.PROCESSING,
            "progress_percent": 10.0,
            "current_stage": "Carregando áudio e extraindo features",
            "error_message": None
        }
        
        # Processa áudio
        audio_service = get_audio_service()
        result = await audio_service.process_audio(
            file_path=file_path,
            analysis_id=analysis_id,
            consultation_type=consultation_type,
            patient_data=patient_data
        )
        
        # Salva resultado
        report_service = get_report_service()
        report_service.save_report(result)
        
        # Armazena na memória
        audio_analysis_results[analysis_id] = result
        
        # Atualiza status final
        audio_analysis_statuses[analysis_id] = {
            "status": AnalysisStatusEnum.COMPLETED,
            "progress_percent": 100.0,
            "current_stage": "Concluído",
            "error_message": None
        }
        
        logger.info(f"Análise de áudio concluída: {analysis_id}")
    
    except Exception as e:
        logger.error(f"Erro ao processar áudio {analysis_id}: {e}", exc_info=True)
        
        audio_analysis_statuses[analysis_id] = {
            "status": AnalysisStatusEnum.FAILED,
            "progress_percent": 0.0,
            "current_stage": "Falha no processamento",
            "error_message": str(e)
        }
    
    finally:
        # Cleanup
        try:
            Path(file_path).unlink(missing_ok=True)
        except Exception as e:
            logger.warning(f"Erro ao remover arquivo temporário {file_path}: {e}")


@router.post("/analyze", status_code=status.HTTP_202_ACCEPTED)
async def analyze_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Arquivo de áudio para análise"),
    consultation_type: str = Form(default="general", description="Tipo de consulta: gynecological, prenatal, postpartum, general"),
    patient_data: str | None = Form(None, description="Dados do paciente em formato JSON")
) -> JSONResponse:
    """
    Upload e análise assíncrona de áudio de consulta médica.
    
    Args:
        file: Arquivo de áudio (WAV, MP3, OGG).
        consultation_type: Tipo de consulta médica especializada.
        patient_data: Dados do paciente (JSON string opcional).
    
    Returns:
        JSON com analysis_id e status inicial.
    """
    # Valida arquivo
    await validate_upload_file(file, file_type="audio")
    
    # Valida consultation_type
    try:
        consult_type = ConsultationType(consultation_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de consulta inválido. Use: gynecological, prenatal, postpartum, general"
        )
    
    # Gera ID
    analysis_id = generate_analysis_id()
    safe_filename = sanitize_filename(file.filename)
    
    # Salva temporariamente
    temp_dir = Path("./storage/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / f"{analysis_id}_{safe_filename}"
    
    try:
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Valida áudio
        is_valid, error_msg = validate_audio_file(str(temp_path))
        if not is_valid:
            temp_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Áudio inválido: {error_msg}"
            )
        
        # Inicializa status
        audio_analysis_statuses[analysis_id] = {
            "status": AnalysisStatusEnum.QUEUED,
            "progress_percent": 0.0,
            "current_stage": "Na fila para processamento",
            "error_message": None
        }
        
        # Adiciona task
        background_tasks.add_task(
            process_audio_task,
            analysis_id,
            str(temp_path),
            safe_filename,
            consult_type,
            patient_data  # Passa o JSON string recebido do Form
        )
        
        logger.info(f"Áudio enviado para análise: {analysis_id} ({safe_filename}, tipo: {consult_type.value})")
        
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={
                "analysis_id": analysis_id,
                "filename": safe_filename,
                "consultation_type": consult_type.value,
                "status": "queued",
                "message": "Áudio recebido e em fila para processamento"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar upload de áudio: {e}")
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar upload"
        )


@router.get("/status/{analysis_id}")
async def get_audio_status(analysis_id: str) -> AnalysisStatus:
    """
    Obtém o status atual de uma análise de áudio.
    
    Returns:
        Status atualizado com progresso.
    """
    if analysis_id not in audio_analysis_statuses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análise não encontrada"
        )
    
    status_dict = audio_analysis_statuses[analysis_id]
    
    return AnalysisStatus(
        analysis_id=analysis_id,
        status=status_dict["status"],
        progress_percent=status_dict["progress_percent"],
        current_stage=status_dict["current_stage"],
        error_message=status_dict.get("error_message")
    )


@router.get("/result/{analysis_id}")
async def get_audio_result(analysis_id: str) -> AudioAnalysisResult:
    """
    Obtém o resultado completo de uma análise de áudio.
    
    Returns:
        Resultado completo com segmentos e relatório.
    """
    if analysis_id not in audio_analysis_statuses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análise não encontrada"
        )
    
    status_dict = audio_analysis_statuses[analysis_id]
    
    if status_dict["status"] != AnalysisStatusEnum.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Análise ainda não concluída. Status: {status_dict['status'].value}"
        )
    
    if analysis_id in audio_analysis_results:
        return audio_analysis_results[analysis_id]
    
    # Tenta carregar do disco
    try:
        report_service = get_report_service()
        result_data = report_service.load_report(analysis_id, "audio")
        return AudioAnalysisResult(**result_data)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resultado não encontrado"
        )


@router.get("/segments/{analysis_id}")
async def get_audio_segments(analysis_id: str) -> JSONResponse:
    """
    Obtém segmentos de áudio com indicadores psicológicos.
    
    Returns:
        JSON com lista de segmentos e suas características.
    """
    if analysis_id not in audio_analysis_results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resultado não encontrado"
        )
    
    result = audio_analysis_results[analysis_id]
    
    # Filtra apenas segmentos com indicadores
    segments_with_indicators = [
        {
            "start_time": seg.start_time,
            "end_time": seg.end_time,
            "duration": seg.end_time - seg.start_time,
            "indicators": [ind.value for ind in seg.indicators],
            "confidence": seg.confidence,
            "emotional_tone": seg.emotional_tone,
            "transcript": seg.transcript[:200] if seg.transcript else None
        }
        for seg in result.segments
        if seg.indicators
    ]
    
    return JSONResponse(content={
        "analysis_id": analysis_id,
        "total_segments": len(result.segments),
        "segments_with_indicators": len(segments_with_indicators),
        "overall_risk": result.overall_risk_level.value,
        "segments": segments_with_indicators
    })


@router.post("/transcribe")
async def generate_transcription(request: TranscriptionRequest) -> MedicalRecordTranscription:
    """
    Gera transcrição formatada para prontuário médico com dados do paciente.
    
    Args:
        request: Dados da requisition com analysis_id e informações do paciente.
    
    Returns:
        Transcrição formatada para registro em prontuário.
    """
    analysis_id = request.analysis_id
    
    # Busca resultado da análise
    if analysis_id not in audio_analysis_results:
        # Tenta carregar do disco
        try:
            report_service = get_report_service()
            result_data = report_service.load_report(analysis_id, "audio")
            result = AudioAnalysisResult(**result_data)
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Análise não encontrada"
            )
    else:
        result = audio_analysis_results[analysis_id]
    
    # Gera sumário da consulta
    consultation_types = {
        "gynecological": "ginecológica",
        "prenatal": "pré-natal",
        "postpartum": "pós-parto",
        "general": "geral"
    }
    
    consultation_name = consultation_types.get(
        result.consultation_type.value if hasattr(result, 'consultation_type') else 'general',
        "médica"
    )
    
    consultation_summary = f"Consulta {consultation_name} realizada em {request.patient_data.consultation_date.strftime('%d/%m/%Y às %H:%M')}. Motivo: {request.patient_data.consultation_reason}. Duração da consulta: {result.duration_seconds:.0f} segundos ({result.duration_seconds // 60:.0f} minutos)."
    
    # Gera achados psicológicos se solicitado
    psychological_findings = None
    if request.include_psychological_indicators:
        # Conta indicadores
        indicator_counts = {}
        for segment in result.segments:
            for indicator in segment.indicators:
                indicator_counts[indicator.value] = indicator_counts.get(indicator.value, 0) + 1
        
        if indicator_counts:
            findings_lines = ["Análise acústica automatizada identificou os seguintes indicadores:\n"]
            
            for indicator, count in indicator_counts.items():
                indicator_readable = indicator.replace("_", " ").title()
                findings_lines.append(f"- {indicator_readable}: {count} segmentos")
            
            findings_lines.append(f"\nNível de risco geral classificado como: {result.overall_risk_level.value.upper()}")
            findings_lines.append("\nOBS: Estes indicadores são baseados em análise computacional de padrões vocais e devem ser interpretados em conjunto com avaliação clínica presencial.")
            
            psychological_findings = "\n".join(findings_lines)
        else:
            psychological_findings = "Análise acústica não identificou indicadores de risco psicológico significativos."
    
    # Gera recomendações
    if result.overall_risk_level.value == "high":
        recommendations_text = """1. Avaliação presencial urgente por profissional de saúde mental
2. Considerar aplicação de escalas validadas (Edinburgh, PHQ-9, GAD-7)
3. Acompanhamento em até 48-72 horas
4. Avaliar necessidade de encaminhamento para serviço especializado"""
    elif result.overall_risk_level.value == "medium":
        recommendations_text = """1. Acompanhamento clínico detalhado
2. Avaliar contexto psicossocial
3. Retorno em 7-14 dias para reavaliação
4. Disponibilizar canais de suporte"""
    else:
        recommendations_text = """1. Manter acompanhamento de rotina conforme protocolo
2. Estar atento a mudanças no padrão emocional
3. Oferecer espaço seguro para expressão de preocupações"""
    
    # Transcrição (placeholder - Gemini poderia gerar isso)
    transcription_text = result.transcription if hasattr(result, 'transcription') and result.transcription else "Transcrição não disponível. Análise baseada em features acústicas."
    
    logger.info(f"Transcrição gerada para análise {analysis_id} - Paciente: {request.patient_data.medical_record_number}")
    
    return MedicalRecordTranscription(
        patient_data=request.patient_data,
        consultation_summary=consultation_summary,
        transcription=transcription_text,
        psychological_findings=psychological_findings,
        recommendations=recommendations_text
    )


@router.get("/download-transcription/{analysis_id}")
async def download_transcription(analysis_id: str):
    """
    Baixa a transcrição de um áudio analisado em formato .txt.
    
    Args:
        analysis_id: ID da análise.
    
    Returns:
        Arquivo .txt com a transcrição.
    """
    from fastapi.responses import Response
    
    # Busca resultado da análise
    if analysis_id not in audio_analysis_results:
        # Tenta carregar do disco
        try:
            report_service = get_report_service()
            result_data = report_service.load_report(analysis_id, "audio")
            result = AudioAnalysisResult(**result_data)
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Análise não encontrada"
            )
    else:
        result = audio_analysis_results[analysis_id]
    
    # Verifica se há transcrição disponível
    transcription = result.transcription if hasattr(result, 'transcription') and result.transcription else None
    
    if not transcription:
        # Gera mensagem de transcrição indisponível
        transcription_lines = [
            f"TRANSCRIÇÃO DE ÁUDIO - {result.filename}",
            f"Duração: {result.duration_seconds:.1f} segundos",
            f"Data: {result.created_at.strftime('%d/%m/%Y %H:%M:%S') if hasattr(result, 'created_at') else 'N/A'}",
            "=" * 80,
            "",
            "⚠️ ATENÇÃO: Transcrição não disponível para este áudio.",
            "",
            "Possíveis motivos:",
            "- O áudio foi processado antes da implementação da transcrição automática",
            "- Erro durante o processamento da transcrição",
            "- Qualidade do áudio insuficiente para transcrição",
            "",
            "Para obter a transcrição, por favor faça o upload novamente.",
            ""
        ]
        
        transcription = "\n".join(transcription_lines)
    else:
        # Formata transcrição existente
        transcription_lines = [
            f"TRANSCRIÇÃO DE ÁUDIO - {result.filename}",
            f"Duração: {result.duration_seconds:.1f} segundos",
            f"Data: {result.created_at.strftime('%d/%m/%Y %H:%M:%S') if hasattr(result, 'created_at') else 'N/A'}",
            "=" * 80,
            "",
            "TRANSCRIÇÃO COMPLETA:",
            "",
            transcription,
            "",
            "=" * 80,
            "",
            "Esta transcrição foi gerada automaticamente pelo sistema Gemini 2.5 Flash.",
            "A precisão pode variar dependendo da qualidade do áudio e clareza da fala.",
        ]
        transcription = "\n".join(transcription_lines)
    
    # Prepara o arquivo para download
    filename = f"transcricao_{analysis_id[:8]}.txt"
    
    logger.info(f"Download de transcrição solicitado: {analysis_id}, arquivo: {filename}")
    
    return Response(
        content=transcription.encode('utf-8'),
        media_type='text/plain; charset=utf-8',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
    )
