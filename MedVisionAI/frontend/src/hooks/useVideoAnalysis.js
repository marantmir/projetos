/**
 * Hook customizado para gerenciar análise de vídeo.
 * 
 * Encapsula lógica de upload, polling de status e obtenção de resultado.
 */

import { useState } from 'react';
import { uploadVideo, getVideoStatus, getVideoResult, getVideoFrames } from '../services/api';
import toast from 'react-hot-toast';

export default function useVideoAnalysis() {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [analysisId, setAnalysisId] = useState(null);
  const [status, setStatus] = useState(null);
  const [result, setResult] = useState(null);
  const [frames, setFrames] = useState([]);
  const [error, setError] = useState(null);

  /**
   * Upload de vídeo
   * @param {File} file - Arquivo de vídeo
   * @param {object} patientData - Dados do paciente (opcional)
   */
  const upload = async (file, patientData = null) => {
    try {
      setIsUploading(true);
      setUploadProgress(0);
      setError(null);

      const data = await uploadVideo(file, (progress) => {
        setUploadProgress(progress);
      }, patientData);

      setAnalysisId(data.analysis_id);
      toast.success('Vídeo enviado! Análise iniciada.');
      return data.analysis_id;
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Erro ao enviar vídeo';
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
      const data = await getVideoStatus(id || analysisId);
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
      const data = await getVideoResult(id || analysisId);
      setResult(data.result);
      return data;
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Erro ao obter resultado';
      setError(errorMsg);
      throw err;
    }
  };

  /**
   * Obter frames anotados
   */
  const fetchFrames = async (id, limit = 10) => {
    try {
      const data = await getVideoFrames(id || analysisId, limit);
      setFrames(data.frames);
      return data;
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Erro ao obter frames';
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
    setFrames([]);
    setError(null);
  };

  return {
    upload,
    fetchStatus,
    fetchResult,
    fetchFrames,
    reset,
    isUploading,
    uploadProgress,
    analysisId,
    status,
    result,
    frames,
    error,
  };
}
