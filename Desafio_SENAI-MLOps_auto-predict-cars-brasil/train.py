"""
Pipeline Completo de Machine Learning - Predição de Preço de Carros no Brasil
Seguindo metodologia CRISP-DM

Etapas:
1. Entendimento do Negócio
2. Entendimento dos Dados (EDA)
3. Preparação dos Dados
4. Modelagem (Treinamento e Comparação)
5. Avaliação
6. Implantação (Deploy)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import mlflow
import mlflow.sklearn
import joblib
import os
import json
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
import warnings
warnings.filterwarnings('ignore')


# ENTENDIMENTO DO NEGÓCIO

print("=" * 60)
print("PIPELINE DE ML - PREDIÇÃO DE PREÇO DE CARROS")
print("=" * 60)


# ENTENDIMENTO DOS DADOS (EDA)

print("\n ETAPA 2: Análise Exploratória dos Dados (EDA)")
print("-" * 60)

df = pd.read_csv("dataset_carros_brasil.csv")

print(f"\nShape do dataset (bruto): {df.shape}")

# --- Limpeza inicial ---
df['Quilometragem'] = pd.to_numeric(df['Quilometragem'], errors='coerce')

print(f"Nulos antes da limpeza: Ano={df['Ano'].isnull().sum()}, Km={df['Quilometragem'].isnull().sum()}")

df = df.dropna().reset_index(drop=True)
df['Ano'] = df['Ano'].astype(int)
df['Quilometragem'] = df['Quilometragem'].astype(int)

print(f"Shape após limpeza de nulos: {df.shape}")

# --- Tratamento de outliers no Valor_Venda (IQR) ---
Q1 = df['Valor_Venda'].quantile(0.25)
Q3 = df['Valor_Venda'].quantile(0.75)
IQR = Q3 - Q1
limite_inferior = Q1 - 1.5 * IQR
limite_superior = Q3 + 1.5 * IQR
outliers_antes = len(df)
df = df[(df['Valor_Venda'] >= limite_inferior) & (df['Valor_Venda'] <= limite_superior)].reset_index(drop=True)
print(f"Outliers removidos em Valor_Venda: {outliers_antes - len(df)}")
print(f"Shape final: {df.shape}")

# Salvar dataset limpo para uso no app
df.to_csv('dataset_limpo.csv', index=False)

print("\n--- Primeiras linhas ---")
print(df.head())

print("\n--- Estatísticas descritivas ---")
print(df.describe())

print("\n--- Valores únicos por coluna categórica ---")
cat_cols = ['Marca', 'Modelo', 'Cor', 'Cambio', 'Combustivel']
for col in cat_cols:
    print(f"  {col}: {df[col].nunique()} valores únicos")

# Criar pasta para gráficos
os.makedirs("graficos", exist_ok=True)

# Gráfico 1: Distribuição do Valor de Venda
fig, ax = plt.subplots(figsize=(10, 5))
sns.histplot(df['Valor_Venda'], bins=50, kde=True, ax=ax)
ax.set_title('Distribuição do Valor de Venda')
ax.set_xlabel('Valor (R$)')
ax.set_ylabel('Frequência')
plt.tight_layout()
fig.savefig('graficos/distribuicao_valor_venda.png', dpi=100)
plt.close()

# Gráfico 2: Correlação entre variáveis numéricas
fig, ax = plt.subplots(figsize=(8, 6))
num_cols_plot = df.select_dtypes(include=[np.number]).columns
sns.heatmap(df[num_cols_plot].corr(), annot=True, cmap='coolwarm', fmt='.2f', ax=ax)
ax.set_title('Matriz de Correlação')
plt.tight_layout()
fig.savefig('graficos/correlacao.png', dpi=100)
plt.close()

# Gráfico 3: Valor médio por Marca
fig, ax = plt.subplots(figsize=(12, 5))
df.groupby('Marca')['Valor_Venda'].mean().sort_values(ascending=False).plot(kind='bar', ax=ax, color='steelblue')
ax.set_title('Valor Médio de Venda por Marca')
ax.set_xlabel('Marca')
ax.set_ylabel('Valor Médio (R$)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
fig.savefig('graficos/valor_medio_marca.png', dpi=100)
plt.close()

# Gráfico 4: Valor vs Ano
fig, ax = plt.subplots(figsize=(10, 5))
sns.scatterplot(data=df, x='Ano', y='Valor_Venda', alpha=0.3, ax=ax)
ax.set_title('Valor de Venda vs Ano de Fabricação')
ax.set_xlabel('Ano')
ax.set_ylabel('Valor (R$)')
plt.tight_layout()
fig.savefig('graficos/valor_vs_ano.png', dpi=100)
plt.close()

# Gráfico 5: Valor vs Quilometragem
fig, ax = plt.subplots(figsize=(10, 5))
sns.scatterplot(data=df, x='Quilometragem', y='Valor_Venda', alpha=0.3, ax=ax)
ax.set_title('Valor de Venda vs Quilometragem')
ax.set_xlabel('Quilometragem (km)')
ax.set_ylabel('Valor (R$)')
plt.tight_layout()
fig.savefig('graficos/valor_vs_km.png', dpi=100)
plt.close()

# Gráfico 6: Boxplot por Câmbio
fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(data=df, x='Cambio', y='Valor_Venda', ax=ax)
ax.set_title('Valor de Venda por Tipo de Câmbio')
plt.tight_layout()
fig.savefig('graficos/valor_por_cambio.png', dpi=100)
plt.close()

# Gráfico 7: Boxplot por Combustível
fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(data=df, x='Combustivel', y='Valor_Venda', ax=ax)
ax.set_title('Valor de Venda por Tipo de Combustível')
plt.tight_layout()
fig.savefig('graficos/valor_por_combustivel.png', dpi=100)
plt.close()

print("\n✅ Gráficos salvos na pasta 'graficos/'")


# PREPARAÇÃO DOS DADOS

print("\n🔧 ETAPA 3: Preparação dos Dados")
print("-" * 60)

target = 'Valor_Venda'
cat_features = ['Marca', 'Modelo', 'Cor', 'Cambio', 'Combustivel']
num_features = ['Ano', 'Quilometragem', 'Portas']

X = df[cat_features + num_features]
y = df[target]

print(f"Features categóricas: {cat_features}")
print(f"Features numéricas: {num_features}")

# Pipeline com ColumnTransformer (OneHot + Scaler)
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), num_features),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_features),
    ]
)

# Split treino/teste
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Tamanho treino: {X_train.shape[0]}")
print(f"Tamanho teste: {X_test.shape[0]}")

# Salvar metadados
os.makedirs("modelo", exist_ok=True)

categorias = {}
for col in cat_features:
    categorias[col] = sorted(df[col].unique().tolist())
with open('modelo/categorias.json', 'w', encoding='utf-8') as f:
    json.dump(categorias, f, ensure_ascii=False, indent=2)

dataset_info = {
    'num_features': num_features,
    'cat_features': cat_features,
    'ano_min': int(df['Ano'].min()),
    'ano_max': int(df['Ano'].max()),
    'km_max': int(df['Quilometragem'].max()),
}
with open('modelo/dataset_info.json', 'w', encoding='utf-8') as f:
    json.dump(dataset_info, f, ensure_ascii=False, indent=2)

print("✅ Metadados salvos")


# 4. MODELAGEM - TREINAMENTO E COMPARAÇÃO

print("\n ETAPA 4: Treinamento e Comparação de Modelos")
print("-" * 60)

modelos_config = {
    "LinearRegression": LinearRegression(),
    "Ridge": Ridge(alpha=1.0),
    "Lasso": Lasso(alpha=1.0),
    "DecisionTree": DecisionTreeRegressor(max_depth=10, random_state=42),
    "RandomForest": RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1),
    "GradientBoosting": GradientBoostingRegressor(n_estimators=200, max_depth=5, learning_rate=0.1, random_state=42),
}

mlflow.set_tracking_uri("mlruns")
experiment_name = "predicao_preco_carros"
mlflow.set_experiment(experiment_name)

resultados = []
pipelines_treinados = {}

for nome, modelo in modelos_config.items():
    print(f"\n--- Treinando: {nome} ---")
    
    pipe = Pipeline([
        ('preprocessor', preprocessor),
        ('model', modelo),
    ])
    
    with mlflow.start_run(run_name=nome):
        pipe.fit(X_train, y_train)
        
        y_pred_train = pipe.predict(X_train)
        y_pred_test = pipe.predict(X_test)
        
        mae_train = mean_absolute_error(y_train, y_pred_train)
        rmse_train = np.sqrt(mean_squared_error(y_train, y_pred_train))
        r2_train = r2_score(y_train, y_pred_train)
        
        mae_test = mean_absolute_error(y_test, y_pred_test)
        rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
        r2_test = r2_score(y_test, y_pred_test)
        
        cv_scores = cross_val_score(pipe, X, y, cv=5, scoring='r2')
        cv_mean = cv_scores.mean()
        cv_std = cv_scores.std()
        
        mlflow.log_param("modelo", nome)
        mlflow.log_metric("mae_train", mae_train)
        mlflow.log_metric("rmse_train", rmse_train)
        mlflow.log_metric("r2_train", r2_train)
        mlflow.log_metric("mae_test", mae_test)
        mlflow.log_metric("rmse_test", rmse_test)
        mlflow.log_metric("r2_test", r2_test)
        mlflow.log_metric("cv_r2_mean", cv_mean)
        mlflow.log_metric("cv_r2_std", cv_std)
        
        mlflow.sklearn.log_model(pipe, "model")
        
        resultado = {
            'Modelo': nome,
            'MAE_Train': round(mae_train, 2),
            'RMSE_Train': round(rmse_train, 2),
            'R2_Train': round(r2_train, 4),
            'MAE_Test': round(mae_test, 2),
            'RMSE_Test': round(rmse_test, 2),
            'R2_Test': round(r2_test, 4),
            'CV_R2_Mean': round(cv_mean, 4),
            'CV_R2_Std': round(cv_std, 4),
        }
        resultados.append(resultado)
        pipelines_treinados[nome] = pipe
        
        print(f"  MAE Teste: {mae_test:.2f}")
        print(f"  RMSE Teste: {rmse_test:.2f}")
        print(f"  R² Teste: {r2_test:.4f}")
        print(f"  CV R² Médio: {cv_mean:.4f} (+/- {cv_std:.4f})")


# AVALIAÇÃO - COMPARAÇÃO DOS MODELOS

print("\n ETAPA 5: Avaliação e Comparação")
print("-" * 60)

df_resultados = pd.DataFrame(resultados)
df_resultados = df_resultados.sort_values('R2_Test', ascending=False)
print("\n--- Ranking dos Modelos (por R² Teste) ---")
print(df_resultados.to_string(index=False))

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

df_sorted = df_resultados.sort_values('R2_Test', ascending=True)
axes[0].barh(df_sorted['Modelo'], df_sorted['R2_Test'], color='steelblue')
axes[0].set_title('R² Score (Teste)')
axes[0].set_xlabel('R²')

df_sorted = df_resultados.sort_values('MAE_Test', ascending=False)
axes[1].barh(df_sorted['Modelo'], df_sorted['MAE_Test'], color='coral')
axes[1].set_title('MAE (Teste)')
axes[1].set_xlabel('MAE (R$)')

df_sorted = df_resultados.sort_values('RMSE_Test', ascending=False)
axes[2].barh(df_sorted['Modelo'], df_sorted['RMSE_Test'], color='green')
axes[2].set_title('RMSE (Teste)')
axes[2].set_xlabel('RMSE (R$)')

plt.suptitle('Comparação dos Modelos', fontsize=14, fontweight='bold')
plt.tight_layout()
fig.savefig('graficos/comparacao_modelos.png', dpi=100)
plt.close()

df_resultados.to_csv('modelo/resultados_modelos.csv', index=False)

# ESCOLHA E SALVAMENTO DO MELHOR MODELO

print("\n ETAPA 6: Salvando Melhor Modelo")
print("-" * 60)

melhor_modelo_nome = df_resultados.iloc[0]['Modelo']
melhor_pipeline = pipelines_treinados[melhor_modelo_nome]

print(f"Melhor modelo: {melhor_modelo_nome}")
print(f"  R² Teste: {df_resultados.iloc[0]['R2_Test']}")
print(f"  MAE Teste: {df_resultados.iloc[0]['MAE_Test']}")
print(f"  RMSE Teste: {df_resultados.iloc[0]['RMSE_Test']}")

joblib.dump(melhor_pipeline, 'modelo/melhor_modelo.pkl')

with open('modelo/melhor_modelo_info.json', 'w', encoding='utf-8') as f:
    json.dump({
        'nome': melhor_modelo_nome,
        'r2_test': float(df_resultados.iloc[0]['R2_Test']),
        'mae_test': float(df_resultados.iloc[0]['MAE_Test']),
        'rmse_test': float(df_resultados.iloc[0]['RMSE_Test']),
    }, f, ensure_ascii=False, indent=2)

print("\n Pipeline completo finalizado!")
print(f" Modelo '{melhor_modelo_nome}' salvo em 'modelo/melhor_modelo.pkl'")
print(" Experimentos registrados no MLflow em 'mlruns/'")
print("Gráficos salvos em 'graficos/'")
