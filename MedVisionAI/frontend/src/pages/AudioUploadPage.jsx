/**
 * AudioUploadPage
 * 
 * Página específica para upload e análise de consultas de áudio.
 * Detecta indicadores psicológicos e gera relatórios especializados.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, Music, Loader, Mic, Heart, Baby, Stethoscope, Edit } from 'lucide-react';
import useAudioAnalysis from '../hooks/useAudioAnalysis';
import AudioRecorder from '../components/AudioRecorder';
import PatientForm from '../components/PatientForm';
import toast from 'react-hot-toast';

const AudioUploadPage = () => {
  const navigate = useNavigate();
  const audioAnalysis = useAudioAnalysis();

  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [consultationType, setConsultationType] = useState('general');
  const [patientData, setPatientData] = useState(null);
  const [showPatientForm, setShowPatientForm] = useState(true);

  const AUDIO_FORMATS = ['audio/wav', 'audio/mp3', 'audio/mpeg', 'audio/ogg', 'audio/m4a', 'audio/webm'];
  const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100 MB

  const CONSULTATION_TYPES = [
    {
      value: 'gynecological',
      label: 'Consulta Ginecológica',
      icon: Heart,
      color: 'pink',
      description: 'Análise de consultas ginecológicas gerais',
      indicators: ['Ansiedade', 'Aflição vocal', 'Sinais de trauma']
    },
    {
      value: 'prenatal',
      label: 'Acompanhamento Pré-natal',
      icon: Baby,
      color: 'blue',
      description: 'Análise de consultas de gestantes',
      indicators: ['Ansiedade gestacional', 'Preocupações', 'Estresse']
    },
    {
      value: 'postpartum',
      label: 'Consulta Pós-parto',
      icon: Heart,
      color: 'purple',
      description: 'Análise de consultas após o parto',
      indicators: ['Depressão pós-parto', 'Ansiedade', 'Fadiga', 'Distress']
    },
    {
      value: 'general',
      label: 'Consulta Geral',
      icon: Stethoscope,
      color: 'gray',
      description: 'Análise de consultas médicas gerais',
      indicators: ['Aflição', 'Ansiedade', 'Depressão']
    }
  ];

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
      toast.error('Arquivo muito grande! Máximo: 100 MB');
      return;
    }

    // Valida formato
    if (!AUDIO_FORMATS.includes(file.type) && !file.name.endsWith('.webm')) {
      toast.error('Formato não suportado! Use WAV, MP3, OGG, M4A ou WebM.');
      return;
    }

    setSelectedFile(file);
    toast.success(`Áudio selecionado: ${file.name}`);
  };

  const handlePatientFormSubmit = (data) => {
    setPatientData(data);
    setShowPatientForm(false);
    toast.success(`Dados de ${data.nome} salvos com sucesso!`);
  };

  const handleEditPatientData = () => {
    setShowPatientForm(true);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error('Selecione um áudio primeiro!');
      return;
    }

    try {
      console.log('[AudioUpload] Starting upload for file:', selectedFile.name);
      const analysisId = await audioAnalysis.upload(selectedFile, consultationType, patientData);
      console.log('[AudioUpload] Upload returned analysisId:', analysisId);
      
      if (!analysisId) {
        console.error('[AudioUpload] No analysisId returned from upload!');
        toast.error('Erro: Upload não retornou ID de análise');
        return;
      }
      
      console.log('[AudioUpload] Navigating to:', `/analysis/${analysisId}?type=audio&consultation=${consultationType}`);
      navigate(`/analysis/${analysisId}?type=audio&consultation=${consultationType}`);
    } catch (error) {
      console.error('[AudioUpload] Upload error:', error);
      toast.error(error.message || 'Erro ao fazer upload do áudio');
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
  };

  const handleRecordingComplete = (audioFile) => {
    validateAndSetFile(audioFile);
  };

  const selectedConsultation = CONSULTATION_TYPES.find(c => c.value === consultationType);
  const SelectedIcon = selectedConsultation?.icon || Stethoscope;

  // Se formulário de paciente não foi preenchido, mostrar apenas o formulário
  if (showPatientForm) {
    return (
      <div className="max-w-4xl mx-auto px-8 py-10">
        <div className="mb-8">
          <div className="flex items-center space-x-4 mb-6">
            <div className="p-5 bg-gradient-to-br from-sky-500 to-cyan-500 rounded-2xl shadow-md">
              <Music size={48} className="text-white" />
            </div>
            <div>
              <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-sky-600 bg-clip-text text-transparent dark:text-white mb-2">
                Análise de Consultas de Áudio
              </h1>
              <p className="text-xl text-gray-600 dark:text-gray-300">
                Primeiro, preencha os dados do paciente
              </p>
            </div>
          </div>
        </div>
        <PatientForm 
          onSubmit={handlePatientFormSubmit}
          initialData={patientData}
        />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-8">
      {/* Header */}
      <div className="mb-12 py-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <div className="p-5 bg-gradient-to-br from-sky-500 to-cyan-500 rounded-2xl shadow-md">
              <Music size={48} className="text-white" />
            </div>
            <div>
              <h1 className="text-6xl md:text-7xl font-bold bg-gradient-to-r from-blue-600 to-sky-600 bg-clip-text text-transparent dark:text-white mb-3 tracking-tight">
                Análise de Consultas de Áudio
              </h1>
              <p className="text-2xl text-gray-600 dark:text-gray-300">
                Detecção de indicadores psicológicos com IA especializada
              </p>
            </div>
          </div>
        </div>

        {/* Card com dados do paciente */}
        {patientData && (
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900 dark:to-emerald-900 dark:bg-opacity-20 border-2 border-green-300 dark:border-green-700 rounded-2xl p-6 shadow-lg mb-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="font-bold text-xl text-green-900 dark:text-green-100 mb-3 flex items-center">
                  <span className="mr-2">✅</span>
                  Dados do Paciente Registrados
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-green-800 dark:text-green-200">
                  <div>
                    <p className="text-sm font-semibold opacity-75">Nome:</p>
                    <p className="text-base font-bold">{patientData.nome}</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold opacity-75">Idade:</p>
                    <p className="text-base font-bold">{patientData.idade} anos</p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold opacity-75">Gestação:</p>
                    <p className="text-base font-bold">
                      {patientData.ja_foi_mae ? `${patientData.numero_gestacoes}ª gestação` : 'Primeira gestação'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-semibold opacity-75">Telefone:</p>
                    <p className="text-base font-bold">{patientData.telefone}</p>
                  </div>
                  {patientData.endereco && (
                    <div className="col-span-2">
                      <p className="text-sm font-semibold opacity-75">Endereço:</p>
                      <p className="text-base font-bold">{patientData.endereco}</p>
                    </div>
                  )}
                </div>
              </div>
              <button
                onClick={handleEditPatientData}
                className="ml-4 px-4 py-2 bg-white dark:bg-gray-800 text-green-700 dark:text-green-300 rounded-xl font-semibold hover:bg-green-100 dark:hover:bg-gray-700 transition flex items-center shadow-md"
              >
                <Edit size={18} className="mr-2" />
                Editar
              </button>
            </div>
          </div>
        )}

        {/* Informações */}
        <div className="bg-purple-50 dark:bg-purple-900 dark:bg-opacity-20 border-2 border-purple-300 dark:border-purple-700 rounded-2xl p-8 shadow-lg">
          <div className="flex items-start space-x-4">
            <div className="p-3 bg-purple-600 rounded-xl">
              <Mic size={28} className="text-white" />
            </div>
            <div className="flex-1">
              <h3 className="font-bold text-2xl text-purple-900 dark:text-purple-100 mb-4">O que será analisado:</h3>
              <ul className="text-lg text-purple-800 dark:text-purple-200 space-y-3">
                <li className="flex items-start"><span className="mr-3 text-2xl">🧠</span><span>Indicadores psicológicos (ansiedade, depressão, trauma, distress)</span></li>
                <li className="flex items-start"><span className="mr-3 text-2xl">🎤</span><span>Análise acústica avançada (MFCC, pitch, energia, ZCR)</span></li>
                <li className="flex items-start"><span className="mr-3 text-2xl">😔</span><span>Detecção de padrões emocionais na fala</span></li>
                <li className="flex items-start"><span className="mr-3 text-2xl">📋</span><span>Relatório clínico especializado com <strong>Gemini 2.5 Flash</strong></span></li>
                <li className="flex items-start"><span className="mr-3 text-2xl">⚠️</span><span>Classificação de nível de risco e recomendações</span></li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Gravador de Áudio */}
      <div className="mb-8">
        <AudioRecorder onRecordingComplete={handleRecordingComplete} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Seletor de tipo de consulta */}
        <div className="lg:col-span-1">
          <h2 className="font-bold text-2xl text-gray-900 dark:text-white mb-6 flex items-center">
            <Stethoscope size={28} className="mr-3" />
            Tipo de Consulta
          </h2>
          <div className="space-y-4">
            {CONSULTATION_TYPES.map((type) => {
              const Icon = type.icon;
              const isSelected = consultationType === type.value;
              
              // Definir cores específicas para cada tipo
              const colors = {
                pink: { border: 'border-pink-500', bg: 'bg-pink-50 dark:bg-pink-900 dark:bg-opacity-20', text: 'text-pink-700 dark:text-pink-300', icon: 'text-pink-600 dark:text-pink-400', badge: 'bg-pink-100 dark:bg-pink-800 text-pink-700 dark:text-pink-200' },
                blue: { border: 'border-blue-500', bg: 'bg-blue-50 dark:bg-blue-900 dark:bg-opacity-20', text: 'text-blue-700 dark:text-blue-300', icon: 'text-blue-600 dark:text-blue-400', badge: 'bg-blue-100 dark:bg-blue-800 text-blue-700 dark:text-blue-200' },
                purple: { border: 'border-purple-500', bg: 'bg-purple-50 dark:bg-purple-900 dark:bg-opacity-20', text: 'text-purple-700 dark:text-purple-300', icon: 'text-purple-600 dark:text-purple-400', badge: 'bg-purple-100 dark:bg-purple-800 text-purple-700 dark:text-purple-200' },
                gray: { border: 'border-gray-500', bg: 'bg-gray-50 dark:bg-gray-700', text: 'text-gray-700 dark:text-gray-300', icon: 'text-gray-600 dark:text-gray-400', badge: 'bg-gray-100 dark:bg-gray-600 text-gray-700 dark:text-gray-200' }
              };
              
              const colorScheme = colors[type.color];

              return (
                <button
                  key={type.value}
                  onClick={() => setConsultationType(type.value)}
                  className={`
                    w-full text-left p-5 rounded-xl border-2 transition-all duration-200
                    ${isSelected 
                      ? `${colorScheme.border} ${colorScheme.bg} shadow-xl scale-105` 
                      : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500 bg-white dark:bg-gray-800 hover:shadow-lg'
                    }
                  `}
                >
                  <div className="flex items-start space-x-4">
                    <Icon 
                      size={32} 
                      className={isSelected ? colorScheme.icon : 'text-gray-400 dark:text-gray-500'}
                    />
                    <div className="flex-1">
                      <h3 className={`font-bold text-lg ${isSelected ? colorScheme.text : 'text-gray-700 dark:text-gray-300'}`}>
                        {type.label}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                        {type.description}
                      </p>
                      {isSelected && (
                        <div className="mt-3 pt-3 border-t border-gray-300 dark:border-gray-600">
                          <p className="text-sm text-gray-600 dark:text-gray-400 font-semibold mb-2">Indicadores:</p>
                          <div className="flex flex-wrap gap-2">
                            {type.indicators.map((indicator, idx) => (
                              <span
                                key={idx}
                                className={`text-sm px-3 py-1 rounded-full ${colorScheme.badge} font-medium`}
                              >
                                {indicator}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                    {isSelected && (
                      <div className="w-7 h-7 rounded-full bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center shadow-lg">
                        <svg className="w-4 h-4 text-white font-bold" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Área de upload */}
        <div className="lg:col-span-2">
          <h2 className="font-bold text-2xl text-gray-900 dark:text-white mb-6 flex items-center">
            <Upload size={28} className="mr-3" />
            Arquivo de Áudio
          </h2>
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
                    ? 'border-medvision-accent bg-medvision-accent bg-opacity-10 scale-[1.02] shadow-xl' 
                    : 'border-gray-400 dark:border-gray-600 hover:border-medvision-accent dark:hover:border-medvision-accent hover:bg-gray-50 dark:hover:bg-gray-700'
                  }
                `}
              >
                <Music size={80} className="mx-auto text-gray-400 dark:text-gray-500 mb-6" />
                <h2 className="text-3xl font-bold text-gray-800 dark:text-white mb-4">
                  Arraste o áudio ou clique para selecionar
                </h2>
                <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">
                  Formatos: WAV, MP3, OGG, M4A (máx. 100 MB)
                </p>
                <input
                  type="file"
                  id="audio-upload"
                  accept="audio/*"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                <label
                  htmlFor="audio-upload"
                  className="inline-block px-12 py-5 bg-gradient-to-r from-sky-500 to-cyan-500 text-white text-xl font-bold rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 cursor-pointer"
                >
                  📁 Selecionar Áudio
                </label>
              </div>
            ) : (
              <div>
                {/* Preview do áudio */}
                <div className="mb-6">
                  <audio
                    src={URL.createObjectURL(selectedFile)}
                    controls
                    className="w-full"
                  />
                </div>

                {/* Informações do arquivo */}
                <div className="bg-gray-100 dark:bg-gray-700 rounded-xl p-6 mb-6 shadow-md">
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

                {/* Tipo de consulta selecionado */}
                <div className="bg-purple-50 dark:bg-purple-900 dark:bg-opacity-20 border-2 border-purple-300 dark:border-purple-700 rounded-xl p-6 mb-8 shadow-md">
                  <div className="flex items-center space-x-4">
                    <div className="p-3 bg-purple-600 rounded-xl">
                      <SelectedIcon size={32} className="text-white" />
                    </div>
                    <div>
                      <p className="font-bold text-xl text-purple-900 dark:text-purple-100">{selectedConsultation?.label}</p>
                      <p className="text-base text-purple-700 dark:text-purple-300 mt-1">{selectedConsultation?.description}</p>
                    </div>
                  </div>
                </div>

                {/* Botão de upload */}
                {audioAnalysis.isUploading ? (
                  <div className="text-center">
                    <Loader size={48} className="mx-auto text-medvision-accent animate-spin mb-4" />
                    <p className="text-gray-600 mb-2">Enviando áudio...</p>
                    <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                      <div
                        className="bg-medvision-accent h-full transition-all duration-300"
                        style={{ width: `${audioAnalysis.uploadProgress}%` }}
                      />
                    </div>
                    <p className="text-sm text-gray-500 mt-2">
                      {audioAnalysis.uploadProgress}%
                    </p>
                  </div>
                ) : (
                  <button
                    onClick={handleUpload}
                    className="w-full py-6 bg-gradient-to-r from-sky-500 to-cyan-500 text-white rounded-2xl font-bold text-2xl shadow-md hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-1"
                  >
                    🧠 Iniciar Análise Psicológica
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Disclaimer + Especificações técnicas */}
      <div className="mt-10">
        <div className="bg-yellow-50 dark:bg-yellow-900 dark:bg-opacity-20 border-2 border-yellow-300 dark:border-yellow-700 rounded-xl p-6 mb-6 shadow-lg">
          <p className="text-lg text-yellow-900 dark:text-yellow-100 leading-relaxed">
            <strong className="text-xl">⚠️ Importante:</strong> Esta análise é uma ferramenta de apoio e <strong>NÃO substitui avaliação clínica profissional</strong>. 
            Os indicadores detectados devem ser interpretados por profissional de saúde mental qualificado.
          </p>
        </div>

        <div className="text-center text-lg text-gray-600 dark:text-gray-400 py-4">
          <p>
            🎤 Análise acústica: <strong>Librosa + MFCC</strong> | 
            🧠 IA generativa: <strong>Gemini 2.5 Flash</strong>
          </p>
        </div>
      </div>
    </div>
  );
};

export default AudioUploadPage;
