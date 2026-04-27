import streamlit as st
import pandas as pd
from PIL import Image
import requests as request
#import joblib
import warnings
warnings.filterwarnings("ignore", category=UserWarning)


# Configuração da página
st.set_page_config(page_title="Docker - Desafio Final Previsão de Preço de Carros", page_icon="🚗", layout="centered")
#st.markdown('## Docker')

html_page_docker = """
     <div style="background-color:black;padding=60px">
         <p style='text-align:center;font-size:50px;font-weight:bold'>Docker</p>
     </div>
               """
st.markdown(html_page_docker, unsafe_allow_html=True)

html_page_title = """
     <div style="background-color:black;padding=60px">
         <p style='text-align:center;font-size:40px;font-weight:bold'>Previsão de Valor de Venda de Carros</p>
     </div>
               """
st.markdown(html_page_title, unsafe_allow_html=True)

st.sidebar.image(Image.open('imgs/aviso.png'), width='stretch')
st.sidebar.success("Este conteúdo é destinado apenas a fins educacionais.")
st.sidebar.success("Os dados exibidos são ilustrativos e podem não corresponder a situações reais.")

# Carregar o modelo (pipeline) treinado
#@st.cache_resource
#def load_pipeline(pipeline_path):
#    return joblib.load(pipeline_path)

#try:
#    pipeline = load_pipeline('modelo/lgbm_best_model_pipeline.pkl')
#except Exception as e:
#    st.error(f"Erro ao carregar o modelo: {e}")
#    st.stop()

# Carregar o dataset para recomendações
@st.cache_data
def load_data():
    return pd.read_csv('dados/dataset_carros_brasil.csv')

df_carros = load_data()

def exibir_recomendacoes(valor_estimado):
    st.divider()
    st.markdown('### Recomendação:')
    st.subheader("Veja opções reais na mesma faixa de preço")
    
    limite_inferior = valor_estimado * 0.90
    limite_superior = valor_estimado * 1.10
    
    carros_abaixo = df_carros[(df_carros['Valor_Venda'] >= limite_inferior) & (df_carros['Valor_Venda'] < valor_estimado)]
    carros_acima = df_carros[(df_carros['Valor_Venda'] >= valor_estimado) & (df_carros['Valor_Venda'] <= limite_superior)]
    
    recomendados_abaixo = carros_abaixo.sample(n=min(2, len(carros_abaixo))) if not carros_abaixo.empty else pd.DataFrame()
    recomendados_acima = carros_acima.sample(n=min(2, len(carros_acima))) if not carros_acima.empty else pd.DataFrame()
    
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
    
    #col1, col2 = st.columns(2)
    
    #with col1:
    #    marca = st.selectbox("Marca", options=['Nissan', 'Ford', 'Toyota', 'Renault', 'Fiat', 'Jeep', 'Honda', 'Volkswagen', 'Hyundai', 'Chevrolet'])
    #    modelo = st.selectbox("Modelo", options=['Frontier', 'Ranger', 'Hilux', 'Sandero', 'Duster', 'Kicks', 'Ka', 'Corolla', 'Mobi', 'Renegade', 'Compass', 'HR-V', 'T-Cross', 'Toro', 'HB20S', 'Yaris', 'EcoSport', 'Onix', 'Polo', 'Argo', 'Kwid', 'Virtus', 'Civic', 'Cronos', 'Gol', 'Versa', 'Creta', 'HB20', 'S10', 'Tracker', 'Onix Plus', 'Fit'])
    #    ano = st.number_input("Ano de Fabricação", min_value=1950, max_value=2026, value=2018, step=1)
    #    quilometragem = st.number_input("Quilometragem (km)", min_value=0, max_value=1000000, value=50000, step=1000)
    
    #with col2:
    #    cor = st.selectbox("Cor", options=['Cinza', 'Preto', 'Branco', 'Azul', 'Prata', 'Vermelho'])
    #    cambio = st.selectbox("Câmbio", options=['Manual', 'Automático'])
    #    combustivel = st.selectbox("Combustível", options=['Gasolina', 'Flex', 'Diesel'])
    #    portas = st.number_input("Número de Portas", min_value=2, max_value=5, value=4, step=1)
        
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
        # 1. Calcular a nova feature
        #idade_carro = 2026 - ano
        
        # 2. Criar DataFrame com as entradas
        dados_entrada = {
            'Marca': [marca],
       #    'Modelo': [modelo],
            'Ano': [ano],
            'Quilometragem': [quilometragem],
        #    'Cor': [cor],
        #    'Cambio': [cambio],
        #    'Combustivel': [combustivel],
        #    'Portas': [portas],
        #    'idade_carro': [idade_carro]
        }
        
        # Criar DataFrame com as entradas
        df = pd.DataFrame(dados_entrada)
        
        try:
            # Enviar os dados crus para a API
            response = request.post("http://api:8000/forecast", json=df.to_dict(orient="records"))
            response.raise_for_status()  # Levantar erro se a requisição falhar
            valor_estimado = response.json()["forecast"][0]
            
            st.success("✅ Previsão realizada com sucesso!")
            st.metric(
                label="Valor de Venda Estimado", 
                value=f"R$ {valor_estimado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )
            exibir_recomendacoes(valor_estimado)
            
        except Exception as e:
            st.error(f"Erro ao fazer a previsão: {e}")
                
    else:
        st.warning("⚠️ Por favor, preencha todos os campos de texto como Marca, Modelo e Cor.")