/**
 * Página AnalysisPage
 * 
 * Página principal de visualização de análise em andamento ou concluída.
 * Integra VideoPlayer, AlertPanel e exibe progresso via WebSocket.
 */

import React, { useEffect, useState } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { Loader, CheckCircle, XCircle, ArrowLeft, Download } from 'lucide-react';
import VideoPlayer from '../components/VideoPlayer';
import AlertPanel from '../components/AlertPanel';
import MarkdownRenderer from '../components/MarkdownRenderer';
import useWebSocket from '../hooks/useWebSocket';
import useVideoAnalysis from '../hooks/useVideoAnalysis';
import useAudioAnalysis from '../hooks/useAudioAnalysis';
import { downloadReportMarkdown } from '../services/api';
import toast from 'react-hot-toast';

const AnalysisPage = () => {
  const { analysisId } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const type = searchParams.get('type'); // 'video' ou 'audio'
  
  console.log('[AnalysisPage] Component render - analysisId:', analysisId, 'type:', type);
  
  const { isConnected, progress, alerts, isCompleted } = useWebSocket(analysisId);
  const videoAnalysis = useVideoAnalysis();
  const audioAnalysis = useAudioAnalysis();

  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [status, setStatus] = useState(null);

  // Debug: Log state changes
  useEffect(() => {
    console.log('[AnalysisPage] State updated:', { result: !!result, error, status });
  }, [result, error, status]);

  // Transforma resposta da API para formato esperado pelos componentes
  const transformResult = (apiResult) => {
    if (!apiResult) return null;

    console.log('[AnalysisPage] Transforming API result:', apiResult);

    // URL base da API
    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    // Transforma frames: frames -> frames_analysis, timestamp_seconds -> timestamp
    const framesAnalysis = (apiResult.frames || []).map(frame => ({
      ...frame,
      timestamp: frame.timestamp_seconds, // Adiciona campo esperado
      bounding_boxes: (frame.bounding_boxes || []).map(bb => ({
        x_min: bb.x1,
        y_min: bb.y1,
        x_max: bb.x2,
        y_max: bb.y2,
        confidence: bb.confidence,
        class_name: bb.label,
        anomaly_type: bb.anomaly_type || 'unknown',
        severity: frame.severity || 'low'
      }))
    }));

    const transformed = {
      ...apiResult,
      frames_analysis: framesAnalysis,
      // IMPORTANTE: Preserva dimensões originais do vídeo
      video_width: apiResult.video_width,
      video_height: apiResult.video_height,
      metadata: {
        file_path: `${API_BASE_URL}/api/v1/video/download/${apiResult.analysis_id}`,
        duration: apiResult.duration_seconds,
        filename: apiResult.filename
      }
    };

    console.log('[AnalysisPage] Transformed result:', transformed);
    console.log('[AnalysisPage] Video dimensions:', {
      width: transformed.video_width,
      height: transformed.video_height
    });
    return transformed;
  };

  // Polling ativo de status (a cada 2 segundos) até concluir
  useEffect(() => {
    console.log('[AnalysisPage] Polling useEffect triggered - analysisId:', analysisId, 'typeof:', typeof analysisId);
    
    // Verifica se tem ID válido
    if (!analysisId || analysisId === 'null' || analysisId === 'undefined') {
      console.warn('[AnalysisPage] No valid analysis ID, redirecting to home');
      toast.error('ID de análise inválido');
      navigate('/');
      return;
    }

    if (result || error) return; // Já tem resultado, não precisa mais fazer polling

    const pollStatus = async () => {
      try {
        const statusData = type === 'video' 
          ? await videoAnalysis.fetchStatus(analysisId)
          : await audioAnalysis.fetchStatus(analysisId);
        
        setStatus(statusData.status);

        // Se completou, busca resultado
        if (statusData.status === 'completed') {
          console.log('[AnalysisPage] Analysis completed, fetching result...');
          const resultData = type === 'video'
            ? await videoAnalysis.fetchResult(analysisId)
            : await audioAnalysis.fetchResult(analysisId);
          
          console.log('[AnalysisPage] Raw API result:', resultData);
          const transformed = transformResult(resultData);
          console.log('[AnalysisPage] Setting transformed result:', transformed);
          setResult(transformed);
          toast.success('Análise concluída!');
        } else if (statusData.status === 'error') {
          setError(statusData.error_message || 'Erro na análise');
          toast.error('Erro na análise');
        }
      } catch (err) {
        console.error('Erro ao verificar status:', err);
      }
    };

    // Poll inicial
    pollStatus();

    // Poll a cada 2 segundos
    const interval = setInterval(pollStatus, 2000);

    return () => clearInterval(interval);
  }, [analysisId, type, result, error]);

  // Fallback: busca resultado quando WebSocket notifica conclusão
  useEffect(() => {
    // Verifica se tem ID válido
    if (!analysisId || analysisId === 'null' || analysisId === 'undefined') {
      return;
    }

    if (!isCompleted || result) return;

    const fetchResult = async () => {
      try {
        const data = type === 'video'
          ? await videoAnalysis.fetchResult(analysisId)
          : await audioAnalysis.fetchResult(analysisId);
        
        const transformed = transformResult(data);
        setResult(transformed);
        toast.success('Análise concluída!');
      } catch (err) {
        setError('Erro ao carregar resultado');
        toast.error('Erro ao carregar resultado');
      }
    };

    fetchResult();
  }, [isCompleted, analysisId, type, result]);

  const handleDownloadReport = async () => {
    try {
      await downloadReportMarkdown(analysisId, type);
      toast.success('Relatório baixado!');
    } catch (err) {
      toast.error('Erro ao baixar relatório');
    }
  };

  const handleDownloadTranscription = async () => {
    try {
      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/api/v1/audio/download-transcription/${analysisId}`);
      
      if (!response.ok) {
        throw new Error('Erro ao baixar transcrição');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `transcricao_${analysisId.substring(0, 8)}.txt`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success('Transcrição baixada!');
    } catch (err) {
      console.error('Erro ao baixar transcrição:', err);
      toast.error('Erro ao baixar transcrição');
    }
  };

  return (
    <div className="min-h-screen bg-white dark:bg-gradient-to-br dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-10 transition-colors">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-10">
        <div className="flex items-center justify-between">
          <button
            onClick={() => navigate('/')}
            className="flex items-center text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition text-lg font-semibold"
          >
            <ArrowLeft size={24} className="mr-3" />
            Voltar
          </button>
          
          <div className="flex items-center space-x-6">
            <div className="text-right">
              <p className="text-gray-600 dark:text-gray-400 text-base">ID da Análise</p>
              <p className="text-gray-900 dark:text-white font-mono text-lg font-bold">{analysisId}</p>
            </div>
            
            <button
              onClick={handleDownloadReport}
              className="
                flex items-center px-8 py-5 bg-gradient-to-r from-blue-500 to-sky-500 text-white 
                rounded-2xl text-xl font-bold shadow-md hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-1
              "
            >
              <Download size={24} className="mr-3" />
              Baixar Relatório
            </button>
          </div>
        </div>
      </div>

      {/* Status da conexão WebSocket */}
      <div className="max-w-7xl mx-auto mb-6">
        <div className={`
          flex items-center px-6 py-4 rounded-2xl text-base font-semibold shadow-md border
          ${isConnected ? 'bg-green-50 dark:bg-green-900 text-green-800 dark:text-green-200 border-green-200 dark:border-green-700' : 'bg-yellow-50 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 border-yellow-200 dark:border-yellow-700'}
        `}>
          {isConnected ? (
            <>
              <CheckCircle size={20} className="mr-3" />
              Conectado ao servidor (tempo real) - Em breve seu relatório será gerado
            </>
          ) : (
            <>
              <Loader className="animate-spin mr-3" size={20} />
              Conectando...
            </>
          )}
        </div>
      </div>

      {/* Grid principal */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Coluna esquerda: Player/Visualização (3/4) */}
        <div className="lg:col-span-3 space-y-8">
          {/* Barra de progresso */}
          {!isCompleted && progress && (
            <div className="bg-white dark:bg-gray-800 rounded-3xl p-8 shadow-md hover:shadow-lg transition-shadow border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-gray-800 dark:text-white font-bold text-xl">Progresso da Análise</h3>
                <span className="text-blue-600 dark:text-sky-400 font-bold text-2xl">
                  {progress.progress_percentage?.toFixed(0) || 0}%
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-5 overflow-hidden mb-3 shadow-inner">
                <div
                  className="bg-gradient-to-r from-medvision-primary to-medvision-accent h-full transition-all duration-500"
                  style={{ width: `${progress.progress_percentage || 0}%` }}
                />
              </div>
              <p className="text-gray-600 dark:text-gray-400 text-base">
                {progress.message || 'Processando...'}
              </p>
            </div>
          )}

          {/* Player de vídeo (se tipo video e resultado disponível) */}
          {type === 'video' && result && (
            <>
              {console.log('[AnalysisPage] Rendering VideoPlayer with URL:', result.metadata?.file_path)}
              {console.log('[AnalysisPage] Frames count:', result.frames_analysis?.length)}
              <VideoPlayer
                videoUrl={result.metadata?.file_path || '#'}
                analysisResult={result}
              />
            </>
          )}

          {/* Visualização de áudio (placeholder) */}
          {type === 'audio' && result && (
            <div className="bg-white dark:bg-gray-800 rounded-3xl p-8 shadow-md hover:shadow-lg transition-shadow border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-gray-900 dark:text-white font-bold text-2xl">Análise de Áudio</h3>
                <button
                  onClick={handleDownloadTranscription}
                  className="
                    flex items-center px-5 py-3 bg-gradient-to-r from-green-500 to-emerald-500 text-white 
                    rounded-xl font-bold shadow-md hover:shadow-xl transition-all duration-300 transform hover:scale-105
                  "
                >
                  <Download size={18} className="mr-2" />
                  Baixar Transcrição
                </button>
              </div>
              <div className="space-y-5">
                <div>
                  <p className="text-gray-600 dark:text-gray-400 text-base mb-1">Duração</p>
                  <p className="text-gray-900 dark:text-white font-bold text-xl">
                    {result.duration?.toFixed(2) || 0}s
                  </p>
                </div>
                <div>
                  <p className="text-gray-600 dark:text-gray-400 text-base mb-1">Segmentos Analisados</p>
                  <p className="text-gray-900 dark:text-white font-bold text-xl">
                    {result.segments?.length || 0}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600 dark:text-gray-400 text-base mb-3">Indicadores Detectados</p>
                  <div className="flex flex-wrap gap-3 mt-2">
                    {result.segments?.slice(0, 5).map((seg, idx) => (
                      <span
                        key={idx}
                        className="px-4 py-2 bg-blue-500 dark:bg-sky-500 text-white rounded-2xl text-base font-semibold shadow-sm"
                      >
                        {seg.psychological_indicator}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Relatório Gemini */}
          {result?.gemini_report && (
            <MarkdownRenderer
              content={result.gemini_report}
              title={type === 'video' ? '📹 Relatório Clínico - Vídeo Cirúrgico' : '🎤 Relatório Clínico - Análise de Áudio'}
              filename={`relatorio_${analysisId}.md`}
            />
          )}

          {/* Estado de erro */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900 dark:bg-opacity-20 border-2 border-red-300 dark:border-red-500 rounded-2xl p-8 flex items-center shadow-xl">
              <XCircle size={32} className="text-red-600 dark:text-red-500 mr-4" />
              <div>
                <h3 className="text-red-800 dark:text-red-400 font-bold text-xl mb-2">Erro na Análise</h3>
                <p className="text-gray-700 dark:text-gray-300 text-base">{error}</p>
              </div>
            </div>
          )}
        </div>

        {/* Coluna direita: Alertas (1/4) */}
        <div className="lg:col-span-1">
          <AlertPanel alerts={alerts} />
        </div>
      </div>
    </div>
  );
};

export default AnalysisPage;
