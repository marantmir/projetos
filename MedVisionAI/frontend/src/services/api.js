/**
 * Serviço de comunicação com a API backend.
 * 
 * Centraliza todas as chamadas HTTP para o backend usando axios.
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Cria instância configurada do axios
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 300000, // 5 minutos para uploads grandes
});

// === VIDEO ENDPOINTS ===

/**
 * Upload e análise de vídeo cirúrgico
 * @param {File} file - Arquivo de vídeo
 * @param {Function} onUploadProgress - Callback de progresso
 * @param {Object} patientData - Dados do paciente (opcional)
 * @returns {Promise<Object>} Resposta com analysis_id
 */
export const uploadVideo = async (file, onUploadProgress, patientData = null) => {
  const formData = new FormData();
  formData.append('file', file);
  
  // Adiciona dados do paciente se fornecidos
  if (patientData) {
    formData.append('patient_data', JSON.stringify(patientData));
  }

  const response = await api.post('/api/v1/video/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onUploadProgress && progressEvent.total) {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onUploadProgress(percentCompleted);
      }
    },
  });

  return response.data;
};

/**
 * Obtém status de análise de vídeo
 * @param {string} analysisId - ID da análise
 * @returns {Promise<Object>} Status da análise
 */
export const getVideoStatus = async (analysisId) => {
  const response = await api.get(`/api/v1/video/status/${analysisId}`);
  return response.data;
};

/**
 * Obtém resultado completo da análise de vídeo
 * @param {string} analysisId - ID da análise
 * @returns {Promise<Object>} Resultado completo
 */
export const getVideoResult = async (analysisId) => {
  const response = await api.get(`/api/v1/video/result/${analysisId}`);
  return response.data;
};

/**
 * Obtém frames anotados
 * @param {string} analysisId - ID da análise
 * @param {number} limit - Número máximo de frames
 * @returns {Promise<Object>} Frames anotados
 */
export const getVideoFrames = async (analysisId, limit = 10) => {
  const response = await api.get(`/api/v1/video/frames/${analysisId}`, {
    params: { limit },
  });
  return response.data;
};

// === AUDIO ENDPOINTS ===

/**
 * Upload e análise de áudio
 * @param {File} file - Arquivo de áudio
 * @param {Function} onUploadProgress - Callback de progresso
 * @param {string} consultationType - Tipo de consulta (gynecological, prenatal, postpartum, general)
 * @param {Object} patientData - Dados do paciente (opcional)
 * @returns {Promise<Object>} Resposta com analysis_id
 */
export const uploadAudio = async (file, onUploadProgress, consultationType = 'general', patientData = null) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('consultation_type', consultationType);
  
  // Adiciona dados do paciente se fornecidos
  if (patientData) {
    formData.append('patient_data', JSON.stringify(patientData));
  }

  const response = await api.post('/api/v1/audio/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onUploadProgress && progressEvent.total) {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onUploadProgress(percentCompleted);
      }
    },
  });

  return response.data;
};

/**
 * Obtém status de análise de áudio
 * @param {string} analysisId - ID da análise
 * @returns {Promise<Object>} Status da análise
 */
export const getAudioStatus = async (analysisId) => {
  const response = await api.get(`/api/v1/audio/status/${analysisId}`);
  return response.data;
};

/**
 * Obtém resultado completo da análise de áudio
 * @param {string} analysisId - ID da análise
 * @returns {Promise<Object>} Resultado completo
 */
export const getAudioResult = async (analysisId) => {
  const response = await api.get(`/api/v1/audio/result/${analysisId}`);
  return response.data;
};

// === REPORTS ENDPOINTS ===

/**
 * Lista todos os relatórios
 * @returns {Promise<Object>} Lista de relatórios
 */
export const listReports = async () => {
  const response = await api.get('/api/v1/reports/list');
  return response.data;
};

/**
 * Exporta relatório como Markdown
 * @param {string} analysisId - ID da análise
 * @param {string} reportType - Tipo do relatório ('video' ou 'audio')
 * @returns {Promise<Blob>} Arquivo Markdown
 */
export const exportReportMarkdown = async (analysisId, reportType = 'video') => {
  const response = await api.get(`/api/v1/reports/${analysisId}/markdown`, {
    params: { report_type: reportType },
    responseType: 'blob',
  });
  return response.data;
};

/**
 * Download de relatório Markdown
 * @param {string} analysisId - ID da análise
 * @param {string} reportType - Tipo do relatório
 */
export const downloadReportMarkdown = async (analysisId, reportType = 'video') => {
  const blob = await exportReportMarkdown(analysisId, reportType);
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${analysisId}_relatorio.md`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

// === HEALTH CHECK ===

/**
 * Verifica saúde da API
 * @returns {Promise<Object>} Status da saúde
 */
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
