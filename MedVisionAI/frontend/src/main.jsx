import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import App from './App.jsx'
import { ThemeProvider } from './contexts/ThemeContext.jsx'
import './index.css'
import './styles/custom.css'

try {
  const root = document.getElementById('root');
  if (!root) {
    throw new Error('Elemento #root não encontrado no DOM!');
  }

  ReactDOM.createRoot(root).render(
    <React.StrictMode>
      <BrowserRouter
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true
        }}
      >
        <ThemeProvider>
          <App />
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#1a3a5c',
                color: '#fff',
              },
              success: {
                iconTheme: {
                  primary: '#0d9488',
                  secondary: '#fff',
                },
              },
              error: {
                iconTheme: {
                  primary: '#dc2626',
                  secondary: '#fff',
                },
              },
            }}
          />
        </ThemeProvider>
      </BrowserRouter>
    </React.StrictMode>,
  );
} catch (error) {
  console.error('[MedVision] ERRO ao renderizar aplicação:', error);
  document.body.innerHTML = 
    '<div style="padding: 40px; font-family: sans-serif; max-width: 800px; margin: 0 auto;">' +
      '<h1 style="color: #dc2626; font-size: 32px; margin-bottom: 20px;">Erro ao Carregar MedVision AI</h1>' +
      '<div style="background: #fee2e2; border: 2px solid #dc2626; border-radius: 8px; padding: 20px; margin-bottom: 20px;">' +
        '<p style="margin: 0; font-size: 18px;"><strong>Mensagem:</strong> ' + error.message + '</p>' +
      '</div>' +
      '<pre style="background: #f5f5f5; padding: 20px; border-radius: 8px; overflow: auto; font-size: 12px;">' + error.stack + '</pre>' +
    '</div>';
}
