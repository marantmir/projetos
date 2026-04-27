/**
 * HomePage
 * 
 * Página inicial com visão geral do sistema.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { Video, Music, FileText, Sparkles, Shield, Zap } from 'lucide-react';

const HomePage = () => {
  const features = [
    {
      icon: Video,
      title: 'Análise de Vídeos Cirúrgicos',
      description: 'Detecção automática de instrumentos cirúrgicos e anomalias com YOLOv8',
      link: '/upload-video',
      color: 'blue',
      highlights: ['Pinças, tesouras, bisturis', 'Detecção de sangramento', 'Distribuição temporal']
    },
    {
      icon: Music,
      title: 'Análise de Consultas de Áudio',
      description: 'Detecção de indicadores psicológicos em consultas médicas especializadas',
      link: '/upload-audio',
      color: 'purple',
      highlights: ['Ansiedade e depressão', 'Análise acústica MFCC', '4 tipos de consulta']
    },
    {
      icon: FileText,
      title: 'Relatórios Detalhados',
      description: 'Histórico completo de análises realizadas',
      link: '/reports',
      color: 'green',
      highlights: ['Exportação Markdown', 'Busca e filtros', 'Estatísticas']
    }
  ];

  const capabilities = [
    {
      icon: Sparkles,
      title: 'IA Generativa Avançada',
      description: 'Powered by Google Gemini 2.5 Flash para relatórios ricos e detalhados'
    },
    {
      icon: Shield,
      title: 'Análise Especializada',
      description: 'Contexto clínico específico para ginecologia, pré-natal e pós-parto'
    },
    {
      icon: Zap,
      title: 'Processamento Rápido',
      description: 'Análise em tempo real com resultados em segundos'
    }
  ];

  return (
    <div className="max-w-7xl mx-auto px-8">
      {/* Hero Section */}
      <div className="text-center mb-24 py-16">
        <h1 className="text-7xl md:text-8xl font-bold bg-gradient-to-r from-blue-600 to-sky-600 bg-clip-text text-transparent dark:text-white mb-8 tracking-tight">
          MedVision AI
        </h1>
        <p className="text-2xl md:text-3xl text-gray-700 dark:text-gray-300 max-w-5xl mx-auto leading-relaxed mb-6">
          Sistema de análise multimodal com IA para vídeos cirúrgicos e consultas de áudio.
        </p>
        <p className="text-xl text-blue-600 dark:text-sky-400 font-semibold mb-10">
          Especializado em <strong>saúde da mulher</strong> com relatórios clínicos detalhados
        </p>
        <div className="mt-10 flex flex-col sm:flex-row justify-center gap-6">
          <Link
            to="/upload-video"
            className="group px-10 py-5 bg-gradient-to-r from-blue-500 to-sky-500 text-white rounded-2xl font-bold text-lg shadow-md hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 flex items-center justify-center space-x-3"
          >
            <span className="text-3xl">📹</span>
            <span>Analisar Vídeo Cirúrgico</span>
          </Link>
          <Link
            to="/upload-audio"
            className="group px-10 py-5 bg-gradient-to-r from-sky-500 to-cyan-500 text-white rounded-2xl font-bold text-lg shadow-md hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-1 flex items-center justify-center space-x-3"
          >
            <span className="text-3xl">🎤</span>
            <span>Analisar Consulta de Áudio</span>
          </Link>
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid md:grid-cols-3 gap-10 mb-24">
        {features.map((feature, index) => {
          const Icon = feature.icon;
          return (
            <Link
              key={index}
              to={feature.link}
              className="group bg-white dark:bg-gray-800 rounded-3xl shadow-md hover:shadow-xl transition-all duration-300 p-10 border-2 border-gray-100 hover:border-blue-300 dark:border-gray-700 dark:hover:border-blue-500 transform hover:scale-105 hover:-translate-y-2"
            >
              <div className={`inline-flex p-5 rounded-2xl bg-${feature.color}-100 dark:bg-${feature.color}-900 dark:bg-opacity-30 mb-8 group-hover:scale-110 transition-transform shadow-lg`}>
                <Icon size={48} className={`text-${feature.color}-600 dark:text-${feature.color}-400`} />
              </div>
              <h3 className="text-3xl font-bold text-gray-800 dark:text-white mb-4 group-hover:text-blue-600 dark:group-hover:text-sky-400 transition">
                {feature.title}
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-8 text-xl leading-relaxed">
                {feature.description}
              </p>
              <ul className="space-y-3">
                {feature.highlights.map((highlight, idx) => (
                  <li key={idx} className="text-lg text-gray-600 dark:text-gray-400 flex items-center">
                    <span className="w-3 h-3 bg-blue-500 dark:bg-sky-400 rounded-full mr-4 shadow-sm"></span>
                    {highlight}
                  </li>
                ))}
              </ul>
            </Link>
          );
        })}
      </div>

      {/* Capabilities */}
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 dark:from-gray-900 dark:to-black rounded-3xl p-16 mb-24 text-white shadow-2xl">
        <h2 className="text-5xl font-bold text-center mb-16">
          🚀 Tecnologia de Ponta
        </h2>
        <div className="grid md:grid-cols-3 gap-12">
          {capabilities.map((capability, index) => {
            const Icon = capability.icon;
            return (
              <div key={index} className="text-center p-8 rounded-2xl bg-white bg-opacity-5 hover:bg-opacity-10 transition">
                <div className="inline-flex p-6 rounded-full bg-white bg-opacity-20 mb-8">
                  <Icon size={48} className="text-medvision-accent" />
                </div>
                <h3 className="font-bold text-2xl mb-4">{capability.title}</h3>
                <p className="text-gray-300 text-lg leading-relaxed">{capability.description}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Clinical Context */}
      <div className="bg-purple-50 border-2 border-purple-200 rounded-xl p-8 mb-16">
        <h2 className="text-2xl font-bold text-purple-900 mb-4 text-center">
          🏥 Análise de Áudio Especializada em Saúde da Mulher
        </h2>
        <div className="grid md:grid-cols-4 gap-4">
          {[
            { title: 'Ginecológica', emoji: '❤️', desc: 'Consultas gerais' },
            { title: 'Pré-natal', emoji: '🤰', desc: 'Acompanhamento gestacional' },
            { title: 'Pós-parto', emoji: '👶', desc: 'Período puerperal' },
            { title: 'Geral', emoji: '🩺', desc: 'Consultas médicas' }
          ].map((type, idx) => (
            <div key={idx} className="bg-white rounded-lg p-4 text-center border border-purple-100">
              <div className="text-3xl mb-2">{type.emoji}</div>
              <h4 className="font-semibold text-purple-900">{type.title}</h4>
              <p className="text-xs text-purple-600">{type.desc}</p>
            </div>
          ))}
        </div>
        <p className="text-center text-purple-700 mt-6 text-sm">
          Detecção automática de indicadores: ansiedade, depressão, trauma, distress vocal, ansiedade gestacional
        </p>
      </div>

      {/* Disclaimer */}
      <div className="bg-yellow-50 border-2 border-yellow-200 rounded-xl p-6 text-center">
        <h3 className="font-bold text-yellow-900 mb-2">⚠️ Disclaimer Médico</h3>
        <p className="text-yellow-800 text-sm">
          Este sistema é uma <strong>ferramenta de apoio</strong> e <strong>NÃO substitui</strong> avaliação médica ou psicológica profissional.
          Todos os resultados devem ser interpretados por profissionais de saúde qualificados.
        </p>
      </div>

      {/* Tech Stack */}
      <div className="mt-16 text-center bg-gradient-to-r from-blue-50 to-sky-50 dark:from-gray-800 dark:to-gray-900 rounded-3xl p-10 shadow-md border border-gray-100 dark:border-gray-800">
        <p className="mb-6 font-bold text-3xl bg-gradient-to-r from-blue-600 to-sky-600 bg-clip-text text-transparent dark:text-white">Tecnologias</p>
        <div className="flex flex-wrap justify-center gap-5">
          <span className="px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-2xl font-semibold text-lg shadow-md hover:shadow-xl transition-all transform hover:scale-110 cursor-default">🤖 YOLOv8n</span>
          <span className="px-6 py-3 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-2xl font-semibold text-lg shadow-md hover:shadow-xl transition-all transform hover:scale-110 cursor-default">🧠 Gemini 2.5 Flash</span>
          <span className="px-6 py-3 bg-gradient-to-r from-pink-500 to-pink-600 text-white rounded-2xl font-semibold text-lg shadow-md hover:shadow-xl transition-all transform hover:scale-110 cursor-default">🎤 Librosa + MFCC</span>
          <span className="px-6 py-3 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-2xl font-semibold text-lg shadow-md hover:shadow-xl transition-all transform hover:scale-110 cursor-default">⚡ FastAPI</span>
          <span className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-cyan-600 text-white rounded-2xl font-semibold text-lg shadow-md hover:shadow-xl transition-all transform hover:scale-110 cursor-default">⚛️ React + Vite</span>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
