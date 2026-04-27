/**
 * Componente AlertPanel
 * 
 * Painel lateral com alertas em tempo real via WebSocket.
 * Exibe alertas críticos, warnings e informativos com destaque visual.
 */

import React, { useEffect, useRef } from 'react';
import { AlertTriangle, Info, AlertCircle, Clock } from 'lucide-react';

// Mapeamento de severidade para ícone e cor
const SEVERITY_CONFIG = {
  critical: {
    icon: AlertTriangle,
    bgColor: 'bg-alert-critical',
    textColor: 'text-red-50',
    borderColor: 'border-red-600',
  },
  warning: {
    icon: AlertCircle,
    bgColor: 'bg-alert-warning',
    textColor: 'text-yellow-50',
    borderColor: 'border-yellow-600',
  },
  info: {
    icon: Info,
    bgColor: 'bg-alert-info',
    textColor: 'text-blue-50',
    borderColor: 'border-blue-600',
  },
};

const AlertPanel = ({ alerts }) => {
  const panelRef = useRef(null);
  const lastAlertCountRef = useRef(0);

  // Auto-scroll para novo alerta
  useEffect(() => {
    if (alerts.length > lastAlertCountRef.current && panelRef.current) {
      panelRef.current.scrollTop = panelRef.current.scrollHeight;
    }
    lastAlertCountRef.current = alerts.length;
  }, [alerts]);

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-md hover:shadow-lg transition-shadow h-full flex flex-col border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-sky-500 p-6">
        <h2 className="text-2xl font-bold text-white flex items-center">
          <AlertTriangle className="mr-3" size={28} />
          Alertas em Tempo Real
        </h2>
        <p className="text-base text-gray-100 mt-2">
          {alerts.length} {alerts.length === 1 ? 'alerta recebido' : 'alertas recebidos'}
        </p>
      </div>

      {/* Lista de alertas */}
      <div
        ref={panelRef}
        className="flex-1 overflow-y-auto p-6 space-y-4"
        style={{ maxHeight: 'calc(100vh - 200px)' }}
      >
        {alerts.length === 0 ? (
          <div className="text-center text-gray-600 dark:text-gray-400 py-16">
            <Info size={64} className="mx-auto mb-6 opacity-50" />
            <p className="text-lg font-semibold">Nenhum alerta crítico</p>
            <p className="text-base mt-2">
              Sistema monitorando em tempo real
            </p>
            <p className="text-sm mt-4 text-gray-500 dark:text-gray-500">
              Alertas aparecem para vídeos cirúrgicos.<br/>
              Análises de áudio não geram alertas visuais.
            </p>
          </div>
        ) : (
          alerts.map((alert, index) => {
            const config = SEVERITY_CONFIG[alert.severity] || SEVERITY_CONFIG.info;
            const Icon = config.icon;

            return (
              <div
                key={index}
                className={`
                  ${config.bgColor} ${config.textColor} ${config.borderColor}
                  border-l-4 rounded-lg p-4 shadow-md
                  transition-all duration-300 hover:shadow-xl
                  animate-fadeIn
                `}
              >
                {/* Header do alerta */}
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center">
                    <Icon size={20} className="mr-2 flex-shrink-0" />
                    <span className="font-bold text-sm uppercase tracking-wide">
                      {alert.severity === 'critical' ? 'CRÍTICO' : 
                       alert.severity === 'warning' ? 'ATENÇÃO' : 'INFO'}
                    </span>
                  </div>
                  <div className="flex items-center text-xs opacity-75">
                    <Clock size={12} className="mr-1" />
                    {formatTimestamp(alert.timestamp)}
                  </div>
                </div>

                {/* Mensagem */}
                <p className="text-sm font-medium mb-2">{alert.message}</p>

                {/* Detalhes */}
                <div className="text-xs opacity-90 space-y-1">
                  <p>
                    <strong>Tipo:</strong> {alert.anomaly_type}
                  </p>
                  <p>
                    <strong>Frame:</strong> {alert.frame_number} | 
                    <strong> Timestamp:</strong> {alert.frame_timestamp.toFixed(2)}s
                  </p>
                  {alert.confidence && (
                    <p>
                      <strong>Confiança:</strong> {(alert.confidence * 100).toFixed(1)}%
                    </p>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Footer com resumo */}
      {alerts.length > 0 && (
        <div className="bg-gray-100 dark:bg-gray-900 p-5 border-t-2 border-gray-200 dark:border-gray-700">
          <div className="flex justify-around text-base">
            <div className="text-center">
              <div className="text-red-500 dark:text-red-400 font-bold text-2xl">
                {alerts.filter(a => a.severity === 'critical').length}
              </div>
              <div className="text-gray-600 dark:text-gray-400 font-medium">Críticos</div>
            </div>
            <div className="text-center">
              <div className="text-yellow-600 dark:text-yellow-400 font-bold text-2xl">
                {alerts.filter(a => a.severity === 'warning').length}
              </div>
              <div className="text-gray-600 dark:text-gray-400 font-medium">Avisos</div>
            </div>
            <div className="text-center">
              <div className="text-blue-600 dark:text-blue-400 font-bold text-2xl">
                {alerts.filter(a => a.severity === 'info').length}
              </div>
              <div className="text-gray-600 dark:text-gray-400 font-medium">Informativos</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AlertPanel;
