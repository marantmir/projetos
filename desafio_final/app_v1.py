import streamlit as st
import pandas as pd
import joblib
from PIL import Image
#import base64


# Configuração da página
st.set_page_config(page_title="Previsão de Preço de Carros", page_icon="🚗", layout="centered")

html_page_cloud = """
     <div style="background-color:black;padding=60px">
         <p style='text-align:center;font-size:50px;font-weight:bold'>Streamlit.io / Cloud</p>
     </div>
               """               
st.markdown(html_page_cloud, unsafe_allow_html=True)

html_page_title = """
     <div style="background-color:black;padding=60px">
         <p style='text-align:center;font-size:40px;font-weight:bold'>Previsão de Valor de Venda de Carros</p>
     </div>
               """               
st.markdown(html_page_title, unsafe_allow_html=True)

st.sidebar.image(Image.open('imgs/aviso.png'), width='stretch')
st.sidebar.success("Este conteúdo é destinado apenas a fins educacionais.")
st.sidebar.success("Os dados exibidos são ilustrativos e podem não corresponder a situações reais.")

# Carregar o modelo (com cache para não recarregar toda vez)
@st.cache_resource
def load_model(model_path):
    # Substitua pelo nome correto do seu arquivo pickle, se for diferente
    return joblib.load(model_path)

try:
    model = load_model('modelo/lasso_best_full_model_pipeline.pkl')
    model_ridge = load_model('modelo/Ridge_best_full_model_pipeline_3.pkl')
    model_gb    = load_model('modelo/GradientBoosting_best_full_model_pipeline_3.pkl')
    model_xgb   = load_model('modelo/XGBoost_best_full_model_pipeline_3.pkl')
    model_lgbm    = load_model('modelo/LightGBM_best_full_model_pipeline_3.pkl')
    
except Exception as e:
    st.error(f"Erro ao carregar o modelo: {e}")
    st.stop()

# Carregar o dataset para recomendações
@st.cache_data
def load_data():
    return pd.read_csv('dados/dataset_carros_brasil.csv')

df_carros = load_data()

def exibir_recomendacoes(valor_estimado):
    st.divider()
    st.markdown('### Recomendação:')
    st.subheader("Veja opções na mesma faixa de preço (10%) ")
    
    limite_inferior = valor_estimado * 0.90
    limite_superior = valor_estimado * 1.10
    
    # Buscar na base de dados carros dentro dos valores
    carros_abaixo = df_carros[(df_carros['Valor_Venda'] >= limite_inferior) & (df_carros['Valor_Venda'] < valor_estimado)]
    carros_acima = df_carros[(df_carros['Valor_Venda'] >= valor_estimado) & (df_carros['Valor_Venda'] <= limite_superior)]
    
    # Sortear até 2 carros de cada faixa
    recomendados_abaixo = carros_abaixo.sample(n=min(2, len(carros_abaixo))) if not carros_abaixo.empty else pd.DataFrame()
    recomendados_acima = carros_acima.sample(n=min(2, len(carros_acima))) if not carros_acima.empty else pd.DataFrame()
    
    # Juntar as recomendações em uma única tabela
    df_recomendacoes = pd.concat([recomendados_abaixo, recomendados_acima])
    
    if not df_recomendacoes.empty:
        colunas_mostrar = ['Marca', 'Modelo', 'Ano', 'Cor', 'Combustivel', 'Valor_Venda']
        if all(col in df_recomendacoes.columns for col in colunas_mostrar):
            df_exibicao = df_recomendacoes[colunas_mostrar].copy()
            df_exibicao = df_exibicao.sort_values(by='Valor_Venda')
            df_exibicao['Valor_Venda'] = df_exibicao['Valor_Venda'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
        else:
            st.dataframe(df_recomendacoes, use_container_width=True, hide_index=True)
    else:
        st.info("Não encontramos carros semelhantes a esse valor nesse exato momento na base de dados.")

# Criar formulário para receber os dados
with st.form("form_previsao"):
    st.subheader("Dados do Veículo")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        marca = st.selectbox("Marca", options=['Nissan', 'Ford', 'Toyota', 'Renault', 'Fiat', 'Jeep', 'Honda', 'Volkswagen', 'Hyundai', 'Chevrolet'])
        #modelo = st.selectbox("Modelo", options=['Frontier', 'Ranger', 'Hilux', 'Sandero', 'Duster', 'Kicks', 'Ka', 'Corolla', 'Mobi', 'Renegade', 'Compass', 'HR-V', 'T-Cross', 'Toro', 'HB20S', 'Yaris', 'EcoSport', 'Onix', 'Polo', 'Argo', 'Kwid', 'Virtus', 'Civic', 'Cronos', 'Gol', 'Versa', 'Creta', 'HB20', 'S10', 'Tracker', 'Onix Plus', 'Fit'])
        #ano = st.number_input("Ano de Fabricação", min_value=1950, max_value=2026, value=2018, step=1)
        #quilometragem = st.number_input("Quilometragem (km)", min_value=0, max_value=1000000, value=50000, step=1000)
    
    with col2:
        quilometragem = st.number_input("Quilometragem (km)", min_value=0, max_value=1000000, value=50000, step=1000)
        #cor = st.selectbox("Cor", options=['Cinza', 'Preto', 'Branco', 'Azul', 'Prata', 'Vermelho'])
        #cambio = st.selectbox("Câmbio", options=['Manual', 'Automático'])
        #combustivel = st.selectbox("Combustível", options=['Gasolina', 'Flex', 'Diesel'])
        #portas = st.number_input("Número de Portas", min_value=2, max_value=5, value=4, step=1)
        
    with col3:
        ano = st.number_input("Ano de Fabricação", min_value=1950, max_value=2026, value=2018, step=1)
        #cor = st.selectbox("Cor", options=['Cinza', 'Preto', 'Branco', 'Azul', 'Prata', 'Vermelho'])
        #cambio = st.selectbox("Câmbio", options=['Manual', 'Automático'])
        #combustivel = st.selectbox("Combustível", options=['Gasolina', 'Flex', 'Diesel'])
        #portas = st.number_input("Número de Portas", min_value=2, max_value=5, value=4, step=1)    

    submit_button = st.form_submit_button(label="🔍 Prever Valor de Venda")
    
    html_page_aviso = """
     <div style="background-color:black;padding=60px">
         <p style='text-align:center;font-size:20px;font-weight:bold'>Dados Ficticios</p>
     </div>
               """               
st.markdown(html_page_aviso, unsafe_allow_html=True)

if submit_button:
    if marca and quilometragem and ano:
        # 1. Tratar os dados
        # A nova feature foi criada a partir de 2026 menos o Ano
        idade_carro = 2026 - ano
        
        # 2. Criar DataFrame com as entradas
        dados_entrada = {
            'Marca': [marca],
            #'Modelo': [modelo],
            'Ano': [ano],
            'Quilometragem': [quilometragem],
            #'Cor': [cor],
            #'Cambio': [cambio],
            #'Combustivel': [combustivel],
            #'Portas': [portas],
            #'idade_carro': [idade_carro]
        }
        
        df_entrada = pd.DataFrame(dados_entrada)
        
        # 3. Fazer a previsão
        try:
            # Tenta prever assumindo que o modelo contém o pipeline com o OneHotEncoder
            valor_estimado = model.predict(df_entrada)[0]
            valor_estimado_ridge = model_ridge.predict(df_entrada)[0]
            valor_estimado_gb = model_gb.predict(df_entrada)[0]
            valor_estimado_xgb = model_xgb.predict(df_entrada)[0]
            valor_estimado_lgbm = model_lgbm.predict(df_entrada)[0]
           
            
            st.success("✅ Previsão realizada com sucesso!")
            #st.metric(label="Valor de Venda Estimado", value=f"R$ {valor_estimado:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            
            lasso = f"{valor_estimado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            ridge = f"{valor_estimado_ridge:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            xgb = f"{valor_estimado_xgb:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            gb = f"{valor_estimado_gb:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            lgbm = f"{valor_estimado_lgbm:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
           
           
            data = {
                    'Modelo': ['Lasso', 'Ridge', 'XGB', 'GB', 'LightGBM'],
                    'Valor Estimado (R$)': [lasso, ridge, xgb, gb, lgbm ]
                     }

            df = pd.DataFrame(data)
            df_melt = df.set_index('Modelo').T
            st.dataframe(df_melt)

            
            
            exibir_recomendacoes(valor_estimado)
            
        except Exception as e:
            # Log de fallback caso o Pickle envolva apenas o estimador e não o Pipeline inteiro.
            # Se o Pickle tiver apenas o estimador treinado com OneHot manual, precisará das colunas exatas de treino.
            try:
                # Fallback usando dummies e alinhando com a estrutura de treino do modelo
                if hasattr(model, "feature_names_in_"):
                    df_entrada_encoded = pd.get_dummies(df_entrada)
                    # Adiciona colunas faltantes com valor 0 e alinha as colunas
                    df_entrada_encoded = df_entrada_encoded.reindex(columns=model.feature_names_in_, fill_value=0)
                    
                    previsao = model.predict(df_entrada_encoded)
                    valor_estimado = previsao[0]
                    
                    st.success("✅ Previsão realizada com sucesso!")
                    st.metric(label="Valor de Venda Estimado", value=f"R$ {valor_estimado:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    exibir_recomendacoes(valor_estimado)
                else:
                    st.error(f"Erro inesperado no modelo com codificação manual: {e}")
            except Exception as e_fallback:
                st.error(f"Erro ao realizar a previsão: {e_fallback}. Certifique-se de que o input bate com os dados de treinamento.")
                
    else:
        st.warning("⚠️ Por favor, preencha todos os campos de texto como Marca, Modelo e Cor.")
