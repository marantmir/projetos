/**
 * Página UploadPage
 * 
 * Interface de upload com drag & drop para vídeos e áudios.
 * Valida formatos, tamanhos e inicia análise.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, Video, Music, FileWarning, Loader } from 'lucide-react';
import useVideoAnalysis from '../hooks/useVideoAnalysis';
import useAudioAnalysis from '../hooks/useAudioAnalysis';
import toast from 'react-hot-toast';

const UploadPage = () => {
  const navigate = useNavigate();
  const videoAnalysis = useVideoAnalysis();
  const audioAnalysis = useAudioAnalysis();

  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileType, setFileType] = useState(null); // 'video' ou 'audio'

  const VIDEO_FORMATS = ['video/mp4', 'video/avi', 'video/mov', 'video/mkv'];
  const AUDIO_FORMATS = ['audio/wav', 'audio/mp3', 'audio/mpeg', 'audio/ogg'];
  const MAX_FILE_SIZE = 500 * 1024 * 1024; // 500 MB

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
    // Valida tamanho
    if (file.size > MAX_FILE_SIZE) {
      toast.error('Arquivo muito grande! Máximo: 500 MB');
      return;
    }

    // Detecta tipo
    let type = null;
    if (VIDEO_FORMATS.includes(file.type)) {
      type = 'video';
    } else if (AUDIO_FORMATS.includes(file.type)) {
      type = 'audio';
    } else {
      toast.error('Formato não suportado! Use MP4, AVI, MOV, WAV ou MP3.');
      return;
    }

    setSelectedFile(file);
    setFileType(type);
    toast.success(`${type === 'video' ? 'Vídeo' : 'Áudio'} selecionado: ${file.name}`);
  };

  const handleUpload = async () => {
    if (!selectedFile || !fileType) {
      toast.error('Selecione um arquivo primeiro!');
      return;
    }

    try {
      let analysisId;

      if (fileType === 'video') {
        analysisId = await videoAnalysis.upload(selectedFile);
      } else {
        analysisId = await audioAnalysis.upload(selectedFile);
      }

      // Navega para página de análise
      navigate(`/analysis/${analysisId}?type=${fileType}`);
    } catch (error) {
      console.error('Erro no upload:', error);
    }
  };

  const isUploading = videoAnalysis.isUploading || audioAnalysis.isUploading;
  const uploadProgress = videoAnalysis.uploadProgress || audioAnalysis.uploadProgress;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-6">
      <div className="max-w-2xl w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Análise Multimodal Cirúrgica
          </h1>
          <p className="text-gray-400">
            Faça upload de vídeo ou áudio para análise com IA
          </p>
        </div>

        {/* Área de upload */}
        <div
          onDragEnter={handleDragEnter}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`
            border-2 border-dashed rounded-xl p-12 text-center
            transition-all duration-300
            ${isDragging 
              ? 'border-medvision-primary bg-medvision-primary bg-opacity-10 scale-105' 
              : 'border-gray-600 bg-gray-800 hover:border-medvision-accent'
            }
          `}
        >
          {!selectedFile ? (
            <>
              <Upload size={64} className="mx-auto text-gray-400 mb-4" />
              <h2 className="text-2xl font-semibold text-white mb-2">
                Arraste ou clique para selecionar
              </h2>
              <p className="text-gray-400 mb-6">
                Suportamos vídeos (MP4, AVI, MOV) e áudios (WAV, MP3)
              </p>
              <input
                type="file"
                id="file-upload"
                className="hidden"
                accept={[...VIDEO_FORMATS, ...AUDIO_FORMATS].join(',')}
                onChange={handleFileSelect}
              />
              <label
                htmlFor="file-upload"
                className="
                  inline-block px-6 py-3 bg-medvision-primary text-white 
                  rounded-lg font-semibold cursor-pointer
                  hover:bg-medvision-accent transition
                "
              >
                Selecionar Arquivo
              </label>
            </>
          ) : (
            <>
              {fileType === 'video' ? (
                <Video size={64} className="mx-auto text-medvision-primary mb-4" />
              ) : (
                <Music size={64} className="mx-auto text-medvision-accent mb-4" />
              )}
              <h2 className="text-xl font-semibold text-white mb-2">
                {selectedFile.name}
              </h2>
              <p className="text-gray-400 mb-2">
                Tamanho: {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
              </p>
              <p className="text-gray-500 text-sm mb-6">
                Tipo: {fileType === 'video' ? 'Vídeo Cirúrgico' : 'Áudio da Equipe'}
              </p>
              
              {!isUploading && (
                <div className="flex justify-center space-x-4">
                  <button
                    onClick={() => {
                      setSelectedFile(null);
                      setFileType(null);
                    }}
                    className="
                      px-6 py-3 bg-gray-700 text-white rounded-lg font-semibold
                      hover:bg-gray-600 transition
                    "
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={handleUpload}
                    className="
                      px-6 py-3 bg-medvision-primary text-white rounded-lg font-semibold
                      hover:bg-medvision-accent transition
                    "
                  >
                    Iniciar Análise
                  </button>
                </div>
              )}

              {isUploading && (
                <div className="mt-6">
                  <div className="flex items-center justify-center mb-2">
                    <Loader className="animate-spin text-medvision-primary mr-2" size={20} />
                    <span className="text-white font-semibold">
                      Enviando... {uploadProgress}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-medvision-primary to-medvision-accent h-full transition-all duration-300"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Informações */}
        <div className="mt-8 bg-gray-800 rounded-lg p-6">
          <div className="flex items-start text-yellow-400 mb-3">
            <FileWarning size={24} className="mr-2 flex-shrink-0" />
            <div>
              <h3 className="font-semibold mb-1">Importante</h3>
              <ul className="text-sm text-gray-300 space-y-1 list-disc list-inside">
                <li>Vídeos: Análise com YOLOv8 para detecção de anomalias</li>
                <li>Áudios: Análise de indicadores psicológicos com librosa</li>
                <li>Tamanho máximo: 500 MB</li>
                <li>Tempo de processamento: 1-5 minutos</li>
                <li>Relatório gerado com Google Gemini 2.5</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
