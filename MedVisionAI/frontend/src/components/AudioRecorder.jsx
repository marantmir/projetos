/**
 * AudioRecorder
 * 
 * Componente para gravar áudio em tempo real usando MediaRecorder API.
 */

import React, { useState, useRef } from 'react';
import { Mic, Square, Play, Pause, Trash2, Upload } from 'lucide-react';
import toast from 'react-hot-toast';

const AudioRecorder = ({ onRecordingComplete }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0);
  
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm'
      });

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        const url = URL.createObjectURL(blob);
        setAudioBlob(blob);
        setAudioUrl(url);
        chunksRef.current = [];
        
        // Para todas as tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setRecordingTime(0);

      // Timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

      toast.success('🎤 Gravação iniciada');
    } catch (error) {
      console.error('Erro ao acessar microfone:', error);
      toast.error('Erro ao acessar microfone. Verifique as permissões.');
    }
  };

  const pauseRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.pause();
      setIsPaused(true);
      clearInterval(timerRef.current);
      toast('⏸️ Gravação pausada');
    }
  };

  const resumeRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'paused') {
      mediaRecorderRef.current.resume();
      setIsPaused(false);
      
      // Retoma timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
      toast('▶️ Gravação retomada');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsPaused(false);
      clearInterval(timerRef.current);
      toast.success('✅ Gravação finalizada');
    }
  };

  const discardRecording = () => {
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }
    setAudioBlob(null);
    setAudioUrl(null);
    setRecordingTime(0);
    toast('🗑️ Gravação descartada');
  };

  const handleComplete = () => {
    if (audioBlob && onRecordingComplete) {
      // Cria File object a partir do Blob
      const file = new File([audioBlob], `gravacao_${Date.now()}.webm`, {
        type: 'audio/webm'
      });
      onRecordingComplete(file);
      toast.success('Gravação pronta! Configure o tipo de consulta e clique em "Iniciar Análise"');
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-md hover:shadow-lg transition-shadow p-8 border border-gray-200 dark:border-gray-700">
      <h3 className="text-2xl font-bold text-gray-800 dark:text-white mb-6 flex items-center">
        <Mic size={32} className="mr-3 text-sky-500" />
        Gravar Áudio em Tempo Real
      </h3>

      {/* Timer de gravação */}
      {(isRecording || audioBlob) && (
        <div className="text-center mb-6">
          <div className="text-6xl font-mono font-bold text-blue-600 dark:text-sky-400">
            {formatTime(recordingTime)}
          </div>
          {isRecording && (
            <div className="flex items-center justify-center mt-3">
              <div className="w-4 h-4 bg-red-500 rounded-full animate-pulse mr-3"></div>
              <span className="text-lg text-gray-600 dark:text-gray-400 font-semibold">
                {isPaused ? 'Pausado' : 'Gravando...'}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Controles de gravação */}
      {!audioBlob && (
        <div className="flex justify-center space-x-4 mb-6">
          {!isRecording ? (
            <button
              onClick={startRecording}
              className="px-10 py-5 bg-red-500 hover:bg-red-600 text-white text-xl rounded-2xl font-bold transition-all duration-300 flex items-center space-x-3 shadow-md hover:shadow-lg transform hover:scale-105 hover:-translate-y-1"
            >
              <Mic size={28} />
              <span>Iniciar Gravação</span>
            </button>
          ) : (
            <>
              {!isPaused ? (
                <button
                  onClick={pauseRecording}
                  className="px-6 py-5 bg-yellow-500 hover:bg-yellow-600 text-white rounded-xl transition shadow-lg text-xl font-bold"
                  title="Pausar"
                >
                  <Pause size={28} />
                </button>
              ) : (
                <button
                  onClick={resumeRecording}
                  className="px-6 py-5 bg-green-500 hover:bg-green-600 text-white rounded-xl transition shadow-lg text-xl font-bold"
                  title="Retomar"
                >
                  <Play size={28} />
                </button>
              )}
              <button
                onClick={stopRecording}
                className="px-10 py-5 bg-blue-500 hover:bg-blue-600 text-white text-xl rounded-2xl font-bold transition-all duration-300 flex items-center space-x-3 shadow-md hover:shadow-lg"
              >
                <Square size={28} />
                <span>Finalizar</span>
              </button>
            </>
          )}
        </div>
      )}

      {/* Player de áudio gravado */}
      {audioUrl && (
        <div className="space-y-6">
          <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-6">
            <p className="text-base text-gray-600 dark:text-gray-400 mb-3 font-semibold">
              Prévia da gravação:
            </p>
            <audio src={audioUrl} controls className="w-full" />
          </div>

          <div className="flex space-x-3">
            <button
              onClick={handleComplete}
              className="flex-1 px-6 py-5 bg-green-500 hover:bg-green-600 text-white text-xl rounded-2xl font-bold transition-all duration-300 flex items-center justify-center space-x-3 shadow-md hover:shadow-lg transform hover:scale-105"
            >
              <Upload size={24} />
              <span>Usar esta Gravação</span>
            </button>
            <button
              onClick={discardRecording}
              className="px-6 py-5 bg-red-500 hover:bg-red-600 text-white rounded-xl transition shadow-lg"
              title="Descartar gravação"
            >
              <Trash2 size={24} />
            </button>
          </div>
        </div>
      )}

      {/* Informações */}
      <div className="mt-6 text-base text-gray-500 dark:text-gray-400 text-center">
        <p className="mb-1">💡 Grave diretamente do seu microfone</p>
        <p className="font-semibold">Formato: WebM • Qualidade: Alta</p>
      </div>
    </div>
  );
};

export default AudioRecorder;
