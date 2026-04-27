/**
 * Componente BoundingBoxOverlay
 * 
 * Responsável por desenhar bounding boxes sobre frames de vídeo usando Canvas.
 * Mapeia coordenadas de detecção para coordenadas de display com escala automática.
 * 
 * IMPORTANTE: Este componente lida corretamente com object-fit: contain, 
 * calculando o letterbox/pillarbox para garantir alinhamento perfeito dos
 * bounding boxes sobre os objetos detectados no vídeo.
 */

import React, { useRef, useEffect } from 'react';

// Mapeamento de tipo de anomalia para cores
const ANOMALY_COLORS = {
  bleeding: '#EF4444',        // Vermelho
  instrument: '#06B6D4',      // Ciano (mais visível)
  anatomical: '#10B981',      // Verde
  procedural: '#F59E0B',      // Amarelo
  patient_safety: '#A855F7',  // Roxo mais vibrante
  other: '#06B6D4',           // Ciano (padrão para instrumentos)
};

// Mapeamento de severidade para espessura da linha
const SEVERITY_THICKNESS = {
  critical: 4,
  warning: 3,
  info: 2,
};

const BoundingBoxOverlay = ({ videoRef, frameAnalysis }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current || !videoRef?.current || !frameAnalysis || !frameAnalysis.bounding_boxes) {
      return;
    }

    const canvas = canvasRef.current;
    const video = videoRef.current;
    const ctx = canvas.getContext('2d');

    // Aguarda o vídeo estar carregado para ter dimensões corretas
    if (!video.videoWidth || !video.videoHeight) {
      console.log('[BoundingBox] Aguardando carregamento do vídeo...');
      return;
    }

    // Usa as MESMAS dimensões do elemento de vídeo renderizado
    const displayWidth = video.offsetWidth;
    const displayHeight = video.offsetHeight;
    
    // Define dimensões do canvas iguais ao vídeo renderizado
    canvas.width = displayWidth;
    canvas.height = displayHeight;

    // Limpa canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Dimensões originais do vídeo (do arquivo)
    const videoWidth = video.videoWidth;
    const videoHeight = video.videoHeight;
    
    // Calcula aspect ratios
    const videoAspect = videoWidth / videoHeight;
    const displayAspect = displayWidth / displayHeight;
    
    // Calcula dimensões reais do vídeo dentro do elemento (object-fit: contain)
    let renderWidth, renderHeight, offsetX, offsetY;
    
    if (displayAspect > videoAspect) {
      // Display mais largo: vídeo limitado pela altura (pillarbox)
      renderHeight = displayHeight;
      renderWidth = displayHeight * videoAspect;
      offsetX = (displayWidth - renderWidth) / 2;
      offsetY = 0;
    } else {
      // Display mais alto: vídeo limitado pela largura (letterbox)
      renderWidth = displayWidth;
      renderHeight = displayWidth / videoAspect;
      offsetX = 0;
      offsetY = (displayHeight - renderHeight) / 2;
    }

    // Fatores de escala
    const scaleX = renderWidth / videoWidth;
    const scaleY = renderHeight / videoHeight;

    console.log('[BoundingBox] Config:', {
      videoOriginal: { width: videoWidth, height: videoHeight, aspect: videoAspect },
      display: { width: displayWidth, height: displayHeight, aspect: displayAspect },
      render: { width: renderWidth, height: renderHeight },
      offset: { x: offsetX, y: offsetY },
      scale: { x: scaleX, y: scaleY }
    });

    // Desenha cada bounding box
    frameAnalysis.bounding_boxes.forEach((box, index) => {
      const { x_min, y_min, x_max, y_max, class_name, confidence, anomaly_type, severity } = box;

      if (index === 0) {
        console.log('[BoundingBox] Box #1 original:', { x_min, y_min, x_max, y_max });
      }

      // Transforma coordenadas
      const x = (x_min * scaleX) + offsetX;
      const y = (y_min * scaleY) + offsetY;
      const width = (x_max - x_min) * scaleX;
      const height = (y_max - y_min) * scaleY;

      if (index === 0) {
        console.log('[BoundingBox] Box #1 transformed:', { x, y, width, height });
      }

      // Define cor baseada no tipo de anomalia
      const color = ANOMALY_COLORS[anomaly_type] || ANOMALY_COLORS.other;
      
      // Define espessura baseada na severidade
      const lineWidth = SEVERITY_THICKNESS[severity] || 2;

      // Desenha retângulo
      ctx.strokeStyle = color;
      ctx.lineWidth = lineWidth;
      ctx.strokeRect(x, y, width, height);

      // Desenha label com classe e confiança
      ctx.font = 'bold 14px Inter, sans-serif';
      const label = `${class_name} ${(confidence * 100).toFixed(0)}%`;
      const textMetrics = ctx.measureText(label);
      const labelHeight = 24;
      const labelWidth = textMetrics.width + 12;
      
      // Desenha fundo semi-transparente para label
      ctx.fillStyle = color + 'DD';
      ctx.fillRect(x, y - labelHeight, labelWidth, labelHeight);

      // Desenha texto da label
      ctx.fillStyle = '#FFFFFF';
      ctx.fillText(label, x + 6, y - 7);

      // Desenha badge de severidade
      if (severity === 'critical') {
        ctx.fillStyle = '#DC2626';
        ctx.fillRect(x + width - 50, y + 4, 46, 16);
        ctx.fillStyle = '#FFFFFF';
        ctx.font = 'bold 10px Inter, sans-serif';
        ctx.fillText('CRÍTICO', x + width - 46, y + 15);
      }
    });
  }, [frameAnalysis, videoRef]);

  // Força atualização quando janela redimensionar
  useEffect(() => {
    const handleResize = () => {
      // Force re-render ao mudar tamanho da janela
      // O useEffect principal será retriggered pois videoRef muda
      if (canvasRef.current && videoRef?.current) {
        const canvas = canvasRef.current;
        const video = videoRef.current;
        
        // Força atualização do canvas dimensions
        requestAnimationFrame(() => {
          canvas.width = video.offsetWidth;
          canvas.height = video.offsetHeight;
        });
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [videoRef]);

  return (
    <canvas
      ref={canvasRef}
      className="absolute top-0 left-0 w-full h-full pointer-events-none"
      style={{ zIndex: 10 }}
    />
  );
};

export default BoundingBoxOverlay;
