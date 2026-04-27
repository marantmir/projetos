"""
Serviço de análise de áudio para detecção de indicadores psicológicos.

Implementa pipeline de extração de features acústicas (MFCC, pitch, energia),
segmentação temporal, classificação de indicadores de depressão, ansiedade
e trauma, e geração de relatório com Gemini.
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import librosa
import numpy as np

from app.core.config import settings
from app.core.logging_config import get_logger
from app.core.security import generate_analysis_id
from app.models.enums import AnomalyType, RiskLevel, ConsultationType
from app.models.schemas import AudioAnalysisResult, AudioSegment
from app.services.gemini_service import GeminiService

logger = get_logger(__name__)


class AudioService:
    """
    Serviço de análise de áudio para consultas médicas.
    
    Pipeline:
    1. Carrega áudio e extrai features acústicas (librosa)
    2. Segmenta em janelas com overlap
    3. Classifica indicadores psicológicos por segmento
    4. Transcreve com Gemini (nativo)
    5. Gera relatório psicológico
    
    Features extraídas:
    - MFCC (Mel-Frequency Cepstral Coefficients): 13 coeficientes
    - Energia RMS (Root Mean Square)
    - Zero Crossing Rate
    - Spectral Centroid
    - Pitch (F0) usando librosa.pyin
    
    Attributes:
        gemini_service: Serviço de geração de relatórios e transcrição.
    """
    
    def __init__(self, gemini_service: GeminiService):
        """
        Inicializa o serviço de análise de áudio.
        
        Args:
            gemini_service: Instância do GeminiService.
        """
        self.gemini_service = gemini_service
    
    async def process_audio(
        self,
        file_path: str,
        analysis_id: Optional[str] = None,
        consultation_type: ConsultationType = ConsultationType.GENERAL,
        patient_data: Optional['PatientData'] = None
    ) -> AudioAnalysisResult:
        """
        Processa um arquivo de áudio completo.
        
        Args:
            file_path: Caminho do arquivo de áudio.
            analysis_id: ID único da análise (gerado automaticamente se None).
            consultation_type: Tipo de consulta médica (ginecológica, pré-natal, pós-parto, geral).
            patient_data: Dados da paciente (opcional).
        
        Returns:
            Resultado completo da análise com segmentos, indicadores e relatório.
        """
        start_time = time.time()
        
        if analysis_id is None:
            analysis_id = generate_analysis_id()
        
        logger.info(f"Iniciando análise de áudio: {file_path} (ID: {analysis_id})")
        
        audio_path = Path(file_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Arquivo de áudio não encontrado: {file_path}")
        
        # Para arquivos .webm, usa processamento simplificado (sem librosa)
        if audio_path.suffix.lower() == ".webm":
            logger.info("Arquivo WebM detectado - usando processamento simplificado")
            return await self._process_webm_audio(
                file_path=file_path,
                analysis_id=analysis_id,
                consultation_type=consultation_type,
                patient_data=patient_data
            )
        
        # Carrega áudio com librosa (para outros formatos)
        y, sr = librosa.load(file_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)
        
        logger.info(f"Áudio carregado: {duration:.1f}s, sample rate: {sr} Hz")
        
        # Segmenta o áudio
        segments = self._segment_audio(y, sr, duration)
        logger.info(f"Áudio segmentado em {len(segments)} segmentos")
        
        # Analisa cada segmento
        analyzed_segments = []
        for seg_audio, start_time_seg, end_time_seg in segments:
            # Extrai features
            features = self._extract_features(seg_audio, sr)
            
            # Classifica indicadores psicológicos
            indicators, confidence = self._classify_segment(features, transcript=None)
            
            # Determina tom emocional
            emotional_tone = self._determine_emotional_tone(features, indicators)
            
            segment = AudioSegment(
                start_time=start_time_seg,
                end_time=end_time_seg,
                transcript=None,  # Será preenchido pelo Gemini se disponível
                indicators=indicators,
                confidence=confidence,
                emotional_tone=emotional_tone
            )
            
            analyzed_segments.append(segment)
        
        # Calcula risco geral
        overall_risk = self._compute_overall_risk(analyzed_segments)
        
        logger.info(f"Análise de áudio concluída. Risco geral: {overall_risk}")
        
        # Gera transcrição do áudio com Gemini
        logger.info("Gerando transcrição do áudio...")
        try:
            transcription = await self.gemini_service.transcribe_audio(file_path)
        except Exception as e:
            logger.error(f"Erro ao transcrever áudio: {e}")
            transcription = None
        
        # Cria resultado temporário para gerar relatório
        temp_result = AudioAnalysisResult(
            analysis_id=analysis_id,
            consultation_type=consultation_type,
            filename=audio_path.name,
            duration_seconds=duration,
            segments=analyzed_segments,
            overall_risk_level=overall_risk,
            gemini_report="",
            transcription=transcription,
            processing_time_seconds=0.0,
            created_at=datetime.utcnow(),
            patient_data=patient_data
        )
        
        # Gera relatório com Gemini
        try:
            gemini_report = await self.gemini_service.generate_audio_report(temp_result)
        except Exception as e:
            logger.error(f"Erro ao gerar relatório Gemini: {e}")
            gemini_report = "Relatório indisponível devido a erro temporário."
        
        processing_time = time.time() - start_time
        
        # Resultado final
        result = AudioAnalysisResult(
            consultation_type=consultation_type,
            analysis_id=analysis_id,
            filename=audio_path.name,
            duration_seconds=duration,
            segments=analyzed_segments,
            overall_risk_level=overall_risk,
            gemini_report=gemini_report,
            transcription=transcription,
            processing_time_seconds=processing_time,
            created_at=datetime.utcnow(),
            patient_data=patient_data
        )
        
        logger.info(
            f"Análise de áudio concluída: {analysis_id} em {processing_time:.2f}s "
            f"({len(analyzed_segments)} segmentos, risco: {overall_risk})"
        )
        
        return result
    
    async def _process_webm_audio(
        self,
        file_path: str,
        analysis_id: str,
        consultation_type: ConsultationType,
        patient_data: Optional['PatientData'] = None
    ) -> AudioAnalysisResult:
        """
        Processa arquivo de áudio WebM sem usar librosa (que requer FFmpeg).
        
        Usa transcrição do Gemini e cria segmentos simulados para o relatório.
        
        Args:
            file_path: Caminho do arquivo WebM.
            analysis_id: ID da análise.
            consultation_type: Tipo de consulta.
            patient_data: Dados da paciente (opcional).
        
        Returns:
            Resultado da análise de áudio.
        """
        start_time = time.time()
        audio_path = Path(file_path)
        
        logger.info(f"Processando WebM: {audio_path.name}")
        
        # Estima duração baseada no tamanho do arquivo (aproximado: ~20KB/segundo para WebM)
        file_size = audio_path.stat().st_size
        estimated_duration = max(10.0, file_size / (20 * 1024))  # Mínimo 10 segundos
        logger.info(f"Duração estimada do WebM: {estimated_duration:.1f}s (baseado em {file_size / 1024:.1f}KB)")
        
        # Gera transcrição do áudio com Gemini
        logger.info("Gerando transcrição do áudio WebM...")
        try:
            transcription = await self.gemini_service.transcribe_audio(file_path)
            if not transcription or transcription.startswith("[Transcrição não disponível"):
                logger.warning("Transcrição Gemini falhou ou retornou mensagem de erro")
                transcription = "[Transcrição não disponível para este áudio WebM. O formato pode não ser compatível com o serviço de transcrição.]"
        except Exception as e:
            logger.error(f"Erro ao transcrever áudio WebM: {e}", exc_info=True)
            transcription = f"[Transcrição não disponível - erro: {str(e)[:100]}]"
        
        # Cria segmentos simulados (a cada 10 segundos)
        num_segments = max(1, int(estimated_duration / 10))
        segment_duration = estimated_duration / num_segments
        
        analyzed_segments = []
        for i in range(num_segments):
            start_time_seg = i * segment_duration
            end_time_seg = min((i + 1) * segment_duration, estimated_duration)
            
            # Indicadores baseados em análise heurística
            # Para WebM (gravações), geralmente há menos indicadores detectáveis sem análise acústica
            indicators = []
            confidence = 0.3  # Baixa confiança sem análise acústica real
            
            # Se houver transcrição, podemos fazer análise de texto básica
            if transcription:
                text_lower = transcription.lower()
                # Palavras-chave simples para indicadores
                if any(word in text_lower for word in ['triste', 'deprimida', 'não tenho vontade', 'sem energia']):
                    indicators.append(AnomalyType.DEPRESSION_INDICATOR)
                    confidence = max(confidence, 0.5)
                if any(word in text_lower for word in ['ansiosa', 'preocupada', 'nervosa', 'medo']):
                    indicators.append(AnomalyType.ANXIETY_INDICATOR)
                    confidence = max(confidence, 0.5)
            
            emotional_tone = "neutro" if not indicators else "preocupante"
            
            segment = AudioSegment(
                start_time=start_time_seg,
                end_time=end_time_seg,
                transcript=None,  # Gemini preencherá via relatório
                indicators=indicators,
                confidence=confidence,
                emotional_tone=emotional_tone
            )
            analyzed_segments.append(segment)
        
        # Calcula risco geral
        overall_risk = self._compute_overall_risk(analyzed_segments)
        logger.info(f"Análise WebM concluída. Risco geral: {overall_risk}")
        
        # Cria resultado temporário para gerar relatório
        temp_result = AudioAnalysisResult(
            analysis_id=analysis_id,
            consultation_type=consultation_type,
            filename=audio_path.name,
            duration_seconds=estimated_duration,
            segments=analyzed_segments,
            overall_risk_level=overall_risk,
            gemini_report="",
            transcription=transcription,
            processing_time_seconds=0.0,
            created_at=datetime.utcnow(),
            patient_data=patient_data
        )
        
        # Gera relatório com Gemini
        try:
            gemini_report = await self.gemini_service.generate_audio_report(temp_result)
        except Exception as e:
            logger.error(f"Erro ao gerar relatório Gemini para WebM: {e}")
            gemini_report = "Relatório indisponível devido a erro temporário."
        
        processing_time = time.time() - start_time
        
        # Resultado final
        result = AudioAnalysisResult(
            consultation_type=consultation_type,
            analysis_id=analysis_id,
            filename=audio_path.name,
            duration_seconds=estimated_duration,
            segments=analyzed_segments,
            overall_risk_level=overall_risk,
            gemini_report=gemini_report,
            transcription=transcription,
            processing_time_seconds=processing_time,
            created_at=datetime.utcnow(),
            patient_data=patient_data
        )
        
        logger.info(
            f"Análise de áudio WebM concluída: {analysis_id} em {processing_time:.2f}s "
            f"({len(analyzed_segments)} segmentos simulados, risco: {overall_risk})"
        )
        
        return result
    
    def _segment_audio(
        self,
        y: np.ndarray,
        sr: int,
        duration: float
    ) -> list[tuple[np.ndarray, float, float]]:
        """
        Segmenta o áudio em janelas com overlap.
        
        Args:
            y: Array de áudio.
            sr: Sample rate.
            duration: Duração total em segundos.
        
        Returns:
            Lista de tuplas (segmento_audio, start_time, end_time).
        """
        segment_duration = settings.AUDIO_SEGMENT_DURATION
        overlap = settings.AUDIO_SEGMENT_OVERLAP
        
        segment_samples = int(segment_duration * sr)
        hop_samples = int((segment_duration - overlap) * sr)
        
        segments = []
        start_sample = 0
        
        while start_sample < len(y):
            end_sample = min(start_sample + segment_samples, len(y))
            
            segment_audio = y[start_sample:end_sample]
            start_time = start_sample / sr
            end_time = end_sample / sr
            
            segments.append((segment_audio, start_time, end_time))
            
            start_sample += hop_samples
        
        return segments
    
    def _extract_features(self, y: np.ndarray, sr: int) -> dict:
        """
        Extrai features acústicas de um segmento de áudio.
        
        Args:
            y: Array de áudio do segmento.
            sr: Sample rate.
        
        Returns:
            Dicionário com features extraídas.
        """
        features = {}
        
        # MFCC (13 coeficientes)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        features["mfcc_mean"] = np.mean(mfcc, axis=1)
        features["mfcc_std"] = np.std(mfcc, axis=1)
        
        # Energia RMS
        rms = librosa.feature.rms(y=y)
        features["rms_mean"] = np.mean(rms)
        features["rms_std"] = np.std(rms)
        
        # Zero Crossing Rate
        zcr = librosa.feature.zero_crossing_rate(y)
        features["zcr_mean"] = np.mean(zcr)
        features["zcr_std"] = np.std(zcr)
        
        # Spectral Centroid
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        features["spectral_centroid_mean"] = np.mean(spectral_centroid)
        features["spectral_centroid_std"] = np.std(spectral_centroid)
        
        # Pitch (F0) usando librosa.pyin
        try:
            f0, voiced_flag, voiced_probs = librosa.pyin(
                y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'), sr=sr
            )
            # Remove valores NaN
            f0_valid = f0[~np.isnan(f0)]
            if len(f0_valid) > 0:
                features["pitch_mean"] = np.mean(f0_valid)
                features["pitch_std"] = np.std(f0_valid)
                features["pitch_range"] = np.max(f0_valid) - np.min(f0_valid)
            else:
                features["pitch_mean"] = 0.0
                features["pitch_std"] = 0.0
                features["pitch_range"] = 0.0
        except Exception as e:
            logger.warning(f"Erro ao extrair pitch: {e}")
            features["pitch_mean"] = 0.0
            features["pitch_std"] = 0.0
            features["pitch_range"] = 0.0
        
        # Taxa de silêncio (frames com energia muito baixa)
        silence_threshold = 0.01
        silence_rate = np.sum(rms < silence_threshold) / len(rms[0])
        features["silence_rate"] = silence_rate
        
        return features
    
    def _classify_segment(
        self,
        features: dict,
        transcript: Optional[str]
    ) -> tuple[list[AnomalyType], float]:
        """
        Classifica indicadores psicológicos em um segmento baseado nas features.
        
        Regras heurísticas baseadas em literatura de análise de voz e psicologia:
        
        Depressão:
        - Pitch baixo e monotonia (baixa variação)
        - Energia baixa consistente
        - Fala lenta (alta taxa de silêncio)
        Referência: Cummins et al. (2015) "A review of depression and suicide risk 
        assessment using speech analysis"
        
        Ansiedade:
        - Alta variação de pitch e energia
        - Fala rápida e tensa
        - ZCR elevado (tremor vocal)
        Referência: Scherer et al. (2013) "Acoustic profiles in vocal emotion expression"
        
        Trauma/Violência Doméstica:
        - Hesitações longas (pausas frequentes)
        - Combinação de baixo pitch com quedas abruptas
        - Inconsistência emocional
        Referência: Estudos qualitativos em saúde da mulher
        
        Args:
            features: Features acústicas extraídas.
            transcript: Transcrição do segmento (opcional).
        
        Returns:
            Tupla (lista_indicadores, confiança_média).
        """
        indicators = []
        confidence_scores = []
        
        pitch_mean = features.get("pitch_mean", 0)
        pitch_std = features.get("pitch_std", 0)
        rms_mean = features.get("rms_mean", 0)
        rms_std = features.get("rms_std", 0)
        silence_rate = features.get("silence_rate", 0)
        zcr_std = features.get("zcr_std", 0)
        
        # Regra 1: Depressão - pitch baixo, baixa energia, alta taxa de silêncio
        if pitch_mean < 150 and rms_mean < 0.02 and silence_rate > 0.3:
            indicators.append(AnomalyType.DEPRESSION_INDICATOR)
            confidence = min(0.9, 0.4 + (silence_rate - 0.3) * 2)
            confidence_scores.append(confidence)
        
        # Regra 2: Ansiedade - alta variação de pitch e energia
        if pitch_std > 30 and rms_std > 0.015:
            indicators.append(AnomalyType.ANXIETY_INDICATOR)
            confidence = min(0.85, 0.5 + (pitch_std - 30) / 100)
            confidence_scores.append(confidence)
        
        # Regra 3: Indicador de trauma - hesitações longas + queda de pitch
        if silence_rate > 0.4 and pitch_mean < 160:
            indicators.append(AnomalyType.DOMESTIC_VIOLENCE_INDICATOR)
            confidence = min(0.75, 0.45 + (silence_rate - 0.4) * 1.5)
            confidence_scores.append(confidence)
        
        # Regra 4: Distress vocal - alta variação de ZCR (tremor)
        if zcr_std > 0.05:
            indicators.append(AnomalyType.VOCAL_DISTRESS)
            confidence = min(0.8, 0.5 + (zcr_std - 0.05) * 5)
            confidence_scores.append(confidence)
        
        # Calcula confiança média
        avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
        
        return indicators, float(avg_confidence)
    
    def _determine_emotional_tone(
        self,
        features: dict,
        indicators: list[AnomalyType]
    ) -> str:
        """
        Determina o tom emocional predominante do segmento.
        
        Args:
            features: Features acústicas.
            indicators: Indicadores psicológicos detectados.
        
        Returns:
            String descrevendo o tom emocional.
        """
        if AnomalyType.DEPRESSION_INDICATOR in indicators:
            return "melancólico"
        elif AnomalyType.ANXIETY_INDICATOR in indicators:
            return "ansioso/agitado"
        elif AnomalyType.DOMESTIC_VIOLENCE_INDICATOR in indicators:
            return "hesitante/retraído"
        elif AnomalyType.VOCAL_DISTRESS in indicators:
            return "angustiado"
        elif features.get("rms_mean", 0) > 0.03:
            return "energético"
        else:
            return "neutro"
    
    def _compute_overall_risk(self, segments: list[AudioSegment]) -> RiskLevel:
        """
        Calcula o nível de risco geral baseado nos segmentos analisados.
        
        Considera:
        - Prevalência de indicadores de risco
        - Severidade (tipo de indicador)
        - Confiança das detecções
        
        Args:
            segments: Lista de segmentos analisados.
        
        Returns:
            Nível de risco geral.
        """
        if not segments:
            return RiskLevel.NONE
        
        total_segments = len(segments)
        
        # Conta segmentos com indicadores de cada tipo
        depression_count = sum(
            1 for s in segments 
            if AnomalyType.DEPRESSION_INDICATOR in s.indicators
        )
        anxiety_count = sum(
            1 for s in segments 
            if AnomalyType.ANXIETY_INDICATOR in s.indicators
        )
        trauma_count = sum(
            1 for s in segments 
            if AnomalyType.DOMESTIC_VIOLENCE_INDICATOR in s.indicators
        )
        distress_count = sum(
            1 for s in segments 
            if AnomalyType.VOCAL_DISTRESS in s.indicators
        )
        
        # Calcula proporções
        depression_rate = depression_count / total_segments
        anxiety_rate = anxiety_count / total_segments
        trauma_rate = trauma_count / total_segments
        distress_rate = distress_count / total_segments
        
        # Calcula confiança média dos segmentos com indicadores
        segments_with_indicators = [s for s in segments if s.indicators]
        avg_confidence = (
            np.mean([s.confidence for s in segments_with_indicators])
            if segments_with_indicators else 0.0
        )
        
        # Lógica de classificação de risco
        # HIGH: Indicadores graves (trauma) ou múltiplos indicadores com alta confiança
        if trauma_rate > 0.2 or (depression_rate > 0.5 and avg_confidence > 0.6):
            return RiskLevel.HIGH
        
        # MEDIUM: Indicadores moderados ou combinação de indicadores
        if depression_rate > 0.3 or anxiety_rate > 0.4 or distress_rate > 0.3:
            return RiskLevel.MEDIUM
        
        # LOW: Indicadores leves
        if depression_rate > 0.1 or anxiety_rate > 0.2 or distress_rate > 0.1:
            return RiskLevel.LOW
        
        # NONE: Sem indicadores significativos
        return RiskLevel.NONE


def get_audio_service() -> AudioService:
    """
    Factory function para criar AudioService com dependências injetadas.
    
    Returns:
        Instância configurada do AudioService.
    """
    from app.services.gemini_service import get_gemini_service
    
    return AudioService(gemini_service=get_gemini_service())
