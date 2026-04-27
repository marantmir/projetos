/**
 * Hook customizado para gerenciar análise de áudio.
 * 
 * Encapsula lógica de upload, polling de status e obtenção de resultado.
 */

import { useState } from 'react';
import { uploadAudio, getAudioStatus, getAudioResult } from '../services/api';
import toast from 'react-hot-toast';

export default function useAudioAnalysis() {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [analysisId, setAnalysisId] = useState(null);
  const [status, setStatus] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  /**
   * Upload de áudio
   * @param {File} file - Arquivo de áudio
   * @param {string} consultationType - Tipo de consulta (gynecological, prenatal, postpartum, general)
   * @param {object} patientData - Dados do paciente (opcional)
   */
  const upload = async (file, consultationType = 'general', patientData = null) => {
    try {
      setIsUploading(true);
      setUploadProgress(0);
      setError(null);

      const data = await uploadAudio(file, (progress) => {
        setUploadProgress(progress);
      }, consultationType, patientData);

      setAnalysisId(data.analysis_id);
      toast.success('Áudio enviado! Análise iniciada.');
      return data.analysis_id;
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Erro ao enviar áudio';
      setError(errorMsg);
      toast.error(errorMsg);
      throw err;
    } finally {
      setIsUploading(false);
    }
  };

  /**
   * Obter status da análise
   */
  const fetchStatus = async (id) => {
    try {
      const data = await getAudioStatus(id || analysisId);
      setStatus(data.status);
      return data;
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Erro ao obter status';
      setError(errorMsg);
      throw err;
    }
  };

  /**
   * Obter resultado completo
   */
  const fetchResult = async (id) => {
    try {
      const data = await getAudioResult(id || analysisId);
      setResult(data.result);
      return data;
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Erro ao obter resultado';
      setError(errorMsg);
      throw err;
    }
  };

  /**
   * Resetar estado
   */
  const reset = () => {
    setIsUploading(false);
    setUploadProgress(0);
    setAnalysisId(null);
    setStatus(null);
    setResult(null);
    setError(null);
  };

  return {
    upload,
    fetchStatus,
    fetchResult,
    reset,
    isUploading,
    uploadProgress,
    analysisId,
    status,
    result,
    error,
  };
}
