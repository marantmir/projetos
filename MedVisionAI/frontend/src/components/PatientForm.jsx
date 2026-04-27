/**
 * PatientForm
 * 
 * Formulário para coletar dados do paciente antes da análise.
 * Inclui: Nome, Idade, Histórico de gestação, Endereço, Telefone
 */

import React, { useState } from 'react';
import { User, Calendar, Baby, MapPin, Phone, Check, X } from 'lucide-react';

const PatientForm = ({ onSubmit, onCancel, initialData = null }) => {
  const [formData, setFormData] = useState({
    nome: initialData?.nome || '',
    idade: initialData?.idade || '',
    ja_foi_mae: initialData?.ja_foi_mae !== undefined ? initialData.ja_foi_mae : null,
    numero_gestacoes: initialData?.numero_gestacoes || '',
    endereco: initialData?.endereco || '',
    telefone: initialData?.telefone || '',
  });

  const [errors, setErrors] = useState({});

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Limpar erro do campo quando usuário começa a digitar
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.nome.trim()) {
      newErrors.nome = 'Nome é obrigatório';
    }

    if (!formData.idade || formData.idade < 1 || formData.idade > 120) {
      newErrors.idade = 'Idade inválida (1-120 anos)';
    }

    if (formData.ja_foi_mae === null) {
      newErrors.ja_foi_mae = 'Selecione uma opção';
    }

    if (formData.ja_foi_mae && (!formData.numero_gestacoes || formData.numero_gestacoes < 1)) {
      newErrors.numero_gestacoes = 'Número de gestações é obrigatório';
    }

    if (!formData.telefone.trim()) {
      newErrors.telefone = 'Telefone é obrigatório';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validate()) {
      const cleanedData = {
        ...formData,
        idade: parseInt(formData.idade),
        numero_gestacoes: formData.ja_foi_mae ? parseInt(formData.numero_gestacoes || 0) : 0,
      };
      onSubmit(cleanedData);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-3xl p-8 shadow-md border border-gray-200 dark:border-gray-700">
      <div className="mb-8">
        <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-sky-600 bg-clip-text text-transparent dark:text-white mb-2">
          Dados do Paciente
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Preencha as informações antes de iniciar a análise
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Nome */}
        <div>
          <label className="flex items-center text-gray-700 dark:text-gray-300 font-semibold mb-2">
            <User size={20} className="mr-2 text-blue-500" />
            Nome Completo *
          </label>
          <input
            type="text"
            value={formData.nome}
            onChange={(e) => handleChange('nome', e.target.value)}
            className={`
              w-full px-4 py-3 rounded-2xl border-2 
              ${errors.nome 
                ? 'border-red-500 focus:border-red-600' 
                : 'border-gray-200 dark:border-gray-700 focus:border-blue-500 dark:focus:border-sky-500'
              }
              bg-white dark:bg-gray-900 text-gray-900 dark:text-white
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50
              transition-all
            `}
            placeholder="Maria Silva Santos"
          />
          {errors.nome && (
            <p className="text-red-500 text-sm mt-1 flex items-center">
              <X size={14} className="mr-1" />
              {errors.nome}
            </p>
          )}
        </div>

        {/* Idade */}
        <div>
          <label className="flex items-center text-gray-700 dark:text-gray-300 font-semibold mb-2">
            <Calendar size={20} className="mr-2 text-blue-500" />
            Idade *
          </label>
          <input
            type="number"
            min="1"
            max="120"
            value={formData.idade}
            onChange={(e) => handleChange('idade', e.target.value)}
            className={`
              w-full px-4 py-3 rounded-2xl border-2
              ${errors.idade 
                ? 'border-red-500 focus:border-red-600' 
                : 'border-gray-200 dark:border-gray-700 focus:border-blue-500 dark:focus:border-sky-500'
              }
              bg-white dark:bg-gray-900 text-gray-900 dark:text-white
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50
              transition-all
            `}
            placeholder="32"
          />
          {errors.idade && (
            <p className="text-red-500 text-sm mt-1 flex items-center">
              <X size={14} className="mr-1" />
              {errors.idade}
            </p>
          )}
        </div>

        {/* Já foi mãe antes? */}
        <div>
          <label className="flex items-center text-gray-700 dark:text-gray-300 font-semibold mb-3">
            <Baby size={20} className="mr-2 text-blue-500" />
            Histórico de Gestação *
          </label>
          <div className="flex gap-4">
            <button
              type="button"
              onClick={() => handleChange('ja_foi_mae', true)}
              className={`
                flex-1 px-6 py-4 rounded-2xl font-semibold transition-all
                ${formData.ja_foi_mae === true
                  ? 'bg-gradient-to-r from-blue-500 to-sky-500 text-white shadow-md'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }
              `}
            >
              Sim, já foi mãe
            </button>
            <button
              type="button"
              onClick={() => {
                handleChange('ja_foi_mae', false);
                handleChange('numero_gestacoes', '');
              }}
              className={`
                flex-1 px-6 py-4 rounded-2xl font-semibold transition-all
                ${formData.ja_foi_mae === false
                  ? 'bg-gradient-to-r from-blue-500 to-sky-500 text-white shadow-md'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }
              `}
            >
              Não, primeira gestação
            </button>
          </div>
          {errors.ja_foi_mae && (
            <p className="text-red-500 text-sm mt-1 flex items-center">
              <X size={14} className="mr-1" />
              {errors.ja_foi_mae}
            </p>
          )}
        </div>

        {/* Número de gestações (se já foi mãe) */}
        {formData.ja_foi_mae && (
          <div className="animate-fadeIn">
            <label className="flex items-center text-gray-700 dark:text-gray-300 font-semibold mb-2">
              <Baby size={20} className="mr-2 text-blue-500" />
              Número de Gestações Anteriores *
            </label>
            <input
              type="number"
              min="1"
              value={formData.numero_gestacoes}
              onChange={(e) => handleChange('numero_gestacoes', e.target.value)}
              className={`
                w-full px-4 py-3 rounded-2xl border-2
                ${errors.numero_gestacoes 
                  ? 'border-red-500 focus:border-red-600' 
                  : 'border-gray-200 dark:border-gray-700 focus:border-blue-500 dark:focus:border-sky-500'
                }
                bg-white dark:bg-gray-900 text-gray-900 dark:text-white
                focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50
                transition-all
              `}
              placeholder="2"
            />
            {errors.numero_gestacoes && (
              <p className="text-red-500 text-sm mt-1 flex items-center">
                <X size={14} className="mr-1" />
                {errors.numero_gestacoes}
              </p>
            )}
          </div>
        )}

        {/* Endereço (opcional) */}
        <div>
          <label className="flex items-center text-gray-700 dark:text-gray-300 font-semibold mb-2">
            <MapPin size={20} className="mr-2 text-blue-500" />
            Endereço
            <span className="text-gray-400 text-sm ml-2">(opcional)</span>
          </label>
          <input
            type="text"
            value={formData.endereco}
            onChange={(e) => handleChange('endereco', e.target.value)}
            className="
              w-full px-4 py-3 rounded-2xl border-2 border-gray-200 dark:border-gray-700
              bg-white dark:bg-gray-900 text-gray-900 dark:text-white
              focus:outline-none focus:border-blue-500 dark:focus:border-sky-500
              focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50
              transition-all
            "
            placeholder="Rua das Flores, 123 - São Paulo, SP"
          />
        </div>

        {/* Telefone */}
        <div>
          <label className="flex items-center text-gray-700 dark:text-gray-300 font-semibold mb-2">
            <Phone size={20} className="mr-2 text-blue-500" />
            Telefone de Contato *
          </label>
          <input
            type="tel"
            value={formData.telefone}
            onChange={(e) => handleChange('telefone', e.target.value)}
            className={`
              w-full px-4 py-3 rounded-2xl border-2
              ${errors.telefone 
                ? 'border-red-500 focus:border-red-600' 
                : 'border-gray-200 dark:border-gray-700 focus:border-blue-500 dark:focus:border-sky-500'
              }
              bg-white dark:bg-gray-900 text-gray-900 dark:text-white
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50
              transition-all
            `}
            placeholder="(11) 98765-4321"
          />
          {errors.telefone && (
            <p className="text-red-500 text-sm mt-1 flex items-center">
              <X size={14} className="mr-1" />
              {errors.telefone}
            </p>
          )}
        </div>

        {/* Botões */}
        <div className="flex gap-4 pt-4">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="
                flex-1 px-6 py-4 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300
                rounded-2xl font-semibold hover:bg-gray-300 dark:hover:bg-gray-600
                transition-all duration-300 shadow-md hover:shadow-lg
                flex items-center justify-center
              "
            >
              <X size={20} className="mr-2" />
              Cancelar
            </button>
          )}
          <button
            type="submit"
            className="
              flex-1 px-6 py-4 bg-gradient-to-r from-blue-500 to-sky-500 text-white
              rounded-2xl font-semibold shadow-md hover:shadow-xl
              transition-all duration-300 transform hover:scale-105 hover:-translate-y-1
              flex items-center justify-center
            "
          >
            <Check size={20} className="mr-2" />
            Prosseguir com Análise
          </button>
        </div>
      </form>

      <p className="text-xs text-gray-500 dark:text-gray-400 text-center mt-6">
        * Campos obrigatórios
      </p>
    </div>
  );
};

export default PatientForm;
