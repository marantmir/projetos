/**
 * Página ReportsPage
 * 
 * Lista todos os relatórios gerados com filtros e exportação.
 */

import React, { useEffect, useState } from 'react';
import { FileText, Download, Calendar, Filter, Search } from 'lucide-react';
import { listReports, downloadReportMarkdown } from '../services/api';
import toast from 'react-hot-toast';

const ReportsPage = () => {
  const [reports, setReports] = useState([]);
  const [filteredReports, setFilteredReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('all'); // 'all', 'video', 'audio'

  useEffect(() => {
    fetchReports();
  }, []);

  useEffect(() => {
    filterReports();
  }, [searchTerm, typeFilter, reports]);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const data = await listReports();
      setReports(data.reports || []);
    } catch (error) {
      toast.error('Erro ao carregar relatórios');
    } finally {
      setLoading(false);
    }
  };

  const filterReports = () => {
    let filtered = [...reports];

    // Filtro por tipo
    if (typeFilter !== 'all') {
      filtered = filtered.filter(r => r.type === typeFilter);
    }

    // Filtro por busca
    if (searchTerm) {
      filtered = filtered.filter(r => 
        r.analysis_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        r.filename?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredReports(filtered);
  };

  const handleDownload = async (analysisId, type) => {
    try {
      await downloadReportMarkdown(analysisId, type);
      toast.success('Relatório baixado!');
    } catch (error) {
      toast.error('Erro ao baixar relatório');
    }
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="min-h-screen bg-white dark:bg-gradient-to-br dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-10 transition-colors">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-16">
          <h1 className="text-6xl md:text-7xl font-bold text-gray-900 dark:text-white mb-5 tracking-tight">Relatórios</h1>
          <p className="text-2xl text-gray-600 dark:text-gray-400">Histórico de análises realizadas</p>
        </div>

        {/* Barra de filtros */}
        <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-md p-6 mb-8 flex flex-col md:flex-row gap-6 border border-gray-200 dark:border-gray-700">
          {/* Busca */}
          <div className="flex-1 relative">
            <Search size={24} className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por ID ou nome do arquivo..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="
                w-full pl-12 pr-6 py-4 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white text-lg rounded-2xl
                focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-sky-500 border border-gray-200 dark:border-gray-600
              "
            />
          </div>

          {/* Filtro por tipo */}
          <div className="flex items-center space-x-3">
            <Filter size={24} className="text-gray-600 dark:text-gray-400" />
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="
                px-6 py-4 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white text-lg rounded-2xl font-semibold
                focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-sky-500 border border-gray-200 dark:border-gray-600
              "
            >
              <option value="all">Todos</option>
              <option value="video">Vídeo</option>
              <option value="audio">Áudio</option>
            </select>
          </div>
        </div>

        {/* Lista de relatórios */}
        {loading ? (
          <div className="text-center text-gray-600 dark:text-gray-400 py-16">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-b-medvision-primary dark:border-b-medvision-accent mx-auto mb-6"></div>
            <p className="text-xl">Carregando relatórios...</p>
          </div>
        ) : filteredReports.length === 0 ? (
          <div className="text-center text-gray-600 dark:text-gray-400 py-16">
            <FileText size={64} className="mx-auto mb-6 opacity-50" />
            <p className="text-xl">Nenhum relatório encontrado</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredReports.map((report) => (
              <div
                key={report.analysis_id}
                className="bg-white dark:bg-gray-800 rounded-3xl p-8 shadow-md hover:shadow-xl transition-all duration-300 transform hover:scale-105 border border-gray-200 dark:border-gray-700"
              >
                {/* Ícone e tipo */}
                <div className="flex items-center justify-between mb-6">
                  <div className={`
                    p-4 rounded-xl shadow-lg
                    ${report.type === 'video' ? 'bg-gradient-to-br from-blue-500 to-blue-700' : 'bg-gradient-to-br from-purple-500 to-purple-700'}
                  `}>
                    <FileText size={32} className="text-white" />
                  </div>
                  <span className={`
                    px-4 py-2 rounded-xl text-sm font-bold shadow-md
                    ${report.type === 'video' 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-purple-500 text-white'
                    }
                  `}>
                    {report.type === 'video' ? 'Vídeo' : 'Áudio'}
                  </span>
                </div>

                {/* Informações */}
                <div className="mb-6">
                  <h3 className="text-gray-900 dark:text-white font-bold text-xl mb-3 truncate">
                    {report.filename || 'Sem nome'}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 text-sm font-mono mb-3 truncate">
                    ID: {report.analysis_id}
                  </p>
                  <div className="flex items-center text-gray-500 dark:text-gray-400 text-sm">
                    <Calendar size={18} className="mr-2" />
                    {formatDate(report.timestamp)}
                  </div>
                </div>

                {/* Estatísticas rápidas */}
                <div className="border-t-2 border-gray-200 dark:border-gray-700 pt-6 mb-6">
                  <div className="grid grid-cols-2 gap-4 text-base">
                    {report.type === 'video' ? (
                      <>
                        <div>
                          <p className="text-gray-500 dark:text-gray-400 text-sm">Frames</p>
                          <p className="text-gray-900 dark:text-white font-bold text-lg">{report.total_frames || 0}</p>
                        </div>
                        <div>
                          <p className="text-gray-500 dark:text-gray-400 text-sm">Anomalias</p>
                          <p className="text-gray-900 dark:text-white font-bold text-lg">{report.total_anomalies || 0}</p>
                        </div>
                      </>
                    ) : (
                      <>
                        <div>
                          <p className="text-gray-500 dark:text-gray-400 text-sm">Duração</p>
                          <p className="text-gray-900 dark:text-white font-bold text-lg">{report.duration?.toFixed(1) || 0}s</p>
                        </div>
                        <div>
                          <p className="text-gray-500 dark:text-gray-400 text-sm">Segmentos</p>
                          <p className="text-gray-900 dark:text-white font-bold text-lg">{report.segments || 0}</p>
                        </div>
                      </>
                    )}
                  </div>
                </div>

                {/* Botão de download */}
                <button
                  onClick={() => handleDownload(report.analysis_id, report.type)}
                  className="
                    w-full flex items-center justify-center px-6 py-4 text-lg
                    bg-gradient-to-r from-blue-500 to-sky-500 text-white rounded-2xl font-bold
                    shadow-md hover:shadow-xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-1
                  "
                >
                  <Download size={22} className="mr-3" />
                  Baixar Relatório
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ReportsPage;
