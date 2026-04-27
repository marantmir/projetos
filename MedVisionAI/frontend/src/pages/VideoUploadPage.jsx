/**
 * VideoUploadPage
 * 
 * Página específica para upload e análise de vídeos cirúrgicos.
 * Detecta instrumentos cirúrgicos e anomalias com YOLOv8.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, Video, FileWarning, Loader, Play, Scissors, AlertTriangle } from 'lucide-react';
import useVideoAnalysis from '../hooks/useVideoAnalysis';
import toast from 'react-hot-toast';

const VideoUploadPage = () => {
  const navigate = useNavigate();
  const videoAnalysis = useVideoAnalysis();

  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [videoPlayable, setVideoPlayable] = useState(true);

  const VIDEO_FORMATS = ['video/mp4', 'video/avi', 'video/mov', 'video/mkv', 'video/webm'];
  const MAX_FILE_SIZE = 500 * 1024 * 1024; // 500 MB

  // Cleanup blob URL quando componente desmontar ou arquivo mudar
  useEffect(() => {
    return () => {
      if (previewUrl) {
        console.log('[VideoUpload] Cleaning up blob URL:', previewUrl);
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      validateAndSetFile(files[0]);
    }
  };

  const handleFileSelect = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      validateAndSetFile(files[0]);
    }
  };

  const validateAndSetFile = (file) => {
    console.log('[VideoUpload] Validating file:', {
      name: file.name,
      size: file.size,
      type: file.type,
      lastModified: file.lastModified
    });

    // Valida tamanho
    if (file.size > MAX_FILE_SIZE) {
      toast.error('Arquivo muito grande! Máximo: 500 MB');
      return;
    }

    // Valida formato (aceita qualquer vídeo se o tipo não estiver na lista)
    const isVideoFile = file.type.startsWith('video/') || file.name.match(/\.(mp4|avi|mov|mkv|webm)$/i);
    if (!isVideoFile && !VIDEO_FORMATS.includes(file.type)) {
      toast.error('Formato não suportado! Use MP4, AVI, MOV, MKV ou WebM.');
      return;
    }

    // Limpa URL anterior se existir
    if (previewUrl) {
      console.log('[VideoUpload] Revoking previous blob URL');
      URL.revokeObjectURL(previewUrl);
    }

    // Cria blob URL para preview
    try {
      const url = URL.createObjectURL(file);
      console.log('[VideoUpload] Created blob URL:', url);
      
      setPreviewUrl(url);
      setSelectedFile(file);
      toast.success(`Vídeo selecionado: ${file.name}`, {
        duration: 3000
      });
    } catch (error) {
      console.error('[VideoUpload] Error creating blob URL:', error);
      toast.error('Erro ao criar preview do vídeo');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error('Selecione um vídeo primeiro!');
      return;
    }

    try {
      console.log('[VideoUpload] Starting upload for file:', selectedFile.name);
      const analysisId = await videoAnalysis.upload(selectedFile);
      console.log('[VideoUpload] Upload returned analysisId:', analysisId);
      
      if (!analysisId) {
        console.error('[VideoUpload] No analysisId returned from upload!');
        toast.error('Erro: Upload não retornou ID de análise');
        return;
      }
      
      console.log('[VideoUpload] Navigating to:', `/analysis/${analysisId}?type=video`);
      navigate(`/analysis/${analysisId}?type=video`);
    } catch (error) {
      console.error('[VideoUpload] Upload error:', error);
      toast.error(error.message || 'Erro ao fazer upload do vídeo');
    }
  };

  const handleRemoveFile = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setSelectedFile(null);
    setPreviewUrl(null);
  };

  return (
    <div className="max-w-7xl mx-auto px-8">
      {/* Header */}
      <div className="mb-12 py-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <div className="p-5 bg-gradient-to-br from-blue-500 to-sky-500 rounded-2xl shadow-md">
              <Video size={48} className="text-white" />
            </div>
            <div>
              <h1 className="text-6xl md:text-7xl font-bold bg-gradient-to-r from-blue-600 to-sky-600 bg-clip-text text-transparent dark:text-white mb-3 tracking-tight">
                Análise de Vídeos Cirúrgicos
              </h1>
              <p className="text-2xl text-gray-600 dark:text-gray-300">
                Detecção de instrumentos cirúrgicos e anomalias com IA
              </p>
            </div>
          </div>
        </div>

        {/* Informações */}
        <div className="bg-blue-50 dark:bg-blue-900 dark:bg-opacity-20 border-2 border-blue-300 dark:border-blue-700 rounded-2xl p-8 shadow-lg">
          <div className="flex items-start space-x-4">
            <div className="p-3 bg-blue-600 rounded-xl">
              <Play size={28} className="text-white" />
            </div>
            <div className="flex-1">
              <h3 className="font-bold text-2xl text-blue-900 dark:text-blue-100 mb-4">O que será analisado:</h3>
              <ul className="text-lg text-blue-800 dark:text-blue-200 space-y-3">
                <li className="flex items-start"><Scissors size={20} className="mr-3 mt-1" /><span>Detecção de instrumentos cirúrgicos (pinças, tesouras, bisturis, etc.)</span></li>
                <li className="flex items-start"><AlertTriangle size={20} className="mr-3 mt-1" /><span>Identificação de anomalias e sangramento excessivo</span></li>
                <li className="flex items-start"><span className="mr-3 text-2xl">📊</span><span>Distribuição temporal de instrumentos ao longo do procedimento</span></li>
                <li className="flex items-start"><span className="mr-3 text-2xl">📋</span><span>Relatório detalhado com modelo <strong>Gemini 2.5 Flash</strong></span></li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Área de upload */}
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-10">
        {!selectedFile ? (
          <div
            onDragEnter={handleDragEnter}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`
              border-3 border-dashed rounded-2xl p-16 text-center
              transition-all duration-300 cursor-pointer
              ${isDragging 
                ? 'border-medvision-primary bg-medvision-primary bg-opacity-10 scale-[1.02] shadow-xl' 
                : 'border-gray-400 dark:border-gray-600 hover:border-medvision-primary dark:hover:border-medvision-primary hover:bg-gray-50 dark:hover:bg-gray-700'
              }
            `}
          >
            <Upload size={80} className="mx-auto text-gray-400 dark:text-gray-500 mb-6" />
            <h2 className="text-3xl font-bold text-gray-800 dark:text-white mb-4">
              Arraste o vídeo ou clique para selecionar
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">
              Formatos suportados: MP4, AVI, MOV, MKV, WebM (máx. 500 MB)
            </p>
            <input
              type="file"
              id="video-upload"
              accept="video/*"
              onChange={handleFileSelect}
              className="hidden"
            />
            <label
              htmlFor="video-upload"
              className="inline-block px-12 py-5 bg-gradient-to-r from-blue-500 to-sky-500 text-white text-xl font-bold rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 cursor-pointer"
            >
              📁 Selecionar Vídeo
            </label>
          </div>
        ) : (
          <div>
            {/* Preview do vídeo */}
            <div className="mb-6 relative">
              <video
                key={`video-${previewUrl}`}
                src={previewUrl}
                controls
                preload="auto"
                playsInline
                className="w-full rounded-2xl shadow-lg max-h-96 border-4 border-blue-200"
                style={{ backgroundColor: '#000', objectFit: 'contain' }}
                onError={(e) => {
                  const video = e.target;
                  const errorInfo = {
                    previewUrl,
                    src: video.src,
                    currentSrc: video.currentSrc,
                    networkState: video.networkState,
                    networkStateText: ['EMPTY', 'IDLE', 'LOADING', 'NO_SOURCE'][video.networkState],
                    readyState: video.readyState,
                    readyStateText: ['HAVE_NOTHING', 'HAVE_METADATA', 'HAVE_CURRENT_DATA', 'HAVE_FUTURE_DATA', 'HAVE_ENOUGH_DATA'][video.readyState],
                    error: video.error,
                    errorCode: video.error?.code,
                    errorCodeText: video.error ? ['', 'ABORTED', 'NETWORK', 'DECODE', 'SRC_NOT_SUPPORTED'][video.error.code] : null,
                    errorMessage: video.error?.message,
                    videoWidth: video.videoWidth,
                    videoHeight: video.videoHeight,
                    duration: video.duration
                  };
                  console.error('[VideoUpload] Preview error:', errorInfo);
                  
                  setVideoPlayable(false);
                  
                  if (video.error?.code === 4 || errorInfo.networkStateText === 'NO_SOURCE') {
                    console.log('[VideoUpload] Video codec not supported for browser playback - upload will still work');
                  }
                }}
                onLoadedMetadata={(e) => {
                  console.log('[VideoUpload] Video loaded successfully:', {
                    previewUrl,
                    duration: e.target.duration,
                    width: e.target.videoWidth,
                    height: e.target.videoHeight,
                    readyState: e.target.readyState
                  });
                  setVideoPlayable(true);
                }}
                onLoadStart={() => {
                  console.log('[VideoUpload] Video load started:', previewUrl);
                  setVideoPlayable(true); // Assume que vai funcionar até dar erro
                }}
                onCanPlay={() => {
                  console.log('[VideoUpload] Video can play');
                  setVideoPlayable(true);
                }}
                onCanPlayThrough={() => {
                  console.log('[VideoUpload] Video can play through');
                }}
                onLoadedData={() => {
                  console.log('[VideoUpload] Video data loaded');
                }}
                onSuspend={(e) => {
                  console.log('[VideoUpload] Video suspended:', e.target.readyState);
                }}
                onAbort={() => {
                  console.log('[VideoUpload] Video aborted');
                }}
                onStalled={() => {
                  console.log('[VideoUpload] Video stalled');
                }}
                onWaiting={() => {
                  console.log('[VideoUpload] Video waiting');
                }}
                onProgress={(e) => {
                  if (e.target.buffered.length > 0) {
                    const buffered = e.target.buffered.end(0);
                    console.log('[VideoUpload] Video progress:', buffered);
                  }
                }}
              >
                Seu navegador não suporta a reprodução de vídeos.
              </video>
              
              {/* Overlay de erro */}
              {!videoPlayable && (
                <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-95 rounded-2xl z-10 p-8">
                  <div className="text-center text-white max-w-md">
                    <Video size={64} className="mx-auto mb-4 text-yellow-400" />
                    <h3 className="text-xl font-bold mb-2">⚠️ Preview não disponível</h3>
                    <p className="text-gray-300 mb-4">
                      O codec deste vídeo não é suportado para visualização no navegador.
                    </p>
                    <p className="text-sm text-green-400 font-semibold">
                      ✅ Você pode prosseguir com o upload normalmente - o backend processará o vídeo corretamente!
                    </p>
                  </div>
                </div>
              )}
              
              {/* Informação de debug */}
              <div className="mt-2 text-xs text-gray-500 bg-gray-100 dark:bg-gray-800 rounded p-2">
                <p><strong>Arquivo:</strong> {selectedFile?.name}</p>
                <p><strong>Tipo:</strong> {selectedFile?.type}</p>
                <p><strong>Tamanho:</strong> {(selectedFile?.size / 1024 / 1024).toFixed(2)} MB</p>
                {!videoPlayable && (
                  <p className="text-yellow-600 dark:text-yellow-400 font-semibold mt-2">
                    ⚠️ Preview indisponível - Upload funcionará normalmente
                  </p>
                )}
              </div>
            </div>

            {/* Informações do arquivo */}
            <div className="bg-gray-100 dark:bg-gray-700 rounded-xl p-6 mb-8 shadow-md">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-bold text-xl text-gray-800 dark:text-white">{selectedFile.name}</p>
                  <p className="text-lg text-gray-600 dark:text-gray-400 mt-1">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                <button
                  onClick={handleRemoveFile}
                  className="px-6 py-3 text-lg font-semibold text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900 dark:hover:bg-opacity-30 rounded-xl transition shadow-md"
                >
                  🗑️ Remover
                </button>
              </div>
            </div>

            {/* Botão de upload */}
            {videoAnalysis.isUploading ? (
              <div className="text-center">
                <Loader size={48} className="mx-auto text-medvision-primary animate-spin mb-4" />
                <p className="text-gray-600 mb-2">Enviando vídeo...</p>
                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div
                    className="bg-medvision-primary h-full transition-all duration-300"
                    style={{ width: `${videoAnalysis.uploadProgress}%` }}
                  />
                </div>
                <p className="text-sm text-gray-500 mt-2">
                  {videoAnalysis.uploadProgress}%
                </p>
              </div>
            ) : (
              <button
                onClick={handleUpload}
                className="w-full py-6 bg-gradient-to-r from-blue-500 to-sky-500 text-white rounded-2xl font-bold text-2xl shadow-md hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-1"
              >
                🚀 Iniciar Análise
              </button>
            )}
          </div>
        )}
      </div>

      {/* Especificações técnicas */}
      <div className="mt-10 text-center text-lg text-gray-600 dark:text-gray-400 py-4">
        <p>
          🤖 Modelo de detecção: <strong>YOLOv8n</strong> | 
          🧠 IA generativa: <strong>Gemini 2.5 Flash</strong>
        </p>
      </div>
    </div>
  );
};

export default VideoUploadPage;
