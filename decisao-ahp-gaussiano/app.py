import streamlit as st
import pandas as pd
from engine import AHPGaussianoEngine  # Importamos a lógica que criamos

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Decision Intelligence Pro",
    page_icon="🎯",
    layout="wide"
)

# Instanciando o motor de cálculo
engine = AHPGaussianoEngine()

# Estilização para um visual de "Produto"
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; font-weight: bold; }
    .success-text { color: #28a745; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Decision Intelligence Pro")
st.markdown("---")

# --- PASSO 1: CONFIGURAÇÃO DE CRITÉRIOS E ALTERNATIVAS ---
with st.sidebar:
    st.header("⚙️ Configurações")
    criterios_raw = st.text_input("Critérios (separados por vírgula)", "Preço, Qualidade, Prazo, Suporte")
    alternativas_raw = st.text_input("Alternativas (separadas por vírgula)", "Fornecedor A, Fornecedor B, Fornecedor C")
    
    lista_criterios = [c.strip() for c in criterios_raw.split(",")]
    lista_alternativas = [a.strip() for a in alternativas_raw.split(",")]

    st.markdown("---")
    st.write("**Defina a natureza de cada critério:**")
    tipo_criterio = {}
    for crit in lista_criterios:
        tipo_criterio[crit] = st.selectbox(
            f"{crit}", 
            ["MAX", "MIN"], 
            help="MAX: Quanto maior melhor. MIN: Quanto menor melhor (ex: Preço).",
            key=f"tipo_{crit}"
        )

# --- PASSO 2: COLETA DE DADOS (FORMULÁRIO DINÂMICO) ---
st.header("1️⃣ Inserir Avaliações")
st.info("Preencha os valores para cada alternativa em relação aos critérios definidos.")

dados_expert = []

with st.form("form_decisao"):
    # Criamos abas para organizar o preenchimento por alternativa
    tabs = st.tabs(lista_alternativas)
    
    for i, alt in enumerate(lista_alternativas):
        with tabs[i]:
            st.subheader(f"Avaliação de: {alt}")
            cols = st.columns(len(lista_criterios))
            valores_alt = {"Alternativas": alt}
            for j, crit in enumerate(lista_criterios):
                val = cols[j].number_input(
                    f"{crit}", 
                    min_value=0.0, 
                    value=10.0 if tipo_criterio[crit] == "MAX" else 5.0,
                    step=0.1, 
                    key=f"{alt}_{crit}"
                )
                valores_alt[crit] = val
            dados_expert.append(valores_alt)
    
    st.markdown("###")
    submit = st.form_submit_button("🚀 Calcular Melhor Decisão")

# --- PASSO 3: PROCESSAMENTO E RESULTADOS ---
if submit:
    # 1. Criar DataFrame com os dados inseridos
    df_decisao = pd.DataFrame(dados_expert).set_index("Alternativas")
    
    # 2. Chamar a Engine (Lógica de Negócio)
    try:
        ranking, pesos = engine.resolver(df_decisao, tipo_criterio)
        
        # --- EXIBIÇÃO ---
        st.markdown("---")
        st.header("🎯 Resultado da Análise")
        
        col_rank, col_pesos = st.columns([1, 1])
        
        with col_rank:
            st.subheader("🏆 Ranking Final")
            # Exibição estilizada da tabela
            st.dataframe(
                ranking.to_frame("Pontuação").style.background_gradient(cmap='Blues'),
                use_container_width=True
            )
            
            vencedor = ranking.index[0]
            st.balloons()
            st.markdown(f"### A melhor escolha é: <span class='success-text'>{vencedor}</span>", unsafe_allow_html=True)

        with col_pesos:
            st.subheader("📊 Importância Automática (Pesos)")
            # Gráfico de barras dos pesos calculados pelo Fator Gaussiano
            st.bar_chart(pesos)
            st.caption("Pesos calculados automaticamente com base na variabilidade dos dados (Método Gaussiano).")

        # --- DOWNLOAD DOS RESULTADOS ---
        st.markdown("###")
        csv = df_decisao.to_csv().encode('utf-8')
        st.download_button(
            label="📥 Baixar Dados da Decisão (CSV)",
            data=csv,
            file_name='analise_decisao.csv',
            mime='text/csv',
        )
        
    except Exception as e:
        st.error(f"Erro ao processar cálculo: {e}")
        st.warning("Certifique-se de que os valores inseridos não resultam em soma zero nas colunas.")

else:
    st.write("---")
    st.caption("Aguardando preenchimento do formulário para gerar o ranking.")