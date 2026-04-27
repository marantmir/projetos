/**
 * Componente Footer
 * 
 * Rodapé da aplicação MedVision AI
 */

import React from 'react';
import { Heart } from 'lucide-react';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gradient-to-r from-blue-900 to-sky-900 text-white mt-16">
      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Sobre */}
          <div>
            <h3 className="text-xl font-bold mb-3">MedVision AI</h3>
            <p className="text-blue-200 text-sm leading-relaxed">
              Plataforma de análise médica com IA para vídeos cirúrgicos e consultas de áudio.
            </p>
          </div>

          {/* Links Rápidos */}
          <div>
            <h3 className="text-xl font-bold mb-3">Links Rápidos</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="/" className="text-blue-200 hover:text-white transition-colors">
                  Início
                </a>
              </li>
              <li>
                <a href="/upload-video" className="text-blue-200 hover:text-white transition-colors">
                  Upload de Vídeo
                </a>
              </li>
              <li>
                <a href="/upload-audio" className="text-blue-200 hover:text-white transition-colors">
                  Upload de Áudio
                </a>
              </li>
              <li>
                <a href="/reports" className="text-blue-200 hover:text-white transition-colors">
                  Relatórios
                </a>
              </li>
            </ul>
          </div>

          {/* Contato */}
          <div>
            <h3 className="text-xl font-bold mb-3">Tecnologias</h3>
            <ul className="space-y-2 text-sm text-blue-200">
              <li>🤖 Google Gemini 2.5 Flash</li>
              <li>🎯 YOLOv8 para Detecção</li>
              <li>⚡ FastAPI + React</li>
              <li>🔄 WebSocket Real-Time</li>
            </ul>
          </div>
        </div>

        {/* Copyright */}
        <div className="border-t border-blue-700 mt-8 pt-6 text-center">
          <p className="text-blue-200 text-sm flex items-center justify-center gap-2">
            Feito com <Heart size={16} className="text-red-400 fill-red-400" /> para o TechChallenge F04 © {currentYear}
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
