import json
from datetime import datetime
from textwrap import dedent
from typing import Any

import requests
import streamlit as st

st.set_page_config(
    page_title="Ensina.AI — Aula Inteligente",
    page_icon="🎓",
    layout="wide",
)
# Estado da aplicação
# ============================================================
def init_session_state() -> None:
    if "history" not in st.session_state:
        st.session_state.history = []
    if "last_result" not in st.session_state:
        st.session_state.last_result = ""
    if "last_payload" not in st.session_state:
        st.session_state.last_payload = {}


# ============================================================
# Configuração visual
# ============================================================
def render_header() -> None:
    st.markdown(
        """
        <div style='padding: 0.5rem 0 1rem 0;'>
            <h1 style='margin-bottom: 0.25rem;'>🎓 Ensina.AI</h1>
            <p style='font-size: 1.05rem; margin-top: 0;'>
                Gere aulas completas, exercícios, projeto prático e conteúdo explicativo em um só lugar.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# Prompt base
# ============================================================
def build_prompt(
    theme: str,
    level: str,
    audience: str,
    area_focus: str,
    include_code: bool,
    include_exercises: bool,
    include_project: bool,
    include_plan: bool,
    lesson_goal: str,
) -> str:
    code_section = (
        dedent(
            """
            Inclua código apenas quando ele realmente ajudar a entender ou aplicar o tema.
            Quando incluir código:
            - traga um exemplo funcional
            - explique linha por linha em linguagem simples
            - mostre a entrada, o processamento e a saída
            - explique por que esse código resolve o problema apresentado
            """
        ).strip()
        if include_code
        else "Não inclua código se ele não fizer sentido para o tema."
    )

    exercises_section = (
        dedent(
            """
            Crie atividades práticas em 3 níveis:
            - Básico: 3 atividades de compreensão
            - Intermediário: 2 atividades aplicadas
            - Desafio: 1 atividade com cenário real
            Traga gabarito ou orientação de resolução comentada.
            """
        ).strip()
        if include_exercises
        else ""
    )

    project_section = (
        dedent(
            """
            Crie um projeto prático completo com:
            - nome do projeto
            - objetivo
            - problema real que resolve
            - pré-requisitos
            - materiais ou ferramentas necessárias
            - passo a passo detalhado de desenvolvimento
            - resultado esperado
            - como validar se ficou correto
            - melhorias futuras
            """
        ).strip()
        if include_project
        else ""
    )

    plan_section = (
        "Monte também um plano de estudo de 7 dias para consolidar o aprendizado."
        if include_plan
        else ""
    )

    return dedent(
        f"""
        Você é um professor especialista, didático e orientado a resultados.

        Sua missão é criar um material de ensino completo sobre o tema informado, de forma que uma pessoa {audience.lower()} consiga entender, praticar, aplicar e ensinar o conteúdo.

        Tema: {theme}
        Nível desejado: {level}
        Foco da área: {area_focus}
        Objetivo específico da aula: {lesson_goal}

        Estruture a resposta exatamente nesta ordem:

        1. Visão geral do tema
        - Explique o que é.
        - Explique por que esse tema importa.
        - Mostre onde ele aparece na prática.

        2. Explicação intuitiva
        - Explique de forma simples e acessível.
        - Use analogias do cotidiano.

        3. Conceitos e fundamentos essenciais
        - Liste os conceitos centrais.
        - Explique cada conceito em linguagem clara.
        - Mostre como os conceitos se conectam.

        4. Base teórica essencial
        - Traga teoria suficiente para entendimento sólido.
        - Evite excesso de academicismo.
        - Explique o porquê das coisas.

        5. Aplicação prática guiada
        - Mostre passo a passo como aplicar o tema.
        - Comece com um exemplo simples.
        - Evolua para um exemplo mais próximo do mundo real.

        6. Exemplo do dia a dia
        - Dê um exemplo simples e fácil de visualizar.

        7. Exemplo profissional
        - Dê um exemplo de mercado, negócio, tecnologia ou operação.

        8. Erros comuns
        - Liste os erros de iniciantes.
        - Explique como evitar cada um.

        9. Como ensinar esse conteúdo para outra pessoa
        - Explique em linguagem muito simples.
        - Traga uma versão para iniciantes.
        - Traga uma versão para contexto profissional.

        10. Resumo inteligente
        - Resumo em tópicos
        - Palavras-chave
        - Checklist do que foi aprendido
        - 5 perguntas com respostas

        {code_section}

        {exercises_section}

        {project_section}

        {plan_section}

        Regras obrigatórias:
        - Não assuma conhecimento prévio.
        - Use linguagem clara, amigável e organizada.
        - Vá do simples ao mais técnico.
        - Priorize clareza e utilidade prática.
        - Sempre conecte teoria com prática.
        - Se o tema pedir código, entregue código realmente utilizável.
        - Se o tema pedir projeto, entregue desenvolvimento passo a passo.
        - Formate a resposta com títulos e subtítulos bem organizados.
        """
    ).strip()


# ============================================================
# Geração local com conteúdo real
# ============================================================
def infer_theme_category(theme: str) -> str:
    t = theme.lower()
    if any(k in t for k in ["sql", "bigquery", "query", "banco de dados"]):
        return "sql"
    if any(k in t for k in ["python", "pandas", "numpy", "streamlit"]):
        return "python"
    if any(k in t for k in ["machine learning", "aprendizado de máquina", "ml", "regress", "classifica"]):
        return "ml"
    if any(k in t for k in ["power bi", "dax", "power query", "bi"]):
        return "powerbi"
    if any(k in t for k in ["crisp-dm", "crisp dm", "metodologia de dados"]):
        return "crispdm"
    if any(k in t for k in ["processo", "lean", "six sigma", "melhoria contínua", "bpm"]):
        return "processos"
    return "generic"


def get_code_example(theme: str, category: str) -> str:
    examples = {
        "sql": dedent(
            """
            ## Código pronto para aula
            ```sql
            SELECT
                categoria,
                COUNT(*) AS total_pedidos,
                ROUND(SUM(valor_venda), 2) AS faturamento,
                ROUND(AVG(valor_venda), 2) AS ticket_medio
            FROM vendas
            WHERE data_venda >= '2026-01-01'
            GROUP BY categoria
            ORDER BY faturamento DESC;
            ```
            """
        ).strip(),
        "python": dedent(
            """
            ## Código pronto para aula
            ```python
            import pandas as pd

            dados = {
                "produto": ["A", "B", "C", "D"],
                "vendas": [120, 90, 150, 80],
                "custo": [70, 50, 80, 45],
            }

            df = pd.DataFrame(dados)
            df["lucro"] = df["vendas"] - df["custo"]
            df["margem"] = (df["lucro"] / df["vendas"]) * 100
            print(df)
            ```
            """
        ).strip(),
        "ml": dedent(
            """
            ## Código pronto para aula
            ```python
            import pandas as pd
            from sklearn.linear_model import LinearRegression
            from sklearn.metrics import mean_absolute_error
            from sklearn.model_selection import train_test_split

            df = pd.DataFrame({
                "horas_estudo": [1, 2, 3, 4, 5, 6, 7, 8],
                "nota": [3, 4, 4.5, 5, 6, 7, 8, 9],
            })

            X = df[["horas_estudo"]]
            y = df["nota"]
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
            modelo = LinearRegression()
            modelo.fit(X_train, y_train)
            previsoes = modelo.predict(X_test)
            erro = mean_absolute_error(y_test, previsoes)
            print("Erro médio absoluto:", round(erro, 2))
            ```
            """
        ).strip(),
        "powerbi": dedent(
            """
            ## Conteúdo prático para aula
            ```DAX
            Faturamento Total = SUM(Vendas[ValorVenda])
            Ticket Médio = DIVIDE(SUM(Vendas[ValorVenda]), COUNT(Vendas[IDPedido]))
            ```
            """
        ).strip(),
        "generic": dedent(
            f"""
            ## Exemplo aplicável
            Para o tema **{theme}**, mostre em aula:
            - um problema real
            - uma forma simples de resolver
            - uma pequena atividade prática
            - uma forma de medir se o aluno aprendeu
            """
        ).strip(),
    }
    return examples.get(category, examples["generic"])


def get_project_example(theme: str, category: str) -> dict[str, Any]:
    projects: dict[str, dict[str, Any]] = {
        "sql": {
            "name": "Mini Laboratório de Consultas SQL",
            "objective": "Ensinar leitura, filtro, agrupamento e ordenação de dados em tabelas de vendas.",
            "problem": "Muitas pessoas sabem a teoria de SQL, mas travam ao montar consultas úteis para análise.",
            "steps": [
                "Criar uma tabela simples de vendas com colunas de data, categoria, cliente e valor.",
                "Montar consultas com SELECT, WHERE, GROUP BY e ORDER BY.",
                "Criar perguntas de negócio para os alunos responderem com SQL.",
                "Comparar respostas corretas e discutir otimizações.",
            ],
            "tools": ["SQLite, BigQuery ou PostgreSQL", "Editor SQL", "GitHub"],
            "deliverable": "Uma coleção de consultas prontas e comentadas para uso em aula.",
        },
        "python": {
            "name": "Análise de Vendas com Python e Pandas",
            "objective": "Ensinar manipulação de dados, criação de colunas e análise básica.",
            "problem": "Iniciantes têm dificuldade para ligar Python a situações reais de negócio.",
            "steps": [
                "Criar um DataFrame com dados simples de vendas.",
                "Calcular lucro, margem e ranking de produtos.",
                "Exibir o resultado em tabela e gráfico.",
                "Explicar cada etapa em linguagem simples.",
            ],
            "tools": ["Python", "Pandas", "Matplotlib ou Streamlit", "GitHub"],
            "deliverable": "Um notebook ou app simples com análise pronta para demonstração em aula.",
        },
        "ml": {
            "name": "Preditor Simples de Desempenho",
            "objective": "Ensinar o fluxo básico de machine learning de forma leve.",
            "problem": "Muitos alunos veem ML como algo complexo demais e não conseguem enxergar a lógica do processo.",
            "steps": [
                "Escolher uma variável de entrada e uma de saída.",
                "Separar dados de treino e teste.",
                "Treinar um modelo simples.",
                "Avaliar o erro e discutir limitações.",
            ],
            "tools": ["Python", "Pandas", "Scikit-learn", "Jupyter ou Streamlit"],
            "deliverable": "Um exemplo funcional de regressão com explicação didática.",
        },
        "generic": {
            "name": f"Projeto Aplicado de {theme}",
            "objective": f"Transformar o tema {theme} em algo ensinável e aplicável.",
            "problem": f"Pessoas iniciantes costumam ter dificuldade para sair da teoria em {theme}.",
            "steps": [
                "Explicar o conceito central.",
                "Criar um exemplo prático.",
                "Aplicar em um pequeno caso.",
                "Registrar o aprendizado como portfólio.",
            ],
            "tools": ["Markdown", "PowerPoint ou Google Slides", "GitHub"],
            "deliverable": "Um material didático com explicação, atividade e resultado.",
        },
    }
    return projects.get(category, projects["generic"])


def generate_local_lesson(payload: dict[str, Any]) -> str:
    theme = payload["theme"]
    level = payload["level"]
    audience = payload["audience"]
    area_focus = payload["area_focus"]
    goal = payload["lesson_goal"]
    category = infer_theme_category(theme)
    code_block = get_code_example(theme, category) if payload["include_code"] else ""
    project = get_project_example(theme, category) if payload["include_project"] else None

    fundamentals_map = {
        "sql": ["tabelas e colunas", "seleção de dados com SELECT", "filtros com WHERE", "agrupamento com GROUP BY", "ordenação com ORDER BY"],
        "python": ["variáveis e estruturas básicas", "manipulação de dados", "uso de bibliotecas", "lógica passo a passo", "interpretação da saída"],
        "ml": ["dados de entrada e saída", "treino e teste", "modelo preditivo", "previsão", "avaliação de desempenho"],
        "generic": ["conceito principal", "partes do tema", "aplicação prática", "erros comuns", "como ensinar"],
    }

    theory_map = {
        "sql": "SQL é a linguagem usada para consultar e manipular dados em bancos relacionais. A lógica principal está em selecionar, filtrar, agrupar e ordenar informações para responder perguntas de negócio.",
        "python": "Python é uma linguagem muito usada para automação, análise de dados e desenvolvimento de aplicações. Seu valor no ensino está na leitura simples e na capacidade de transformar lógica em resultado prático.",
        "ml": "Machine Learning ensina o computador a identificar padrões a partir de dados. Em vez de programar todas as regras manualmente, fornecemos exemplos para o modelo aprender relações e fazer previsões.",
        "generic": f"{theme} deve ser ensinado como algo que sai da teoria e chega à prática. O ponto principal é mostrar conceito, aplicação e utilidade real.",
    }

    intuitive_map = {
        "sql": "Imagine um arquivo gigante de informações. SQL é a forma organizada de fazer perguntas a esse arquivo para encontrar respostas com rapidez.",
        "python": "Imagine que você quer ensinar o computador a repetir tarefas e fazer contas por você. Python é uma forma simples de dar essas instruções.",
        "ml": "Pense em Machine Learning como um aluno que observa muitos exemplos e começa a reconhecer padrões sozinho.",
        "generic": f"Pense em {theme} como uma ferramenta para entender melhor um problema e agir de forma mais segura.",
    }

    day_to_day_map = {
        "sql": "Imagine uma loja com milhares de vendas registradas. SQL ajuda a descobrir rapidamente quais produtos venderam mais, em que período e para quais clientes.",
        "python": "Imagine calcular automaticamente o lucro de vários produtos sem fazer conta manualmente. Python faz esse trabalho repetitivo por você.",
        "ml": "Imagine prever a nota de um aluno com base em horas de estudo observando exemplos anteriores.",
        "generic": f"Imagine uma situação comum em que {theme} ajude a organizar, entender ou melhorar um problema real.",
    }

    professional_map = {
        "sql": "Em empresas, SQL é usado para responder perguntas de negócio com base em dados: faturamento, clientes, produtos e desempenho operacional.",
        "python": "No mercado, Python é usado para automação, análise de dados, construção de relatórios, APIs e aplicações.",
        "ml": "No contexto profissional, machine learning pode apoiar previsão de demanda, risco, churn, recomendação e classificação.",
        "generic": f"No contexto profissional, {theme} pode apoiar análise, melhoria, tomada de decisão ou entrega de valor.",
    }

    fundamentals = fundamentals_map.get(category, fundamentals_map["generic"])
    fundamentals_md = "\n".join([f"- {item}" for item in fundamentals])

    exercises_block = ""
    if payload["include_exercises"]:
        exercises_block = dedent(
            f"""
            ## Atividades práticas prontas para utilizar
            ### Nível básico
            1. Explique com suas palavras o que é **{theme}**.
            2. Cite um problema real que pode ser resolvido com **{theme}**.
            3. Liste os conceitos mais importantes do tema e diga por que eles importam.

            ### Nível intermediário
            1. Monte um exemplo aplicado de uso de **{theme}** no trabalho ou em um projeto.
            2. Explique quais decisões precisam ser tomadas para aplicar esse tema corretamente.

            ### Nível desafio
            1. Crie uma mini solução usando **{theme}** para resolver um problema específico.
            2. Explique como você ensinaria essa solução para outra pessoa.
            """
        ).strip()

    project_block = ""
    if project:
        steps_md = "\n".join([f"{i + 1}. {step}" for i, step in enumerate(project["steps"])])
        tools_md = "\n".join([f"- {tool}" for tool in project["tools"]])
        project_block = dedent(
            f"""
            ## Projeto prático com desenvolvimento passo a passo
            **Nome do projeto:** {project['name']}

            **Objetivo:**
            {project['objective']}

            **Problema que resolve:**
            {project['problem']}

            **Pré-requisitos:**
            - noções básicas do tema
            - vontade de praticar com um caso real ou simulado

            **Ferramentas sugeridas:**
            {tools_md}

            **Passo a passo de desenvolvimento:**
            {steps_md}

            **Entrega final esperada:**
            {project['deliverable']}
            """
        ).strip()

    plan_block = ""
    if payload["include_plan"]:
        plan_block = dedent(
            f"""
            ## Plano de aula ou estudo em 7 dias
            - **Dia 1:** visão geral e motivação sobre {theme}
            - **Dia 2:** conceitos e fundamentos essenciais
            - **Dia 3:** base teórica e explicação intuitiva
            - **Dia 4:** prática guiada com exemplo
            - **Dia 5:** execução das atividades práticas
            - **Dia 6:** desenvolvimento do projeto passo a passo
            - **Dia 7:** revisão final e ensino para outra pessoa
            """
        ).strip()

    return dedent(
        f"""
        # Material completo: {theme}

        **Nível:** {level}
        **Público:** {audience}
        **Área:** {area_focus}
        **Objetivo:** {goal}

        ## 1. Visão geral do tema
        O tema **{theme}** é importante porque ajuda a transformar conhecimento em ação.

        ## 2. Explicação intuitiva
        {intuitive_map.get(category, intuitive_map['generic'])}

        ## 3. Conceitos e fundamentos essenciais
        {fundamentals_md}

        ## 4. Base teórica essencial
        {theory_map.get(category, theory_map['generic'])}

        ## 5. Aplicação prática guiada
        1. Comece apresentando um problema simples.
        2. Mostre como {theme} ajuda a organizar a solução.
        3. Demonstre um exemplo pequeno e comentado.
        4. Peça ao aluno para adaptar o exemplo.
        5. Evolua para um caso mais próximo da prática real.

        ## 6. Exemplo do dia a dia
        {day_to_day_map.get(category, day_to_day_map['generic'])}

        ## 7. Exemplo profissional
        {professional_map.get(category, professional_map['generic'])}

        ## 8. Erros comuns
        - tentar avançar sem dominar a base
        - decorar sem entender a lógica
        - ignorar atividades práticas
        - não revisar o que foi aprendido
        - focar só na ferramenta e esquecer o problema real

        ## 9. Como ensinar esse conteúdo para outra pessoa
        Comece com uma analogia simples. Depois, mostre o conceito técnico em linguagem acessível.

        ## 10. Resumo inteligente
        - **Resumo:** {theme} combina entendimento, aplicação e comunicação.
        - **Palavras-chave:** conceito, prática, aplicação, exemplo, resultado.
        - **Checklist:** consigo definir? consigo dar exemplo? consigo aplicar? consigo ensinar?

        {code_block}

        {exercises_block}

        {project_block}

        {plan_block}
        """
    ).strip()


# ============================================================
# Integração com APIs de IA
# ============================================================
def get_provider_configs() -> dict[str, dict[str, Any]]:
    try:
        groq_api_key = st.secrets.get("GROQ_API_KEY", "")
        groq_model = st.secrets.get("GROQ_MODEL", "llama-3.3-70b-versatile")
        groq_base_url = st.secrets.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

        gemini_api_key = st.secrets.get("GEMINI_API_KEY", "")
        gemini_model = st.secrets.get("GEMINI_MODEL", "gemini-2.5-flash")
        gemini_base_url = st.secrets.get("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
    except Exception:
        groq_api_key = ""
        groq_model = "llama-3.3-70b-versatile"
        groq_base_url = "https://api.groq.com/openai/v1"
        gemini_api_key = ""
        gemini_model = "gemini-2.5-flash"
        gemini_base_url = "https://generativelanguage.googleapis.com/v1beta"

    return {
        "Groq": {
            "api_key": groq_api_key,
            "model": groq_model,
            "base_url": groq_base_url,
            "enabled": bool(groq_api_key),
        },
        "Gemini": {
            "api_key": gemini_api_key,
            "model": gemini_model,
            "base_url": gemini_base_url,
            "enabled": bool(gemini_api_key),
        },
    }


def available_generation_modes() -> list[str]:
    configs = get_provider_configs()
    modes = ["Modo local"]
    for provider_name, config in configs.items():
        if config["enabled"]:
            modes.insert(0, provider_name)
    return modes


def generate_with_groq(prompt: str, temperature: float = 0.4) -> str:
    config = get_provider_configs()["Groq"]
    if not config["enabled"]:
        raise RuntimeError("Groq não configurado.")

    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": "Você é um professor especialista, didático e orientado a resultados."},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
    }

    response = requests.post(
        f"{config['base_url'].rstrip('/')}/chat/completions",
        headers=headers,
        data=json.dumps(payload),
        timeout=120,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Erro da API Groq: {response.status_code} - {response.text[:500]}")

    data = response.json()
    choices = data.get("choices", [])
    if not choices:
        raise RuntimeError("A Groq respondeu sem conteúdo utilizável.")

    message = choices[0].get("message", {})
    content = message.get("content", "")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("Não foi possível extrair o texto da resposta da Groq.")
    return content.strip()


def extract_text_from_gemini(data: dict[str, Any]) -> str:
    candidates = data.get("candidates", [])
    texts: list[str] = []
    for candidate in candidates:
        content = candidate.get("content", {})
        parts = content.get("parts", []) if isinstance(content, dict) else []
        for part in parts:
            text = part.get("text") if isinstance(part, dict) else None
            if isinstance(text, str) and text.strip():
                texts.append(text.strip())
    return "\n\n".join(texts).strip()


def generate_with_gemini(prompt: str, temperature: float = 0.4) -> str:
    config = get_provider_configs()["Gemini"]
    if not config["enabled"]:
        raise RuntimeError("Gemini não configurado.")

    headers = {"Content-Type": "application/json"}
    payload = {
        "systemInstruction": {
            "parts": [
                {"text": "Você é um professor especialista, didático e orientado a resultados."}
            ]
        },
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": temperature
        },
    }

    url = (
        f"{config['base_url'].rstrip('/')}/models/{config['model']}:generateContent"
        f"?key={config['api_key']}"
    )
    response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)
    if response.status_code >= 400:
        raise RuntimeError(f"Erro da API Gemini: {response.status_code} - {response.text[:500]}")

    data = response.json()
    text = extract_text_from_gemini(data)
    if not text:
        raise RuntimeError("Não foi possível extrair o texto da resposta da Gemini.")
    return text


def generate_with_provider(provider: str, prompt: str, temperature: float = 0.4) -> str:
    if provider == "Groq":
        return generate_with_groq(prompt, temperature)
    if provider == "Gemini":
        return generate_with_gemini(prompt, temperature)
    raise RuntimeError(f"Provedor não suportado: {provider}")


# ============================================================
# Persistência em sessão
# ============================================================
def save_history(theme: str, result: str, payload: dict[str, Any], source: str) -> None:
    st.session_state.history.insert(
        0,
        {
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "theme": theme,
            "source": source,
            "result": result,
            "payload": payload,
        },
    )
    st.session_state.last_result = result
    st.session_state.last_payload = payload


# ============================================================
# Interface
# ============================================================
def render_sidebar() -> dict[str, Any]:
    with st.sidebar:
        st.header("Configurações da aula")
        theme = st.text_input("Tema da aula", placeholder="Ex.: SQL para análise de dados")
        lesson_goal = st.text_area(
            "Objetivo específico",
            placeholder="Ex.: Quero entender o tema do zero e ser capaz de ensinar para outra pessoa.",
            height=100,
        )
        level = st.selectbox("Nível", ["Iniciante", "Básico ao Intermediário", "Intermediário", "Básico ao Avançado"])
        audience = st.selectbox("Público", ["Leigo", "Estudante", "Profissional em transição", "Equipe de trabalho"])
        area_focus = st.selectbox("Foco principal", ["Tecnologia", "Dados", "Negócios", "Educação", "Processos", "Outro"])

        st.subheader("Recursos")
        include_code = st.checkbox("Incluir código", value=True)
        include_exercises = st.checkbox("Incluir exercícios", value=True)
        include_project = st.checkbox("Incluir projeto prático", value=True)
        include_plan = st.checkbox("Incluir plano de estudo", value=True)

        st.subheader("Modo de geração")
        generation_options = available_generation_modes()
        generation_mode = st.radio("Escolha o modo", generation_options, index=0)
        temperature = st.slider("Criatividade", min_value=0.0, max_value=1.0, value=0.4, step=0.1)

        generate = st.button("Gerar aula completa", type="primary", use_container_width=True)
        clear_history = st.button("Limpar histórico", use_container_width=True)

        if clear_history:
            st.session_state.history = []
            st.session_state.last_result = ""
            st.session_state.last_payload = {}
            st.success("Histórico limpo.")

        st.divider()
        st.caption("O app funciona sem API, mas aceita integração com Groq e Gemini por secrets.")

    return {
        "theme": theme,
        "lesson_goal": lesson_goal.strip() or "Entender, aplicar e ensinar esse tema com clareza.",
        "level": level,
        "audience": audience,
        "area_focus": area_focus,
        "include_code": include_code,
        "include_exercises": include_exercises,
        "include_project": include_project,
        "include_plan": include_plan,
        "generation_mode": generation_mode,
        "temperature": temperature,
        "generate": generate,
    }


def render_overview() -> None:
    configs = get_provider_configs()
    enabled = [name for name, cfg in configs.items() if cfg["enabled"]]
    status = ", ".join(enabled) if enabled else "Local"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Histórico da sessão", len(st.session_state.history))
    with col2:
        st.metric("Provedores ativos", status)
    with col3:
        st.metric("App", "Pronto para MVP")

    st.info("Este app funciona em modo local e também pode gerar conteúdo via Groq ou Gemini quando as chaves forem configuradas.")


def render_setup_tab() -> None:
    st.subheader("Como ligar Groq e Gemini")
    st.markdown(
        """
        Crie o arquivo `.streamlit/secrets.toml` no projeto local ou configure as secrets no ambiente de deploy.

        Exemplo:
        ```toml
        GROQ_API_KEY = "sua_chave_groq"
        GROQ_MODEL = "llama-3.3-70b-versatile"
        GROQ_BASE_URL = "https://api.groq.com/openai/v1"

        GEMINI_API_KEY = "sua_chave_gemini"
        GEMINI_MODEL = "gemini-2.5-flash"
        GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
        ```
        """
    )

    st.subheader("Dependências sugeridas")
    st.code("streamlit>=1.44.0\nrequests>=2.31.0", language="txt")

    st.subheader("Observações de integração")
    st.markdown(
        """
        - Groq usa endpoint compatível com OpenAI em `/chat/completions`.
        - Gemini usa `generateContent` por modelo.
        - O modo local continua disponível como fallback.
        """
    )


def render_history_tab() -> None:
    st.subheader("Histórico da sessão")
    if not st.session_state.history:
        st.caption("Nenhuma aula foi gerada ainda.")
        return

    for i, item in enumerate(st.session_state.history, start=1):
        with st.expander(f"{i}. {item['theme']} — {item['timestamp']} — {item['source']}"):
            st.markdown(item["result"])
            st.download_button(
                label="Baixar em Markdown",
                data=item["result"],
                file_name=f"aula_{item['theme'].lower().replace(' ', '_')}.md",
                mime="text/markdown",
                key=f"download_{i}",
            )


def render_generator_tab(payload: dict[str, Any]) -> None:
    st.subheader("Gerador inteligente")
    st.markdown(
        """
        Preencha os campos na barra lateral e clique em **Gerar aula completa**.
        O conteúdo pode ser criado por Groq, Gemini ou pelo modo local estruturado.
        """
    )

    if payload["generate"]:
        if not payload["theme"].strip():
            st.warning("Informe um tema para gerar a aula.")
            return

        prompt = build_prompt(
            theme=payload["theme"],
            level=payload["level"],
            audience=payload["audience"],
            area_focus=payload["area_focus"],
            include_code=payload["include_code"],
            include_exercises=payload["include_exercises"],
            include_project=payload["include_project"],
            include_plan=payload["include_plan"],
            lesson_goal=payload["lesson_goal"],
        )

        with st.expander("Ver prompt base usado na geração"):
            st.code(prompt, language="markdown")

        with st.spinner("Gerando aula..."):
            try:
                if payload["generation_mode"] in ["Groq", "Gemini"]:
                    result = generate_with_provider(payload["generation_mode"], prompt, temperature=payload["temperature"])
                    source = payload["generation_mode"]
                else:
                    result = generate_local_lesson(payload)
                    source = "Modo local"

                save_history(payload["theme"], result, payload, source)
                st.success(f"Aula gerada com sucesso via {source}.")
            except Exception as exc:
                st.error(f"Não foi possível gerar a aula: {exc}")
                return

    if st.session_state.last_result:
        st.subheader("Resultado")
        st.markdown(st.session_state.last_result)
        st.download_button(
            label="Baixar aula em Markdown",
            data=st.session_state.last_result,
            file_name="aula_completa.md",
            mime="text/markdown",
        )


def main() -> None:
    init_session_state()
    render_header()
    payload = render_sidebar()
    render_overview()

    tab1, tab2, tab3 = st.tabs(["Gerar aula", "Histórico", "Configuração"])
    with tab1:
        render_generator_tab(payload)
    with tab2:
        render_history_tab()
    with tab3:
        render_setup_tab()


if __name__ == "__main__":
    main()
