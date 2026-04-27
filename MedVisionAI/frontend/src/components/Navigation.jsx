/**
 * Componente Navigation
 * 
 * Barra de navegação principal entre páginas de vídeo e áudio.
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Video, Music, FileText, Home, Moon, Sun } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

const Navigation = () => {
  const location = useLocation();
  const { isDark, toggleTheme } = useTheme();

  const navItems = [
    {
      path: '/',
      icon: Home,
      label: 'Início',
      description: 'Página inicial'
    },
    {
      path: '/upload-video',
      icon: Video,
      label: 'Vídeos Cirúrgicos',
      description: 'Análise de instrumentos cirúrgicos'
    },
    {
      path: '/upload-audio',
      icon: Music,
      label: 'Consultas de Áudio',
      description: 'Análise psicológica de consultas'
    },
    {
      path: '/reports',
      icon: FileText,
      label: 'Relatórios',
      description: 'Histórico de análises'
    }
  ];

  return (
    <nav className="bg-white dark:bg-gray-900 shadow-lg border-b-2 border-blue-100 dark:border-gray-800 transition-colors">
      <div className="container mx-auto px-6">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-sky-500 rounded-2xl flex items-center justify-center shadow-md hover:shadow-lg transition-shadow">
              <span className="text-white font-bold text-2xl">M</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-sky-600 bg-clip-text text-transparent dark:text-white">MedVision AI</h1>
              <p className="text-sm text-blue-600 dark:text-gray-400">Análise Multimodal</p>
            </div>
          </Link>

          {/* Navigation Links + Theme Toggle */}
          <div className="flex items-center space-x-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`
                    flex items-center space-x-2 px-5 py-3 rounded-2xl text-base
                    transition-all duration-300 group font-semibold
                    ${isActive 
                      ? 'bg-gradient-to-r from-blue-500 to-sky-500 text-white shadow-md scale-105' 
                      : 'text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-gray-800 hover:text-blue-600 dark:hover:text-blue-400 hover:shadow-sm'
                    }
                  `}
                  title={item.description}
                >
                  <Icon 
                    size={22} 
                    className={isActive ? '' : 'group-hover:scale-110 transition-transform'}
                  />
                  <span className="font-medium hidden md:inline">{item.label}</span>
                </Link>
              );
            })}

            {/* Botão de modo escuro/claro */}
            <button
              onClick={toggleTheme}
              className="ml-4 p-3 rounded-2xl bg-blue-50 dark:bg-gray-700 text-blue-600 dark:text-yellow-300 hover:bg-blue-100 dark:hover:bg-gray-600 transition-all hover:scale-110 shadow-md hover:shadow-lg border border-blue-200 dark:border-gray-600"
              title={isDark ? '☀️ Ativar Modo Claro' : '🌙 Ativar Modo Escuro'}
            >
              {isDark ? <Sun size={22} className="animate-pulse" /> : <Moon size={22} />}
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
