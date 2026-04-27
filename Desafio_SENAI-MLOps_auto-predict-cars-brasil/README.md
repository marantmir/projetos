---
title: AutoPredict BR — Precificação de Veículos
emoji: 🚗
colorFrom: green
colorTo: blue
sdk: docker
app_port: 8501
pinned: false
license: mit
---

# 🚗 AutoPredict BR — Precificação de Veículos Brasil

**Projeto:** SESI/SENAI S/C - UNISENAI  
**Curso:** Pós-graduação em Inteligência Artificial Aplicada  
**Unidade Curricular:** Aprendizado de Máquina  
**Professor:** Regis Cardoso  
**Grupo:** 2 (Elias, Bruno e João Clemente)

**Pipeline Completo de Machine Learning — UC Aprendizado de Máquina 2026/1**

> ⚠️ Este conteúdo é destinado apenas para fins educacionais. Os dados exibidos são ilustrativos e podem não corresponder a situações reais.

## 📋 Descrição do Projeto

Este projeto implementa um pipeline completo de Machine Learning seguindo a metodologia **CRISP-DM** para prever o valor de venda de veículos usados no Brasil. O sistema utiliza dados de 10.000 veículos com características como marca, modelo, ano, quilometragem, câmbio, combustível e cor.

## 🎯 Objetivo

Construir um modelo preditivo capaz de estimar o preço de venda de um veículo usado com base em suas características, seguindo todas as etapas de um projeto de ML profissional.

## 🔗 Deploy

- **Repositório GitHub:** [Desafio SENAI MLOps Auto Predict Cars Brasil](https://github.com/eliasgdeveloper/Desafio_SENAI-MLOps_auto-predict-cars-brasil)  
- **Aplicação no Hugging Face Spaces:** [Auto Predict Cars Brasil](https://huggingface.co/spaces/elias-developer/Auto_Predict_Cars_Brasil)

## 🏗️ Estrutura do Projeto

desafio_final/
├── app.py                      # Aplicação Streamlit (deploy)
├── train.py                    # Script de treinamento completo
├── dataset_carros_brasil.csv   # Dataset original
├── requirements.txt            # Dependências do projeto
├── README.md                   # Documentação
├── modelo/                     # Artefatos do modelo
│   ├── melhor_modelo.pkl       # Modelo treinado
│   ├── label_encoders.pkl      # Encoders categóricos
│   ├── scaler.pkl              # Scaler numérico
│   ├── feature_names.pkl       # Nomes das features
│   ├── categorias.json         # Categorias para o app
│   ├── melhor_modelo_info.json # Info do melhor modelo
│   └── resultados_modelos.csv  # Comparação de modelos
├── graficos/                   # Gráficos da EDA
│   ├── distribuicao_valor_venda.png
│   ├── correlacao.png
│   ├── valor_medio_marca.png
│   ├── valor_vs_ano.png
│   ├── valor_vs_km.png
│   ├── valor_por_cambio.png
│   ├── valor_por_combustivel.png
│   └── comparacao_modelos.png
└── mlruns/                     # Experimentos MLflow

## 📊 Dataset

| Variável | Descrição |
|----------|-----------|
| Marca | Fabricante do veículo |
| Modelo | Modelo do veículo |
| Ano | Ano de fabricação |
| Quilometragem | Distância percorrida (km) |
| Cor | Cor do carro |
| Cambio | Tipo de câmbio (Manual/Automático) |
| Combustivel | Tipo de combustível (Flex/Gasolina/Diesel) |
| Portas | Número de portas |
| **Valor_Venda** | **Valor de venda (variável alvo)** |

## 🧪 Metodologia (CRISP-DM)

### 1. Entendimento do Negócio
Problema de regressão: prever o preço de carros usados no mercado brasileiro.

### 2. Entendimento dos Dados (EDA)
- Análise descritiva completa
- Distribuição do valor de venda
- Correlações entre variáveis
- Análise por marcas, câmbio, combustível

### 3. Preparação dos Dados
- Label Encoding para variáveis categóricas
- Standard Scaler para variáveis numéricas
- Split treino/teste (80/20)

### 4. Modelagem
Modelos treinados e comparados:
| Modelo | Descrição |
|--------|-----------|
| Linear Regression | Regressão linear simples |
| Ridge | Regularização L2 |
| Lasso | Regularização L1 |
| Decision Tree | Árvore de decisão |
| Random Forest | Ensemble (bagging) |
| Gradient Boosting | Ensemble (boosting) |

### 5. Avaliação
Métricas utilizadas:
- **MAE** — Erro Absoluto Médio
- **RMSE** — Raiz do Erro Quadrático Médio
- **R²** — Coeficiente de Determinação
- **CV R²** — Validação Cruzada (5 folds)

### 6. MLOps
- Rastreamento de experimentos com **MLflow**
- Registro de parâmetros, métricas e modelos
- Salvamento automatizado do melhor modelo

## 🚀 Como Rodar Localmente

### Pré-requisitos
- Python 3.10+

### Instalação

```bash
# Clonar repositório
git clone git@github.com:eliasgdeveloper/Desafio_SENAI-MLOps_auto-predict-cars-brasil.git
cd Desafio_SENAI-MLOps_auto-predict-cars-brasil

# Instalar dependências
pip install -r requirements.txt
