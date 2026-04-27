/**
 * MarkdownRenderer
 * 
 * Componente para renderizar markdown com suporte a GFM (GitHub Flavored Markdown).
 * Inclui botões para copiar e baixar o conteúdo.
 */

import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Copy, Download, Check } from 'lucide-react';
import toast from 'react-hot-toast';

const MarkdownRenderer = ({ content, title = 'Relatório', filename = 'relatorio.md' }) => {
  const [copied, setCopied] = useState(false);

  // Pré-processar conteúdo para corrigir \n literais e formatar segmentos como tabela
  const processContent = (rawContent) => {
    if (!rawContent) return '';
    
    // Substituir \n literais por quebras de linha reais
    let processed = rawContent.replace(/\\n/g, '\n');
    
    // Detectar e formatar segmentos como tabela
    const segmentRegex = /Segmento (\d+): ([\d.]+)s - ([\d.]+)s\n - Indicadores: ([^\n]+)\n - Confiança: ([\d]+)%/g;
    const segments = [];
    let match;
    
    while ((match = segmentRegex.exec(processed)) !== null) {
      segments.push({
        numero: match[1],
        inicio: match[2],
        fim: match[3],
        indicadores: match[4],
        confianca: match[5]
      });
    }
    
    // Se encontrou segmentos, criar tabela
    if (segments.length > 0) {
      const tableHeader = '\n| Segmento | Período | Indicadores | Confiança |\n|----------|---------|-------------|-----------|\n';
      const tableRows = segments.map(s => 
        `| ${s.numero} | ${s.inicio}s - ${s.fim}s | ${s.indicadores} | ${s.confianca}% |`
      ).join('\n');
      
      // Substituir primeira ocorrência dos segmentos pela tabela
      const firstSegmentIndex = processed.indexOf('Segmento 1:');
      if (firstSegmentIndex !== -1) {
        const lastSegmentMatch = processed.match(/Segmento \d+:[^]*?Confiança: \d+%/);
        if (lastSegmentMatch) {
          const lastSegmentEnd = processed.indexOf(lastSegmentMatch[0]) + lastSegmentMatch[0].length;
          processed = processed.substring(0, firstSegmentIndex) + 
                     tableHeader + tableRows + '\n' +
                     processed.substring(lastSegmentEnd);
        }
      }
    }
    
    return processed;
  };

  const processedContent = processContent(content);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    toast.success('Relatório copiado!');
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    toast.success('Relatório baixado!');
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-md hover:shadow-lg transition-shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      {/* Header com botões */}
      <div className="bg-gradient-to-r from-blue-500 to-sky-500 p-4 flex items-center justify-between">
        <h3 className="text-white font-semibold text-lg flex items-center">
          <span className="mr-2">📋</span>
          {title}
        </h3>
        <div className="flex space-x-2">
          <button
            onClick={handleCopy}
            className="px-4 py-2 bg-white bg-opacity-20 hover:bg-opacity-30 text-white rounded-lg transition flex items-center space-x-2"
            title="Copiar para área de transferência"
          >
            {copied ? (
              <>
                <Check size={18} />
                <span className="hidden sm:inline">Copiado!</span>
              </>
            ) : (
              <>
                <Copy size={18} />
                <span className="hidden sm:inline">Copiar</span>
              </>
            )}
          </button>
          <button
            onClick={handleDownload}
            className="px-4 py-2 bg-white bg-opacity-20 hover:bg-opacity-30 text-white rounded-lg transition flex items-center space-x-2"
            title="Baixar arquivo Markdown"
          >
            <Download size={18} />
            <span className="hidden sm:inline">Download</span>
          </button>
        </div>
      </div>

      {/* Conteúdo do markdown */}
      <div className="p-6 max-h-[600px] overflow-y-auto">
        <div className="prose prose-slate dark:prose-invert max-w-none prose-table:text-sm">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {processedContent}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
};

export default MarkdownRenderer;
