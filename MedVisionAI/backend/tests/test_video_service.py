"""
Testes do VideoService.

Valida o pipeline completo de análise de vídeo, incluindo extração de frames,
detecção com YOLO e geração de relatório com Gemini.
"""

import pytest

from app.services.video_service import VideoService
from app.models.enums import SeverityLevel


@pytest.mark.asyncio
async def test_process_video_returns_result(
    sample_video_path,
    mock_yolo_service,
    mock_gemini_service
):
    """Testa que process_video retorna um VideoAnalysisResult válido."""
    from app.services import get_yolo_service, get_gemini_service
    
    video_service = VideoService(
        yolo_service=get_yolo_service(),
        gemini_service=get_gemini_service()
    )
    
    result = await video_service.process_video(
        file_path=sample_video_path,
        analysis_id="test-123"
    )
    
    assert result.analysis_id == "test-123"
    assert result.total_frames_analyzed > 0
    assert result.duration_seconds > 0
    assert result.gemini_report != ""
    assert isinstance(result.anomaly_summary, dict)


def test_detect_frame_returns_bounding_boxes(mock_yolo_service, mock_yolo_detections):
    """Testa que detect_frame retorna lista de BoundingBox."""
    from app.services import get_yolo_service
    import numpy as np
    
    yolo_service = get_yolo_service()
    
    # Frame dummy
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    boxes = yolo_service.detect_frame(frame)
    
    assert isinstance(boxes, list)
    assert len(boxes) == len(mock_yolo_detections)
    assert all(hasattr(box, 'confidence') for box in boxes)


def test_severity_critical_on_bleeding(mock_yolo_service):
    """Testa que sangramento com alta confiança resulta em severidade crítica."""
    from app.services import get_yolo_service
    from app.models.schemas import BoundingBox
    from app.models.enums import AnomalyType
    
    yolo_service = get_yolo_service()
    
    # Box de sangramento com confiança alta
    bleeding_box = BoundingBox(
        x1=100, y1=100, x2=200, y2=200,
        confidence=0.85,
        label="blood",
        anomaly_type=AnomalyType.SURGICAL_BLEEDING
    )
    
    severity = yolo_service.classify_severity([bleeding_box])
    
    assert severity == SeverityLevel.CRITICAL
