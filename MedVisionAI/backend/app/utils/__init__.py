"""Módulo de utilitários."""

from .frame_annotator import FrameAnnotator
from .video_utils import (
    get_video_info,
    extract_frame_at_timestamp,
    validate_video_file,
    resize_frame_keep_aspect,
)
from .audio_utils import (
    get_audio_info,
    validate_audio_file,
    normalize_audio,
    extract_audio_segment,
)

__all__ = [
    "FrameAnnotator",
    "get_video_info",
    "extract_frame_at_timestamp",
    "validate_video_file",
    "resize_frame_keep_aspect",
    "get_audio_info",
    "validate_audio_file",
    "normalize_audio",
    "extract_audio_segment",
]
