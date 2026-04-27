/**
 * Serviço de comunicação WebSocket para streaming em tempo real.
 * 
 * Gerencia conexão, reconexão automática e parsing de mensagens.
 */

const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

class WebSocketService {
  constructor() {
    this.ws = null;
    this.analysisId = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000; // ms
    this.listeners = {
      progress: [],
      alert: [],
      completed: [],
      connected: [],
      error: [],
    };
  }

  /**
   * Conecta ao WebSocket do backend
   * @param {string} analysisId - ID da análise a monitorar
   */
  connect(analysisId) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.warn('WebSocket já conectado');
      return;
    }

    this.analysisId = analysisId;
    const wsUrl = `${WS_BASE_URL}/ws/analysis/${analysisId}`;

    console.log(`Conectando WebSocket: ${wsUrl}`);

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket conectado');
      this.reconnectAttempts = 0;
      this._notifyListeners('connected', { analysisId });
    };

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        this._handleMessage(message);
      } catch (error) {
        console.error('Erro ao parsear mensagem WebSocket:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('Erro WebSocket:', error);
      this._notifyListeners('error', error);
    };

    this.ws.onclose = (event) => {
      console.log('WebSocket desconectado:', event.code, event.reason);
      
      // Tenta reconectar se não foi fechamento intencional
      if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
        this._reconnect();
      }
    };
  }

  /**
   * Desconecta WebSocket
   */
  disconnect() {
    if (this.ws) {
      this.ws.close(1000, 'Desconexão intencional');
      this.ws = null;
    }
  }

  /**
   * Adiciona listener para tipo de mensagem
   * @param {string} type - Tipo de mensagem ('progress', 'alert', etc.)
   * @param {Function} callback - Função a chamar quando mensagem chegar
   */
  on(type, callback) {
    if (this.listeners[type]) {
      this.listeners[type].push(callback);
    }
  }

  /**
   * Remove listener
   * @param {string} type - Tipo de mensagem
   * @param {Function} callback - Função a remover
   */
  off(type, callback) {
    if (this.listeners[type]) {
      this.listeners[type] = this.listeners[type].filter((cb) => cb !== callback);
    }
  }

  /**
   * Limpa todos os listeners
   */
  removeAllListeners() {
    Object.keys(this.listeners).forEach((type) => {
      this.listeners[type] = [];
    });
  }

  /**
   * Processa mensagem recebida
   * @private
   */
  _handleMessage(message) {
    const { type, data, timestamp } = message;

    switch (type) {
      case 'ping':
        // Responde com pong
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
          this.ws.send(JSON.stringify({ type: 'pong' }));
        }
        break;

      case 'progress':
        this._notifyListeners('progress', data);
        break;

      case 'alert':
        this._notifyListeners('alert', data);
        break;

      case 'completed':
        this._notifyListeners('completed', data);
        break;

      case 'connected':
        console.log('Mensagem de conexão recebida:', message.message);
        break;

      default:
        console.warn('Tipo de mensagem desconhecido:', type);
    }
  }

  /**
   * Notifica listeners registrados
   * @private
   */
  _notifyListeners(type, data) {
    if (this.listeners[type]) {
      this.listeners[type].forEach((callback) => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Erro ao executar listener ${type}:`, error);
        }
      });
    }
  }

  /**
   * Tenta reconectar com backoff exponencial
   * @private
   */
  _reconnect() {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(
      `Tentando reconectar (${this.reconnectAttempts}/${this.maxReconnectAttempts}) em ${delay}ms...`
    );

    setTimeout(() => {
      if (this.analysisId) {
        this.connect(this.analysisId);
      }
    }, Math.min(delay, 30000)); // Max 30s
  }
}

// Exporta instância singleton
export default new WebSocketService();
