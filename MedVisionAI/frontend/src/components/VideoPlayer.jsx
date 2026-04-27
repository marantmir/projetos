/**
 * Componente VideoPlayer
 * 
 * Player de vídeo com controles e overlay de bounding boxes.
 * Sincroniza frames analisados com timestamp do vídeo.
 */

import React, { useRef, useState, useEffect } from 'react';
import { Play, Pause, Volume2, VolumeX, Maximize } from 'lucide-react';
import BoundingBoxOverlay from './BoundingBoxOverlay';

const VideoPlayer = ({ videoUrl, analysisResult }) => {
  const videoRef = useRef(null);
  const containerRef = useRef(null);
  
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [currentFrame, setCurrentFrame] = useState(null);
  const [videoError, setVideoError] = useState(null);

  // Log da URL do vídeo
  useEffect(() => {
    console.log('[VideoPlayer] Initialized with videoUrl:', videoUrl);
    console.log('[VideoPlayer] Analysis result frames:', analysisResult?.frames_analysis?.length);
  }, [videoUrl, analysisResult]);

  // Atualiza frame atual baseado no timestamp
  useEffect(() => {
    if (!analysisResult?.frames_analysis) return;

    const frames = analysisResult.frames_analysis;
    
    // Encontra frame mais próximo do timestamp atual
    const closestFrame = frames.reduce((prev, curr) => {
      const prevDiff = Math.abs(prev.timestamp - currentTime);
      const currDiff = Math.abs(curr.timestamp - currentTime);
      return currDiff < prevDiff ? curr : prev;
    });

    setCurrentFrame(closestFrame);
  }, [currentTime, analysisResult]);

  // Atualiza timestamp conforme vídeo reproduz
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    let lastUpdateTime = 0;
    const THROTTLE_MS = 100; // Atualiza no máximo a cada 100ms (10 FPS)

    const handleTimeUpdate = () => {
      const now = Date.now();
      if (now - lastUpdateTime >= THROTTLE_MS) {
        setCurrentTime(video.currentTime);
        lastUpdateTime = now;
      }
    };

    const handleLoadedMetadata = () => {
      setDuration(video.duration);
      console.log('[VideoPlayer] Video loaded successfully:', {
        duration: video.duration,
        videoWidth: video.videoWidth,
        videoHeight: video.videoHeight
      });
    };

    const handleError = (e) => {
      const errorDetails = {
        error: e,
        networkState: video.networkState,
        readyState: video.readyState,
        currentSrc: video.currentSrc,
        errorCode: video.error?.code,
        errorMessage: video.error?.message
      };
      console.error('[VideoPlayer] Video error:', errorDetails);
      setVideoError(`Erro ao carregar vídeo: ${video.error?.message || 'Desconhecido'}`);
    };

    const handleCanPlay = () => {
      console.log('[VideoPlayer] Video can play');
    };

    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('loadedmetadata', handleLoadedMetadata);
    video.addEventListener('error', handleError);
    video.addEventListener('canplay', handleCanPlay);

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate);
      video.removeEventListener('loadedmetadata', handleLoadedMetadata);
      video.removeEventListener('error', handleError);
      video.removeEventListener('canplay', handleCanPlay);
    };
  }, []);

  const togglePlay = () => {
    const video = videoRef.current;
    if (!video) return;

    if (isPlaying) {
      video.pause();
    } else {
      video.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleSeek = (e) => {
    const video = videoRef.current;
    if (!video) return;

    const newTime = parseFloat(e.target.value);
    video.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const toggleMute = () => {
    const video = videoRef.current;
    if (!video) return;

    video.muted = !isMuted;
    setIsMuted(!isMuted);
  };

  const handleVolumeChange = (e) => {
    const video = videoRef.current;
    if (!video) return;

    const newVolume = parseFloat(e.target.value);
    video.volume = newVolume;
    setVolume(newVolume);
    setIsMuted(newVolume === 0);
  };

  const toggleFullscreen = () => {
    const container = containerRef.current;
    if (!container) return;

    if (!document.fullscreenElement) {
      container.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <>
      {videoError && (
        <div className="bg-red-900 text-white p-4 text-center">
          <p className="font-semibold">⚠️ {videoError}</p>
          <p className="text-sm mt-2">Verifique se o arquivo de vídeo existe no servidor.</p>
        </div>
      )}
      
      <div ref={containerRef} className="bg-gray-900 rounded-lg overflow-hidden shadow-2xl">
        {/* Container do vídeo com overlay */}
        <div className="relative bg-black" style={{ width: '100%', aspectRatio: '16/9' }}>
          {/* Vídeo */}
          <video
            ref={videoRef}
            src={videoUrl}
            className="absolute top-0 left-0 w-full h-full object-contain"
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
            crossOrigin="anonymous"
            preload="metadata"
          />
        
        {/* Overlay de bounding boxes - mesma posição e tamanho do vídeo */}
        {currentFrame && (
          <BoundingBoxOverlay
            videoRef={videoRef}
            frameAnalysis={currentFrame}
          />
        )}
      </div>

      {/* Controles */}
      <div className="bg-gray-800 p-4 space-y-3">
        {/* Barra de progresso */}
        <input
          type="range"
          min="0"
          max={duration || 0}
          step="0.1"
          value={currentTime}
          onChange={handleSeek}
          className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-medvision-primary"
        />

        {/* Controles inferiores */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {/* Play/Pause */}
            <button
              onClick={togglePlay}
              className="text-white hover:text-medvision-primary transition"
            >
              {isPlaying ? <Pause size={24} /> : <Play size={24} />}
            </button>

            {/* Volume */}
            <div className="flex items-center space-x-2">
              <button
                onClick={toggleMute}
                className="text-white hover:text-medvision-primary transition"
              >
                {isMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
              </button>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={isMuted ? 0 : volume}
                onChange={handleVolumeChange}
                className="w-20 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-medvision-primary"
              />
            </div>

            {/* Timestamp */}
            <span className="text-sm text-gray-400">
              {formatTime(currentTime)} / {formatTime(duration)}
            </span>
          </div>

          {/* Fullscreen */}
          <button
            onClick={toggleFullscreen}
            className="text-white hover:text-medvision-primary transition"
          >
            <Maximize size={20} />
          </button>
        </div>
      </div>

      {/* Informações do frame atual */}
      {currentFrame && currentFrame.bounding_boxes.length > 0 && (
        <div className="bg-gray-800 px-4 py-2 border-t border-gray-700">
          <p className="text-sm text-gray-300">
            Frame atual: <span className="font-semibold">{currentFrame.frame_number}</span> | 
            Detecções: <span className="font-semibold">{currentFrame.bounding_boxes.length}</span>
          </p>
        </div>
      )}
      </div>
    </>
  );
};

export default VideoPlayer;
