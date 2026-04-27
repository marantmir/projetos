"""
WebSocket para streaming de alertas e progresso em tempo real.

Implementa conexões WebSocket para comunicação bidirecional com o frontend,
enviando updates de progresso e alertas críticos durante o processamento.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/ws", tags=["websocket"])


class ConnectionManager:
    """
    Gerenciador de conexões WebSocket.
    
    Mantém registro de todas as conexões ativas e permite broadcast
    de mensagens para clientes específicos ou todos.
    """
    
    def __init__(self):
        """Inicializa o gerenciador."""
        # Dicionário analysis_id -> lista de websockets
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, analysis_id: str):
        """
        Aceita e registra uma nova conexão WebSocket.
        
        Args:
            websocket: Conexão WebSocket.
            analysis_id: ID da análise a monitorar.
        """
        await websocket.accept()
        
        if analysis_id not in self.active_connections:
            self.active_connections[analysis_id] = []
        
        self.active_connections[analysis_id].append(websocket)
        logger.info(f"WebSocket conectado: {analysis_id} (total: {len(self.active_connections[analysis_id])})")
    
    def disconnect(self, websocket: WebSocket, analysis_id: str):
        """
        Remove uma conexão WebSocket.
        
        Args:
            websocket: Conexão a remover.
            analysis_id: ID da análise.
        """
        if analysis_id in self.active_connections:
            try:
                self.active_connections[analysis_id].remove(websocket)
                logger.info(f"WebSocket desconectado: {analysis_id}")
                
                # Remove lista vazia
                if not self.active_connections[analysis_id]:
                    del self.active_connections[analysis_id]
            except ValueError:
                pass
    
    async def send_message(self, analysis_id: str, message: dict):
        """
        Envia mensagem para todos os clientes de uma análise.
        
        Args:
            analysis_id: ID da análise.
            message: Dicionário a enviar (será convertido para JSON).
        """
        if analysis_id not in self.active_connections:
            return
        
        # Lista de conexões a remover (se falharem)
        dead_connections = []
        
        for connection in self.active_connections[analysis_id]:
            try:
                if connection.client_state == WebSocketState.CONNECTED:
                    await connection.send_json(message)
                else:
                    dead_connections.append(connection)
            except Exception as e:
                logger.warning(f"Erro ao enviar mensagem WebSocket: {e}")
                dead_connections.append(connection)
        
        # Remove conexões mortas
        for dead_conn in dead_connections:
            self.disconnect(dead_conn, analysis_id)
    
    async def broadcast_progress(
        self,
        analysis_id: str,
        percent: float,
        stage: str
    ):
        """
        Envia update de progresso.
        
        Args:
            analysis_id: ID da análise.
            percent: Progresso percentual (0-100).
            stage: Descrição da etapa atual.
        """
        message = {
            "type": "progress",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "percent": percent,
                "stage": stage
            }
        }
        await self.send_message(analysis_id, message)
    
    async def broadcast_alert(self, analysis_id: str, alert_data: dict):
        """
        Envia alerta de anomalia crítica.
        
        Args:
            analysis_id: ID da análise.
            alert_data: Dados do alerta (formato RealtimeAlert).
        """
        message = {
            "type": "alert",
            "timestamp": datetime.utcnow().isoformat(),
            "data": alert_data
        }
        await self.send_message(analysis_id, message)
    
    async def broadcast_completed(self, analysis_id: str, summary: dict):
        """
        Envia notificação de conclusão.
        
        Args:
            analysis_id: ID da análise.
            summary: Sumário dos resultados.
        """
        message = {
            "type": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "data": summary
        }
        await self.send_message(analysis_id, message)


# Singleton global
connection_manager = ConnectionManager()


@router.websocket("/analysis/{analysis_id}")
async def analysis_stream(websocket: WebSocket, analysis_id: str):
    """
    WebSocket endpoint para streaming de progresso e alertas.
    
    Protocolo de mensagens:
    - {"type": "ping"}: Heartbeat (a cada N segundos)
    - {"type": "progress", "data": {"percent": float, "stage": str}}
    - {"type": "alert", "data": {...}}
    - {"type": "completed", "data": {...}}
    
    Args:
        websocket: Conexão WebSocket.
        analysis_id: ID da análise a monitorar.
    """
    await connection_manager.connect(websocket, analysis_id)
    
    # Envia mensagem inicial de conexão
    await websocket.send_json({
        "type": "connected",
        "timestamp": datetime.utcnow().isoformat(),
        "message": f"Conectado ao stream da análise {analysis_id}"
    })
    
    try:
        # Loop de heartbeat e recepção de mensagens
        heartbeat_interval = settings.WEBSOCKET_HEARTBEAT_INTERVAL
        last_heartbeat = asyncio.get_event_loop().time()
        
        while True:
            try:
                # Aguarda mensagem do cliente com timeout
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=1.0
                )
                
                # Processa mensagem do cliente (se houver)
                try:
                    client_msg = json.loads(data)
                    
                    # Responde a pong do cliente
                    if client_msg.get("type") == "pong":
                        logger.debug(f"Pong recebido de {analysis_id}")
                
                except json.JSONDecodeError:
                    logger.warning(f"Mensagem WebSocket inválida: {data}")
            
            except asyncio.TimeoutError:
                # Timeout é normal, apenas continua
                pass
            
            # Envia heartbeat periodicamente
            current_time = asyncio.get_event_loop().time()
            if current_time - last_heartbeat >= heartbeat_interval:
                try:
                    await websocket.send_json({
                        "type": "ping",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    last_heartbeat = current_time
                except Exception as e:
                    logger.warning(f"Erro ao enviar heartbeat: {e}")
                    break
    
    except WebSocketDisconnect:
        logger.info(f"Cliente desconectou WebSocket: {analysis_id}")
    except Exception as e:
        logger.error(f"Erro no WebSocket {analysis_id}: {e}", exc_info=True)
    finally:
        connection_manager.disconnect(websocket, analysis_id)


def get_connection_manager() -> ConnectionManager:
    """
    Obtém o gerenciador de conexões singleton.
    
    Returns:
        Instância global do ConnectionManager.
    """
    return connection_manager
