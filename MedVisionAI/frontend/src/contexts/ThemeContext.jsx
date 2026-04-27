/**
 * ThemeContext
 * 
 * Contexto global para gerenciar tema claro/escuro.
 */

import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [isDark, setIsDark] = useState(() => {
    // Carrega preferência salva - padrão é LIGHT MODE
    const saved = localStorage.getItem('theme');
    if (saved) {
      return saved === 'dark';
    }
    // Sempre começa em light mode (padrão)
    return false;
  });

  useEffect(() => {
    // Salva preferência
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    
    // Aplica classe no documento HTML
    const root = document.documentElement;
    if (isDark) {
      root.classList.add('dark');
      root.style.colorScheme = 'dark';
    } else {
      root.classList.remove('dark');
      root.style.colorScheme = 'light';
    }
    
    console.log('[ThemeContext] Tema alterado para:', isDark ? 'DARK' : 'LIGHT');
  }, [isDark]);

  const toggleTheme = () => setIsDark(!isDark);

  return (
    <ThemeContext.Provider value={{ isDark, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export default ThemeContext;
