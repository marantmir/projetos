/**
 * Hook customizado para gerenciar conexão WebSocket.
 * 
 * Conecta automaticamente ao WebSocket quando analysisId é fornecido,
 * e desconecta na desmontagem do componente.
 */

import { useEffect, useState } from 'react';
import websocketService from '../services/websocketService';

export default function useWebSocket(analysisId) {
  const [isConnected, setIsConnected] = useState(false);
  const [progress, setProgress] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [isCompleted, setIsCompleted] = useState(false);

  useEffect(() => {
    if (!analysisId) return;

    // Callbacks para eventos do WebSocket
    const handleConnected = () => {
      setIsConnected(true);
    };

    const handleProgress = (data) => {
      setProgress(data);
    };

    const handleAlert = (data) => {
      setAlerts((prev) => [...prev, data]);
    };

    const handleCompleted = (data) => {
      setIsCompleted(true);
      setProgress(data);
    };

    const handleError = (error) => {
      console.error('Erro no WebSocket:', error);
      setIsConnected(false);
    };

    // Registra listeners
    websocketService.on('connected', handleConnected);
    websocketService.on('progress', handleProgress);
    websocketService.on('alert', handleAlert);
    websocketService.on('completed', handleCompleted);
    websocketService.on('error', handleError);

    // Conecta
    websocketService.connect(analysisId);

    // Cleanup na desmontagem
    return () => {
      websocketService.off('connected', handleConnected);
      websocketService.off('progress', handleProgress);
      websocketService.off('alert', handleAlert);
      websocketService.off('completed', handleCompleted);
      websocketService.off('error', handleError);
      websocketService.disconnect();
    };
  }, [analysisId]);

  return {
    isConnected,
    progress,
    alerts,
    isCompleted,
  };
}
