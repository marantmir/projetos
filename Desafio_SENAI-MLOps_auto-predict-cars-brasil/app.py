import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import os
import base64
import io
def _load_logo_src():
    """Carrega logo de logo_b64.txt (texto base64 puro, sem LFS)."""
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_b64.txt")
    try:
        with open(p, "r", encoding="utf-8") as f:
            b64 = f.read().strip()
        if b64 and len(b64) > 200:          # evita ponteiro LFS (~40 chars)
            return f"data:image/png;base64,{b64}"
    except Exception:
        pass
    return ""

_LOGO_SRC = _load_logo_src()




st.set_page_config(
    page_title="AutoPredict BR — Precificação de Veículos",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Barlow+Condensed:wght@500;700;900&display=swap');

/* ── BASE ──────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #0c0f14;
    min-height: 100vh;
}

/* ── SIDEBAR ───────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: #080b10 !important;
    border-right: 1px solid #1e2530;
}
[data-testid="stSidebar"] * {
    color: #8a9bb0 !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #dce6f0 !important;
}

/* ── HEADER BANNER ─────────────────────────────────────────── */
.site-header {
    background: linear-gradient(180deg, #0a0d13 0%, #111620 100%);
    border-bottom: 3px solid #16a34a;
    padding: 36px 48px 32px;
    margin-bottom: 0;
}
.site-header-eyebrow {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    color: #16a34a;
    margin-bottom: 10px;
}
.site-header-title {
    font-family: 'Barlow Condensed', 'Inter', sans-serif;
    font-size: 3.2rem;
    font-weight: 900;
    text-transform: uppercase;
    color: #f0f4f8;
    letter-spacing: 0.03em;
    line-height: 1;
    margin-bottom: 6px;
}
.site-header-subtitle {
    font-size: 1rem;
    color: #8aa4b8;
    font-weight: 400;
    letter-spacing: 0.01em;
}

/* ── AVISO EDUCACIONAL ─────────────────────────────────────── */
.edu-notice {
    background: #0f1a10;
    border-left: 3px solid #16a34a;
    padding: 10px 20px;
    font-size: 0.82rem;
    color: #7aaa80;
    letter-spacing: 0.01em;
}
.edu-notice strong {
    color: #5aba65;
}

/* ── SECTION STRIPE ────────────────────────────────────────── */
.section-stripe {
    background: #111620;
    border-top: 1px solid #1a2030;
    border-bottom: 1px solid #1a2030;
    padding: 12px 0 10px;
    margin-bottom: 24px;
}
.section-label {
    font-family: 'Barlow Condensed', 'Inter', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #dce6f0;
}
.section-label-green {
    color: #16a34a;
}

/* ── METRIC CARDS ──────────────────────────────────────────── */
.stat-card {
    background: #111620;
    border: 1px solid #1e2a38;
    border-top: 3px solid #16a34a;
    padding: 22px 20px 18px;
    text-align: left;
}
.stat-card.accent-blue { border-top-color: #2563eb; }
.stat-card.accent-amber { border-top-color: #d97706; }
.stat-card.accent-rose { border-top-color: #e11d48; }

.stat-label {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: #6a8a9a;
    margin-bottom: 8px;
}
.stat-value {
    font-size: 1.7rem;
    font-weight: 800;
    color: #e8f0f8;
    line-height: 1;
    font-family: 'Barlow Condensed', sans-serif;
}
.stat-value-green { color: #22c55e; }
.stat-value-blue  { color: #60a5fa; }
.stat-value-amber { color: #fbbf24; }
.stat-value-rose  { color: #fb7185; }

/* ── FORM CARD ─────────────────────────────────────────────── */
.form-panel {
    background: #111620;
    border: 1px solid #1e2a38;
    padding: 28px;
}

/* ── RESULT PANEL ──────────────────────────────────────────── */
.result-panel {
    background: #0a1a0f;
    border: 1px solid #1a3020;
    border-top: 4px solid #16a34a;
    padding: 36px 32px;
    text-align: center;
    height: 100%;
}
.result-eyebrow {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: #4a9058;
    margin-bottom: 12px;
}
.result-price {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 3.8rem;
    font-weight: 900;
    color: #22c55e;
    line-height: 1;
    letter-spacing: 0.01em;
}
.result-range {
    font-size: 0.82rem;
    color: #4a8a58;
    margin-top: 10px;
}
.result-range span {
    color: #6aaa78;
    font-weight: 600;
}
.result-specs {
    margin-top: 24px;
    border-top: 1px solid #1a3020;
    padding-top: 18px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
}
.result-spec-tag {
    background: #0c1a10;
    border: 1px solid #1e3525;
    color: #6a9070;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 4px 12px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.result-spec-tag strong {
    color: #98c8a8;
}
.result-empty {
    border: 1px dashed #1a2530;
    padding: 60px 24px;
    text-align: center;
    color: #5a7888;
}
.result-empty-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #6a8a9a;
    margin-top: 8px;
}

/* ── CHART PANEL ───────────────────────────────────────────── */
.chart-panel {
    background: #111620;
    border: 1px solid #1e2a38;
    margin-bottom: 20px;
    overflow: hidden;
}
.chart-panel-header {
    background: #0c1018;
    border-bottom: 1px solid #1a2030;
    padding: 10px 16px;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #6a8a9a;
}

/* ── MODEL CARD ────────────────────────────────────────────── */
.model-info-card {
    background: #111620;
    border: 1px solid #1e2a38;
    border-left: 3px solid #2563eb;
    padding: 16px 20px;
    margin-bottom: 10px;
}
.model-info-card.highlight {
    border-left-color: #16a34a;
    background: #0a1410;
}
.model-info-name {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #dce6f0;
    margin-bottom: 2px;
}
.model-info-desc {
    font-size: 0.78rem;
    color: #6a8090;
}
.model-info-score {
    font-size: 0.85rem;
    font-weight: 700;
    color: #22c55e;
    font-family: 'Barlow Condensed', sans-serif;
    float: right;
    margin-top: -22px;
}

/* ── SIDEBAR — PIPELINE ────────────────────────────────────── */
.pipe-step {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid #0f1620;
}
.pipe-step:last-child { border-bottom: none; }
.pipe-num {
    width: 26px; height: 26px; min-width: 26px;
    background: #16a34a;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.72rem; font-weight: 800;
    color: white;
    flex-shrink: 0;
}
.pipe-num.done { background: #1e3530; color: #3a7050; }
.pipe-title {
    font-size: 0.82rem;
    font-weight: 600;
    color: #8a9bb0 !important;
    line-height: 1.3;
}
.pipe-desc {
    font-size: 0.7rem;
    color: #5a7080 !important;
    margin-top: 1px;
}

/* ── SIDEBAR — CHAMP ───────────────────────────────────────── */
.champ-block {
    background: #0a1408;
    border: 1px solid #1a3020;
    border-top: 3px solid #16a34a;
    padding: 18px;
    text-align: center;
    margin: 8px 0;
}
.champ-eyebrow {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: #5a8860;
    margin-bottom: 6px;
}
.champ-name {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2rem;
    font-weight: 900;
    text-transform: uppercase;
    color: #22c55e;
    letter-spacing: 0.04em;
    line-height: 1;
}
.champ-r2 {
    font-size: 0.8rem;
    font-weight: 600;
    color: #5aaa68;
    margin-top: 4px;
    font-family: 'Barlow Condensed', sans-serif;
    letter-spacing: 0.06em;
}
.sidebar-stat {
    background: #0c1018;
    border: 1px solid #1a2030;
    padding: 10px 14px;
    margin-bottom: 8px;
}
.sidebar-stat-label {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #5a7888;
    margin-bottom: 2px;
}
.sidebar-stat-value {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: #60a5fa;
}

/* ── TABS ──────────────────────────────────────────────────── */
[data-testid="stTabs"] button {
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    color: #6a8a9a !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    padding: 10px 22px !important;
    border-radius: 0 !important;
    transition: color 0.2s ease !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #22c55e !important;
    background: #0a1410 !important;
    border-bottom: 2px solid #16a34a !important;
}
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid #1a2030 !important;
    gap: 4px;
    margin-bottom: 24px;
}

/* ── INPUTS ────────────────────────────────────────────────── */
.stSelectbox > label, .stNumberInput > label,
.stSlider > label, .stRadio > label {
    color: #6a8a9a !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
[data-testid="stNumberInput"] input {
    background: #0c1018 !important;
    border: 1px solid #1e2a38 !important;
    border-radius: 0 !important;
    color: #c8d8e8 !important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within,
[data-testid="stNumberInput"] input:focus {
    border-color: #16a34a !important;
    box-shadow: none !important;
}

/* ── BOTÃO ─────────────────────────────────────────────────── */
[data-testid="stButton"] > button[kind="primary"] {
    background: #16a34a !important;
    border: none !important;
    border-radius: 0 !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    padding: 14px 32px !important;
    color: white !important;
    transition: background-color 0.2s ease !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #15803d !important;
}

/* ── DATAFRAME ─────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid #1e2a38 !important;
    border-radius: 0 !important;
    overflow: hidden;
}

/* ── STREAMLIT METRICS ─────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #111620 !important;
    border: 1px solid #1e2a38 !important;
    border-top: 2px solid #2563eb !important;
    border-radius: 0 !important;
    padding: 16px !important;
}
[data-testid="stMetric"] label {
    color: #6a8a9a !important;
    font-size: 0.68rem !important;
    text-transform: uppercase !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
}
[data-testid="stMetricValue"] {
    color: #e8f0f8 !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 1.6rem !important;
    font-weight: 800 !important;
}

/* ── DIVIDER ───────────────────────────────────────────────── */
hr {
    border-color: #1a2030 !important;
    margin: 24px 0 !important;
}

/* ── FOOTER ────────────────────────────────────────────────── */
.site-footer {
    background: #080b10;
    border-top: 1px solid #1a2030;
    padding: 20px 0 12px;
    text-align: center;
    font-size: 0.75rem;
    color: #9ab8c8;
    margin-top: 40px;
    letter-spacing: 0.04em;
}
.site-footer strong {
    color: #c0d8e8;
}

/* ── SCROLLBAR ─────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #080b10; }
::-webkit-scrollbar-thumb { background: #1e2a38; }
::-webkit-scrollbar-thumb:hover { background: #16a34a; }

</style>
""", unsafe_allow_html=True)


def _load_b64_file(path):
    """Lê arquivo _b64.txt e retorna bytes decodificados (bypass LFS)."""
    with open(path, 'r', encoding='utf-8') as f:
        return base64.b64decode(f.read().strip())

@st.cache_resource
def carregar_modelo():
    pkl_bytes = _load_b64_file('modelo/melhor_modelo_b64.txt')
    pipeline = joblib.load(io.BytesIO(pkl_bytes))
    with open('modelo/categorias.json', 'r', encoding='utf-8') as f:
        categorias = json.load(f)
    with open('modelo/melhor_modelo_info.json', 'r', encoding='utf-8') as f:
        info = json.load(f)
    with open('modelo/dataset_info.json', 'r', encoding='utf-8') as f:
        dataset_info = json.load(f)
    return pipeline, categorias, info, dataset_info

@st.cache_data
def carregar_dados():
    return pd.read_csv('dataset_limpo.csv')

try:
    pipeline, categorias, modelo_info, dataset_info = carregar_modelo()
    df_ref = carregar_dados()
except Exception as e:
    st.error(f"Erro ao carregar artefatos: {e}")
    st.stop()


with st.sidebar:
    st.markdown(f"""
    <div style="padding: 12px 0 20px;">
        <img src="{_LOGO_SRC}" style="height:90px; display:block; margin-bottom:6px;">
        <div style="font-size:0.65rem; color:#1e3028; text-transform:uppercase;
             letter-spacing:0.16em; font-weight:700;">
            Machine Learning · 2026/1
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.65rem; font-weight:700; text-transform:uppercase;
         letter-spacing:0.14em; color:#2a3a4a; margin-bottom:8px;">
    Pipeline CRISP-DM
    </div>
    """, unsafe_allow_html=True)

    steps = [
        ("Entendimento do Negócio", "Precificação de veículos usados", True),
        ("Análise Exploratória",    "EDA + visualizações",              True),
        ("Preparação dos Dados",    "OneHot · Scaler · Split",          True),
        ("Modelagem",               "6 algoritmos treinados",            True),
        ("Avaliação · MLflow",      "MAE · RMSE · R² · CV",             True),
        ("Deploy",                  "Esta aplicação Streamlit",          True),
    ]
    pipe_html = ""
    for i, (titulo, desc, done) in enumerate(steps):
        num_class = "pipe-num done" if done else "pipe-num"
        pipe_html += f"""
        <div class="pipe-step">
          <div class="{num_class}">{i+1}</div>
          <div>
            <div class="pipe-title">{titulo}</div>
            <div class="pipe-desc">{desc}</div>
          </div>
        </div>"""
    st.markdown(pipe_html, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="champ-block">
        <div class="champ-eyebrow">Modelo Selecionado</div>
        <div class="champ-name">{modelo_info['nome']}</div>
        <div class="champ-r2">R² = {modelo_info['r2_test']:.4f}</div>
    </div>
    <div class="sidebar-stat">
        <div class="sidebar-stat-label">MAE — Erro Médio</div>
        <div class="sidebar-stat-value">R$ {modelo_info['mae_test']:,.0f}</div>
    </div>
    <div class="sidebar-stat">
        <div class="sidebar-stat-label">RMSE — Raiz do Erro</div>
        <div class="sidebar-stat-value">R$ {modelo_info['rmse_test']:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
st.markdown(f"""
<div class="site-header">
    <div class="site-header-eyebrow">Aprendizado de Maquina · CRISP-DM · MLflow · Deploy</div>
    <img src="{_LOGO_SRC}" style="height:130px; display:block; margin-bottom:8px;">
    <div class="site-header-subtitle">
        Inteligencia Artificial para Precificacao de Veiculos — 9.588 registros · 6 modelos comparados
    </div>
</div>
<div class="edu-notice">
    <strong>Conteudo educacional.</strong>
    Os dados sao ilustrativos e destinados exclusivamente para fins academicos — Atividade Final UC 2026/1.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


tab1, tab2, tab3 = st.tabs([
    "PREVISAO DE PRECO",
    "ANALISE EXPLORATORIA",
    "COMPARACAO DE MODELOS"
])

with tab1:
    st.markdown("""
    <div class="section-stripe">
        <span class="section-label">
            <span class="section-label-green">01</span> — Configure o Veiculo
        </span>
    </div>
    """, unsafe_allow_html=True)

    col_form, col_gap, col_result = st.columns([5, 0.3, 4])

    if 'resultado' not in st.session_state:
        st.session_state.resultado = None

    with col_form:
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            marca = st.selectbox("Marca", options=categorias['Marca'])
        with r1c2:
            modelos_marca = sorted(df_ref[df_ref['Marca'] == marca]['Modelo'].unique().tolist())
            modelo_carro = st.selectbox("Modelo", options=modelos_marca)

        r2c1, r2c2 = st.columns(2)
        with r2c1:
            ano = st.slider("Ano de Fabricacao",
                            min_value=dataset_info['ano_min'],
                            max_value=dataset_info['ano_max'],
                            value=2018)
        with r2c2:
            quilometragem = st.number_input("Quilometragem (km)",
                                            min_value=0,
                                            max_value=dataset_info['km_max'],
                                            value=50000, step=1000)

        r3c1, r3c2, r3c3 = st.columns(3)
        with r3c1:
            cambio = st.selectbox("Cambio", options=categorias['Cambio'])
        with r3c2:
            combustivel = st.selectbox("Combustivel", options=categorias['Combustivel'])
        with r3c3:
            cor = st.selectbox("Cor", options=categorias['Cor'])

        portas = st.radio("Portas", options=[2, 4], horizontal=True)

        prever = st.button("Calcular Valor Estimado", type="primary", use_container_width=True)

    if prever:
        entrada = pd.DataFrame([{
            'Marca': marca,
            'Modelo': modelo_carro,
            'Cor': cor,
            'Cambio': cambio,
            'Combustivel': combustivel,
            'Ano': ano,
            'Quilometragem': quilometragem,
            'Portas': portas,
        }])
        valor_previsto = max(pipeline.predict(entrada)[0], 0)
        margem = modelo_info['mae_test']
        st.session_state.resultado = {
            'valor': valor_previsto,
            'margem': margem,
            'faixa_min': max(valor_previsto - margem, 0),
            'faixa_max': valor_previsto + margem,
            'marca': marca,
            'modelo_carro': modelo_carro,
            'ano': ano,
            'quilometragem': quilometragem,
            'cambio': cambio,
            'combustivel': combustivel,
            'cor': cor,
            'portas': portas,
        }

    with col_result:
        res = st.session_state.resultado
        if res:
            st.markdown(f"""
            <div class="result-panel">
                <div class="result-eyebrow">Valor Estimado de Mercado</div>
                <div class="result-price">R$ {res['valor']:,.0f}</div>
                <div class="result-range">
                    Faixa provavel &nbsp;·&nbsp;
                    <span>R$ {res['faixa_min']:,.0f}</span> — <span>R$ {res['faixa_max']:,.0f}</span>
                </div>
                <div class="result-specs">
                    <div class="result-spec-tag">{res['marca']} <strong>{res['modelo_carro']}</strong></div>
                    <div class="result-spec-tag">Ano <strong>{res['ano']}</strong></div>
                    <div class="result-spec-tag"><strong>{res['quilometragem']:,}</strong> km</div>
                    <div class="result-spec-tag"><strong>{res['cambio']}</strong></div>
                    <div class="result-spec-tag"><strong>{res['combustivel']}</strong></div>
                    <div class="result-spec-tag"><strong>{res['cor']}</strong> · <strong>{res['portas']}p</strong></div>
                </div>
            </div>
            <br>
            <div style="display:flex; gap:12px;">
                <div class="stat-card" style="border-top-color:#16a34a; flex:1;">
                    <div class="stat-label">Precisao R2</div>
                    <div class="stat-value stat-value-green">{modelo_info['r2_test']:.4f}</div>
                </div>
                <div class="stat-card accent-blue" style="flex:1;">
                    <div class="stat-label">Erro Medio</div>
                    <div class="stat-value stat-value-blue">+/- R$ {res['margem']:,.0f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="result-empty">
                <div style="width:40px; height:3px; background:#1a2a38; margin:0 auto 16px;"></div>
                <div class="result-empty-title">Configure o veiculo ao lado<br>e calcule o valor estimado</div>
            </div>
            """, unsafe_allow_html=True)


with tab2:
    st.markdown("""
    <div class="section-stripe">
        <span class="section-label">
            <span class="section-label-green">01</span> — Visao Geral do Dataset
        </span>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Total de Registros</div>
        <div class="stat-value">{len(df_ref):,}</div>
    </div>""", unsafe_allow_html=True)
    m2.markdown(f"""
    <div class="stat-card accent-blue">
        <div class="stat-label">Marcas</div>
        <div class="stat-value stat-value-blue">{df_ref['Marca'].nunique()}</div>
    </div>""", unsafe_allow_html=True)
    m3.markdown(f"""
    <div class="stat-card" style="border-top-color:#16a34a;">
        <div class="stat-label">Preco Medio</div>
        <div class="stat-value stat-value-green">R$ {df_ref['Valor_Venda'].mean():,.0f}</div>
    </div>""", unsafe_allow_html=True)
    m4.markdown(f"""
    <div class="stat-card accent-amber">
        <div class="stat-label">Preco Mediano</div>
        <div class="stat-value stat-value-amber">R$ {df_ref['Valor_Venda'].median():,.0f}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-stripe">
        <span class="section-label">
            <span class="section-label-green">02</span> — Graficos Exploratórios
        </span>
    </div>
    """, unsafe_allow_html=True)

    graficos = [
        ("Distribuicao do Valor de Venda",    "graficos/distribuicao_valor_venda.png"),
        ("Matriz de Correlacao",              "graficos/correlacao.png"),
        ("Valor Medio por Marca",             "graficos/valor_medio_marca.png"),
        ("Valor vs Ano de Fabricacao",        "graficos/valor_vs_ano.png"),
        ("Valor vs Quilometragem",            "graficos/valor_vs_km.png"),
        ("Valor por Tipo de Cambio",          "graficos/valor_por_cambio.png"),
        ("Valor por Tipo de Combustivel",     "graficos/valor_por_combustivel.png"),
    ]

    for i in range(0, len(graficos), 2):
        c1, c2 = st.columns(2)
        for col, (titulo, caminho) in zip([c1, c2], graficos[i:i+2]):
            if os.path.exists(caminho):
                with col:
                    st.markdown(
                        f'<div class="chart-panel"><div class="chart-panel-header">{titulo}</div>',
                        unsafe_allow_html=True)
                    st.image(caminho, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-stripe">
        <span class="section-label">
            <span class="section-label-green">03</span> — Amostra dos Dados
        </span>
    </div>
    """, unsafe_allow_html=True)
    st.dataframe(df_ref.head(20), use_container_width=True, height=360)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-stripe">
        <span class="section-label">
            <span class="section-label-green">04</span> — Estatisticas Descritivas
        </span>
    </div>
    """, unsafe_allow_html=True)
    st.dataframe(df_ref.describe().T, use_container_width=True)

with tab3:
    st.markdown("""
    <div class="section-stripe">
        <span class="section-label">
            <span class="section-label-green">01</span> — Ranking dos Modelos
        </span>
    </div>
    """, unsafe_allow_html=True)

    if os.path.exists('modelo/resultados_modelos.csv'):
        df_res = pd.read_csv('modelo/resultados_modelos.csv')

        best = df_res.iloc[0]
        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.markdown(f"""
        <div class="stat-card" style="border-top-color:#16a34a;">
            <div class="stat-label">Melhor Modelo</div>
            <div class="stat-value stat-value-green" style="font-size:1.3rem;">{best['Modelo']}</div>
        </div>""", unsafe_allow_html=True)
        mc2.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">R2 Teste</div>
            <div class="stat-value stat-value-green">{best['R2_Test']:.4f}</div>
        </div>""", unsafe_allow_html=True)
        mc3.markdown(f"""
        <div class="stat-card accent-blue">
            <div class="stat-label">MAE Teste</div>
            <div class="stat-value stat-value-blue">R$ {best['MAE_Test']:,.0f}</div>
        </div>""", unsafe_allow_html=True)
        mc4.markdown(f"""
        <div class="stat-card accent-amber">
            <div class="stat-label">CV R2 Medio</div>
            <div class="stat-value stat-value-amber">{best['CV_R2_Mean']:.4f}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.dataframe(
            df_res.style
                .background_gradient(subset=['R2_Test', 'CV_R2_Mean'], cmap='Greens')
                .background_gradient(subset=['MAE_Test', 'RMSE_Test'], cmap='Reds_r')
                .format({'MAE_Train': 'R$ {:,.0f}', 'RMSE_Train': 'R$ {:,.0f}',
                         'MAE_Test': 'R$ {:,.0f}', 'RMSE_Test': 'R$ {:,.0f}',
                         'R2_Train': '{:.4f}', 'R2_Test': '{:.4f}',
                         'CV_R2_Mean': '{:.4f}', 'CV_R2_Std': '{:.4f}'}),
            use_container_width=True,
            height=280
        )

        if os.path.exists('graficos/comparacao_modelos.png'):
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="chart-panel"><div class="chart-panel-header">Comparacao Visual — R2 · MAE · RMSE</div>',
                        unsafe_allow_html=True)
            st.image('graficos/comparacao_modelos.png', use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("""
        <div class="section-stripe">
            <span class="section-label">
                <span class="section-label-green">02</span> — Sobre os Algoritmos
            </span>
        </div>
        """, unsafe_allow_html=True)

        desc_modelos = [
            ("LinearRegression", "Regressao Linear",   "Modelo base — relacao linear entre features e target. Referencia de comparacao."),
            ("Ridge",            "Ridge  —  L2",        "Regularizacao L2, penaliza coeficientes grandes. Reduz overfitting em dados correlacionados."),
            ("Lasso",            "Lasso  —  L1",        "Regularizacao L1, promove esparsidade nos coeficientes. Seleciona as features mais relevantes."),
            ("DecisionTree",     "Decision Tree",       "Arvore de decisao com splits recursivos. Interpreta no-lineares sem transformacoes manuais."),
            ("RandomForest",     "Random Forest",       "Ensemble de arvores via bagging. Alta robustez e resistencia ao overfitting."),
            ("GradientBoosting", "Gradient Boosting",   "Boosting sequencial — cada arvore minimiza o erro residual da anterior."),
        ]

        col_desc1, col_desc2 = st.columns(2)
        for i, (key, nome, desc) in enumerate(desc_modelos):
            r2 = df_res[df_res['Modelo'] == key]['R2_Test'].values
            r2_str = f"R2 {r2[0]:.4f}" if len(r2) else "—"
            is_best = (key == best['Modelo'])
            highlight_cls = "model-info-card highlight" if is_best else "model-info-card"
            card_html = f"""
            <div class="{highlight_cls}">
                <span class="model-info-score">{r2_str}</span>
                <div class="model-info-name">{nome}</div>
                <div class="model-info-desc">{desc}</div>
            </div>"""
            if i % 2 == 0:
                col_desc1.markdown(card_html, unsafe_allow_html=True)
            else:
                col_desc2.markdown(card_html, unsafe_allow_html=True)
    else:
        st.warning("Execute o script train.py para gerar os resultados.")


st.markdown("""
<div class="site-footer">
    <strong>Conteudo educacional — Atividade Final UC Aprendizado de Maquina 2026/1.</strong>
    Os dados sao ilustrativos e nao representam valores reais de mercado.
    <div style="margin-top:8px; font-size:0.72rem; color:#8aabb8; letter-spacing:0.08em;">
        Desenvolvido por <strong style="color:#a8c8d8;">Elias · Bruno · João Clemente</strong>
    </div>
</div>
""", unsafe_allow_html=True)
