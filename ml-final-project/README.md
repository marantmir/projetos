# Projeto Final de ML para Recomendação de Graduação

Este projeto implementa um pipeline completo de Machine Learning para recomendar uma graduação com base no perfil e nas preferências de um estudante.

O fluxo cobre:

- análise exploratória dos dados
- preprocessamento
- treinamento e comparação de modelos
- avaliação de métricas
- persistência de artefatos
- disponibilização do modelo via API FastAPI
- deploy simples no Render

O dataset principal está em `data/dataset_graduacao_indicada.csv` e a variável alvo prevista é `Graduacao_Indicada`.

## Visão geral

O projeto recebe dados brutos sobre idade, tempo estimado de formação, curso técnico e preferências por áreas de interesse. A partir disso, o pipeline transforma os dados, treina modelos de classificação e expõe a inferência por API e interface web.

Hoje o treinamento compara estes modelos:

- `LogisticRegression`
- `RandomForest`
- `XGBoost`
- `GradientBoosting`

O melhor modelo é escolhido priorizando `f1_macro` e, em caso de empate, `accuracy`.

## Como o projeto funciona

O fluxo principal do projeto é este:

1. Ler o CSV bruto.
2. Gerar EDA com gráficos e insights simples.
3. Aplicar preprocessamento com separação entre variáveis numéricas e categóricas.
4. Salvar datasets processados de treino e teste.
5. Treinar e comparar os modelos.
6. Salvar o melhor modelo e os artefatos de deploy.
7. Expor a predição pela API.

### Pré-processamento

O pipeline de preparação inclui:

- imputação simples
- `StandardScaler` para colunas numéricas
- `OneHotEncoder` para variáveis categóricas
- split treino/teste com estratificação e `random_state=42`

### Saídas geradas

Após rodar o pipeline completo, os principais artefatos são:

- `artifacts/preprocess_pipeline.joblib`
- `artifacts/model.joblib`
- `artifacts/deploy_logreg.joblib`
- `artifacts/deploy_rf_compacto.joblib`
- `artifacts/deploy_xgb_compacto.joblib`
- `artifacts/deploy_gb_compacto.joblib`
- `reports/eda.html`
- `reports/preprocess.html`
- `reports/model_report.html`
- `data/processed/train.parquet`
- `data/processed/test.parquet`

## Como rodar localmente

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Executar o pipeline completo

```bash
python -B -m src.run_pipeline
```

Esse comando executa EDA, preprocessamento, treinamento, geração de relatórios e tracking local no MLflow.

### 3. Subir a API

```bash
uvicorn app.main:app --reload
```

URLs úteis após subir a aplicação:

- Interface web: `http://127.0.0.1:8000/`
- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health check: `http://127.0.0.1:8000/health`
- Relatório EDA: `http://127.0.0.1:8000/reports/eda`
- Relatório de preprocessamento: `http://127.0.0.1:8000/reports/preprocess`
- Relatório de treinamento: `http://127.0.0.1:8000/reports/model`

## Como usar o modelo

O jeito principal de usar o modelo neste projeto é pela API FastAPI.

### Endpoints principais

- `GET /`
- `GET /health`
- `POST /predict`
- `POST /web/predict`

Os endpoints `/reports/eda`, `/reports/preprocess` e `/reports/model` também servem os relatórios HTML já gerados pelo pipeline.

### Entrada esperada

O endpoint `POST /predict` recebe um JSON com estes campos:

- `Idade`
- `Curso_Tecnico`
- `Anos_Para_Formar`
- `Gosta_Matematica`
- `Gosta_Programacao`
- `Gosta_Biologia`
- `Gosta_Fisica`
- `Gosta_Quimica`
- `Gosta_Arte_Design`
- `Gosta_Comunicacao`
- `Gosta_Negocios`
- `Gosta_Historia`
- `Gosta_Geografia`

Regras de validação principais:

- `Idade`: de 14 a 100
- `Anos_Para_Formar`: de 1 a 15
- preferências: de 1 a 5
- `Curso_Tecnico`: aceita `Sim`, `Nao` e `Não`

### Exemplo de requisição

```json
{
  "Idade": 45,
  "Curso_Tecnico": "Não",
  "Anos_Para_Formar": 7,
  "Gosta_Matematica": 1,
  "Gosta_Programacao": 4,
  "Gosta_Biologia": 2,
  "Gosta_Fisica": 3,
  "Gosta_Quimica": 5,
  "Gosta_Arte_Design": 3,
  "Gosta_Comunicacao": 1,
  "Gosta_Negocios": 1,
  "Gosta_Historia": 5,
  "Gosta_Geografia": 1
}
```

### Exemplo com `curl`

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d "{\"Idade\":45,\"Curso_Tecnico\":\"Não\",\"Anos_Para_Formar\":7,\"Gosta_Matematica\":1,\"Gosta_Programacao\":4,\"Gosta_Biologia\":2,\"Gosta_Fisica\":3,\"Gosta_Quimica\":5,\"Gosta_Arte_Design\":3,\"Gosta_Comunicacao\":1,\"Gosta_Negocios\":1,\"Gosta_Historia\":5,\"Gosta_Geografia\":1}"
```

### Resposta esperada

O retorno do `POST /predict` segue este formato:

```json
{
  "prediction": "Ciência da Computação",
  "probability": 94.21,
  "model_name": "XGBoostCompacto"
}
```

Campos da resposta:

- `prediction`: graduação indicada pelo modelo
- `probability`: confiança da classe prevista, em percentual
- `model_name`: nome do modelo carregado na API

### Uso pela interface web

Se preferir, basta abrir `http://127.0.0.1:8000/`, preencher o formulário e enviar a predição pelo navegador.

## Variantes do modelo na API

A API carrega duas coisas na inicialização:

- o pipeline de preprocessamento em `artifacts/preprocess_pipeline.joblib`
- um artefato de modelo selecionado pela variável de ambiente `MODEL_VARIANT`

Valores suportados por `MODEL_VARIANT`:

- `logreg`
- `rf_compacto`
- `xgb_compacto`
- `gb_compacto`

Exemplo em PowerShell:

```powershell
$env:MODEL_VARIANT="xgb_compacto"
uvicorn app.main:app --reload
```

Se a variante for inválida ou se os artefatos não existirem, o endpoint `GET /health` responde com status degradado.

## Estrutura do repositório

```text
.
|-- app/
|   |-- main.py
|   |-- predictor.py
|   `-- templates/
|-- artifacts/
|-- data/
|   |-- dataset_graduacao_indicada.csv
|   `-- processed/
|-- reports/
|   `-- figures/
|-- src/
|   |-- eda.py
|   |-- preprocess.py
|   |-- train.py
|   `-- run_pipeline.py
|-- requirements.txt
`-- render.yaml
```

## Comandos úteis

### Rodar apenas a EDA

```bash
python -B -m src.eda
```

### Rodar apenas o preprocessamento

```bash
python -B -m src.preprocess --input data/dataset_graduacao_indicada.csv --outdir data/processed --artifacts artifacts --reports reports
```

### Rodar apenas o treinamento

```bash
python -B -m src.train --data_dir data/processed --artifacts artifacts --reports reports
```

### Ver experimentos no MLflow

```bash
mlflow ui --backend-store-uri mlruns
```

Interface local do MLflow:

```text
http://127.0.0.1:5000
```

## Deploy no Render

O projeto está configurado para deploy simples sem Docker usando `render.yaml`.

Configuração atual:

- runtime Python
- build com `pip install -r requirements.txt`
- start com `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- health check em `/health`

Valor padrão configurado hoje:

```text
MODEL_VARIANT=xgb_compacto
```

## CI/CD

O workflow de CI valida:

- instalação de dependências
- compilação/importação dos módulos
- entrypoints principais com `--help`
- presença de arquivos obrigatórios versionados
- smoke tests da API

O treino completo não roda na CI para manter a esteira simples e evitar regravação de artefatos.

## Dependências principais

- `pandas`
- `numpy`
- `matplotlib`
- `seaborn`
- `scikit-learn`
- `xgboost`
- `joblib`
- `mlflow`
- `pyarrow`
- `fastapi`
- `httpx`
- `uvicorn`
- `pydantic`
- `jinja2`
- `python-multipart`
