from __future__ import annotations
"""Script de análise exploratória para o dataset de graduação indicada.

Gera um relatório HTML e figuras PNG a partir do CSV de entrada.
"""

import argparse
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.utils.report_utils import build_structured_report


matplotlib.use("Agg")
sns.set_theme(style="whitegrid")

PREFERENCE_COLUMNS = [
    "Gosta_Matematica",
    "Gosta_Programacao",
    "Gosta_Biologia",
    "Gosta_Fisica",
    "Gosta_Quimica",
    "Gosta_Arte_Design",
    "Gosta_Comunicacao",
    "Gosta_Negocios",
    "Gosta_Historia",
    "Gosta_Geografia",
]

DISPLAY_NAMES = {
    "Idade": "Idade",
    "Curso_Tecnico": "Possui curso técnico",
    "Anos_Para_Formar": "Anos para formar",
    "Gosta_Matematica": "Gosta de Matemática",
    "Gosta_Programacao": "Gosta de Programação",
    "Gosta_Biologia": "Gosta de Biologia",
    "Gosta_Fisica": "Gosta de Física",
    "Gosta_Quimica": "Gosta de Química",
    "Gosta_Arte_Design": "Gosta de Arte e Design",
    "Gosta_Comunicacao": "Gosta de Comunicação",
    "Gosta_Negocios": "Gosta de Negócios",
    "Gosta_Historia": "Gosta de História",
    "Gosta_Geografia": "Gosta de Geografia",
    "Graduacao_Indicada": "Graduação indicada",
}


def parse_args() -> argparse.Namespace:
    """Lê os argumentos de linha de comando do script de EDA."""
    parser = argparse.ArgumentParser(description="Executa a análise exploratória dos dados.")
    parser.add_argument(
        "--input",
        default="data/dataset_graduacao_indicada.csv",
        help="Arquivo CSV que será analisado.",
    )
    parser.add_argument(
        "--out",
        default="reports",
        help="Diretório de saída do relatório em markdown e das figuras.",
    )
    return parser.parse_args()


def resolve_input_path(raw_path: str) -> Path:
    """Resolve o caminho do arquivo de entrada com alguns fallbacks úteis."""
    candidate = Path(raw_path)
    if candidate.exists():
        return candidate

    fallback = Path.cwd() / candidate.name
    if fallback.exists():
        return fallback

    data_fallback = Path.cwd() / "data" / candidate.name
    if data_fallback.exists():
        return data_fallback

    raise FileNotFoundError(f"Input file not found: {raw_path}")


def ensure_output_dirs(output_dir: Path) -> Path:
    """Garante a existência da pasta de figuras e retorna seu caminho."""
    figures_dir = output_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    return figures_dir


def build_course_tecnico_numeric(series: pd.Series) -> pd.Series:
    """Converte a coluna categórica Curso_Tecnico para formato binário."""
    normalized = series.astype(str).str.strip().str.lower()
    mapping = {"sim": 1, "nao": 0, "não": 0}
    encoded = normalized.map(mapping)

    if encoded.isnull().any():
        unexpected = sorted(series[encoded.isnull()].astype(str).unique())
        raise ValueError(f"Unexpected values in Curso_Tecnico: {unexpected}")

    return encoded.astype(int)


def prepare_table_for_display(df: pd.DataFrame, index_label: str = "índice") -> pd.DataFrame:
    """Prepara um DataFrame para renderização tabular no relatório."""
    table = df.copy()
    index_name = table.index.name or index_label
    table = table.reset_index().rename(columns={"index": index_name})
    return table


def rename_columns_for_display(df: pd.DataFrame) -> pd.DataFrame:
    """Renomeia índices e colunas para nomes mais amigáveis no relatório."""
    return df.rename(index=DISPLAY_NAMES, columns=DISPLAY_NAMES)


def format_decimal_ptbr(value: float, digits: int = 2) -> str:
    """Formata números decimais usando vírgula como separador."""
    return f"{value:.{digits}f}".replace(".", ",")


def format_int_ptbr(value: int) -> str:
    """Formata inteiros com separador de milhar no padrão brasileiro."""
    return f"{value:,}".replace(",", ".")


def plot_target_distribution(df: pd.DataFrame, figures_dir: Path) -> str:
    """Gera o gráfico de distribuição da variável alvo."""
    target_counts = df["Graduacao_Indicada"].value_counts()
    fig, ax = plt.subplots(figsize=(12, 7))
    sns.barplot(
        x=target_counts.values,
        y=target_counts.index,
        hue=target_counts.index,
        palette="Blues_r",
        dodge=False,
        legend=False,
        ax=ax,
    )
    ax.set_title(
        "Distribuição da variável alvo\nQuantidade de estudantes por graduação indicada",
        fontsize=14,
        pad=14,
    )
    ax.set_xlabel("Quantidade de estudantes", fontsize=11)
    ax.set_ylabel("Graduação indicada", fontsize=11)
    for patch in ax.patches:
        width = patch.get_width()
        y_position = patch.get_y() + patch.get_height() / 2
        percentage = width / len(df) * 100
        ax.text(
            width + 40,
            y_position,
            f"{int(width)} ({percentage:.1f}%)",
            va="center",
            fontsize=9,
        )
    fig.tight_layout()

    output_path = figures_dir / "target_distribution.png"
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output_path.name


def plot_age_distribution(df: pd.DataFrame, figures_dir: Path) -> str:
    """Gera um histograma da idade usando barras por idade inteira."""
    fig, ax = plt.subplots(figsize=(10, 6))
    min_age = int(df["Idade"].min())
    max_age = int(df["Idade"].max())
    bins = np.arange(min_age - 0.5, max_age + 1.5, 1)
    sns.histplot(
        df["Idade"],
        bins=bins,
        color="#2E86AB",
        edgecolor="white",
        linewidth=1,
        ax=ax,
    )
    mean_age = df["Idade"].mean()
    median_age = df["Idade"].median()
    ax.axvline(mean_age, color="#C73E1D", linestyle="--", linewidth=2, label=f"Média: {mean_age:.1f}")
    ax.axvline(
        median_age,
        color="#3A7D44",
        linestyle=":",
        linewidth=2,
        label=f"Mediana: {median_age:.1f}",
    )
    ax.set_title(
        "Distribuição da idade dos estudantes\nHistograma com idades inteiras",
        fontsize=14,
        pad=14,
    )
    ax.set_xlabel("Idade", fontsize=11)
    ax.set_ylabel("Frequência", fontsize=11)
    ax.set_xticks(np.arange(min_age, max_age + 1, 2))
    ax.set_xlim(min_age - 0.75, max_age + 0.75)
    ax.legend()
    fig.tight_layout()

    output_path = figures_dir / "age_distribution.png"
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output_path.name


def plot_course_tecnico_distribution(df: pd.DataFrame, figures_dir: Path) -> str:
    """Gera a distribuição da coluna categórica Curso_Tecnico."""
    fig, ax = plt.subplots(figsize=(7, 5))
    order = df["Curso_Tecnico"].value_counts().index
    sns.countplot(
        data=df,
        x="Curso_Tecnico",
        order=order,
        hue="Curso_Tecnico",
        palette="Set2",
        legend=False,
        ax=ax,
    )
    ax.set_title(
        "Distribuição de estudantes com curso técnico\nComparação entre respostas Sim e Não",
        fontsize=14,
        pad=14,
    )
    ax.set_xlabel("Possui curso técnico", fontsize=11)
    ax.set_ylabel("Quantidade de estudantes", fontsize=11)
    total = len(df)
    for patch in ax.patches:
        height = patch.get_height()
        percentage = height / total * 100
        ax.text(
            patch.get_x() + patch.get_width() / 2,
            height + 80,
            f"{int(height)}\n({percentage:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    fig.tight_layout()

    output_path = figures_dir / "curso_tecnico_distribution.png"
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output_path.name


def plot_correlation_heatmap(df: pd.DataFrame, figures_dir: Path) -> str:
    """Gera o mapa de calor das correlações entre variáveis explicativas."""
    correlation_df = df.drop(columns=["Graduacao_Indicada"]).copy()
    correlation_df["Curso_Tecnico"] = build_course_tecnico_numeric(
        correlation_df["Curso_Tecnico"]
    )
    correlation = correlation_df.corr(numeric_only=True)
    correlation = rename_columns_for_display(correlation)

    # O triângulo superior e a diagonal são ocultados para destacar apenas
    # as relações entre pares de variáveis.
    mask = np.triu(np.ones_like(correlation, dtype=bool))
    off_diagonal = correlation.where(~np.eye(len(correlation), dtype=bool))
    max_abs_corr = float(off_diagonal.abs().max().max())
    color_limit = max(0.03, round(max_abs_corr + 0.005, 3))

    fig, ax = plt.subplots(figsize=(11, 8))
    sns.heatmap(
        correlation,
        mask=mask,
        cmap="coolwarm",
        center=0,
        vmin=-color_limit,
        vmax=color_limit,
        annot=True,
        fmt=".2f",
        linewidths=0.5,
        cbar_kws={"shrink": 0.8, "label": "Correlação de Pearson"},
        ax=ax,
    )
    ax.set_title(
        "Mapa de calor das correlações entre variáveis\nTriângulo inferior sem a diagonal, destacando relações lineares fracas",
        fontsize=14,
        pad=14,
    )
    ax.set_xlabel("Variáveis explicativas", fontsize=11)
    ax.set_ylabel("Variáveis explicativas", fontsize=11)
    fig.tight_layout()

    output_path = figures_dir / "feature_correlation.png"
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output_path.name


def plot_preference_heatmap(df: pd.DataFrame, figures_dir: Path) -> str:
    """Gera a média das preferências agrupadas por graduação indicada."""
    grouped = (
        df.groupby("Graduacao_Indicada")[PREFERENCE_COLUMNS]
        .mean()
        .sort_index()
        .round(2)
    )
    grouped = rename_columns_for_display(grouped)

    fig, ax = plt.subplots(figsize=(13, 8))
    sns.heatmap(
        grouped,
        cmap="YlGnBu",
        annot=True,
        fmt=".2f",
        linewidths=0.5,
        cbar_kws={"shrink": 0.8, "label": "Média do nível de interesse"},
        ax=ax,
    )
    ax.set_title(
        "Média das preferências por graduação indicada\nAjuda a entender quais interesses se destacam em cada curso",
        fontsize=14,
        pad=14,
    )
    ax.set_xlabel("Preferências avaliadas", fontsize=11)
    ax.set_ylabel("Graduação indicada", fontsize=11)
    fig.tight_layout()

    output_path = figures_dir / "preference_by_course.png"
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output_path.name


def build_report(df: pd.DataFrame, input_path: Path, figures: dict[str, str]) -> str:
    """Monta o conteúdo do relatório final em HTML."""
    target_counts = df["Graduacao_Indicada"].value_counts()
    target_percentage = (target_counts / len(df) * 100).round(2)
    data_types = df.dtypes.astype(str)
    null_counts = df.isnull().sum()
    duplicate_count = int(df.duplicated().sum())

    summary_stats = df.describe().round(2)

    correlation_df = df.drop(columns=["Graduacao_Indicada"]).copy()
    correlation_df["Curso_Tecnico"] = build_course_tecnico_numeric(
        correlation_df["Curso_Tecnico"]
    )
    correlation = correlation_df.corr(numeric_only=True)

    # Mantemos apenas uma metade da matriz para identificar o par com maior
    # correlação sem duplicar combinações.
    upper_triangle = correlation.where(
        ~pd.DataFrame(
            [[i >= j for j in range(correlation.shape[1])] for i in range(correlation.shape[0])],
            index=correlation.index,
            columns=correlation.columns,
        )
    )
    strongest_pair_values = upper_triangle.stack()
    strongest_pair = strongest_pair_values.reindex(
        strongest_pair_values.abs().sort_values(ascending=False).index
    ).head(1)

    grouped_preferences = (
        df.groupby("Graduacao_Indicada")[PREFERENCE_COLUMNS]
        .mean()
        .round(2)
        .sort_index()
    )

    top_classes = target_counts.head(5)
    curso_tecnico_distribution = df["Curso_Tecnico"].value_counts().rename("count")
    curso_tecnico_percentage = (curso_tecnico_distribution / len(df) * 100).round(2)
    record_count_ptbr = format_int_ptbr(len(df))
    top_class_percentage_ptbr = format_decimal_ptbr(target_percentage.iloc[0])
    bottom_class_percentage_ptbr = format_decimal_ptbr(target_percentage.iloc[-1])

    strongest_pair_text = "Nenhum par de correlação foi encontrado."
    if not strongest_pair.empty:
        (feature_a, feature_b), value = strongest_pair.index[0], strongest_pair.iloc[0]
        strongest_pair_text = (
            f"{feature_a} x {feature_b}: correlação {format_decimal_ptbr(value, 3)} "
            f"(valor absoluto {format_decimal_ptbr(abs(value), 3)})"
        )

    insights = [
        (
            "O dataset está limpo para modelagem: não foram encontrados valores nulos nem "
            f"linhas duplicadas nas {record_count_ptbr} observações."
        ),
        (
            "A variável alvo está desbalanceada. "
            f"{target_counts.index[0]} representa {top_class_percentage_ptbr}% da base, "
            f"enquanto {target_counts.index[-1]} representa apenas {bottom_class_percentage_ptbr}%."
        ),
        (
            "A correlação linear entre as features é muito fraca no geral, o que sugere baixa "
            f"multicolinearidade. Em valor absoluto, o par mais forte foi {strongest_pair_text}."
        ),
        (
            "As variáveis de preferência parecem informativas para o alvo: Engenharia e "
            "Licenciatura em Matemática apresentam médias altas em matemática/física, Medicina e "
            "Odontologia se destacam em biologia/química, e Direito/Administração concentram "
            "maior afinidade com comunicação ou negócios."
        ),
        (
            "As distribuições das variáveis numéricas são bastante regulares, com médias próximas "
            "ao centro da escala e frequências semelhantes entre categorias, o que sugere uma base "
            "mais controlada do que dados reais de produção."
        ),
    ]
    sections = [
        {
            "title": "Visão geral do dataset",
            "description": "Resumo inicial da base usada na análise exploratória.",
            "blocks": [
                {
                    "type": "metrics_grid",
                    "items": [
                        {"label": "Arquivo de origem", "value": input_path.as_posix()},
                        {"label": "Linhas", "value": len(df)},
                        {"label": "Colunas", "value": df.shape[1]},
                        {"label": "Número de classes", "value": df["Graduacao_Indicada"].nunique()},
                    ],
                }
            ],
        },
        {
            "title": "Qualidade dos dados",
            "blocks": [
                {
                    "type": "table",
                    "title": "Tipos das colunas",
                    "data": prepare_table_for_display(data_types.rename("tipo").to_frame(), "índice"),
                },
                {
                    "type": "table",
                    "title": "Valores nulos",
                    "data": prepare_table_for_display(
                        null_counts.rename("quantidade_nulos").to_frame(),
                        "índice",
                    ),
                },
                {
                    "type": "text",
                    "format": "paragraph",
                    "content": f"Linhas duplicadas identificadas: {duplicate_count}.",
                },
            ],
        },
        {
            "title": "Estatísticas descritivas",
            "blocks": [
                {
                    "type": "table",
                    "data": prepare_table_for_display(summary_stats, "índice"),
                }
            ],
        },
        {
            "title": "Distribuição da variável alvo",
            "blocks": [
                {
                    "type": "table",
                    "data": prepare_table_for_display(
                        pd.DataFrame({"quantidade": target_counts, "porcentagem": target_percentage}),
                        "Graduacao_Indicada",
                    ),
                },
                {
                    "type": "figure",
                    "src": f"figures/{figures['target_distribution']}",
                    "alt": "Distribuição da variável alvo",
                    "caption": "Distribuição das graduações indicadas no dataset.",
                },
            ],
        },
        {
            "title": "Distribuição de Curso_Tecnico",
            "blocks": [
                {
                    "type": "table",
                    "data": prepare_table_for_display(
                        pd.DataFrame(
                            {
                                "quantidade": curso_tecnico_distribution,
                                "porcentagem": curso_tecnico_percentage,
                            }
                        ),
                        "Curso_Tecnico",
                    ),
                },
                {
                    "type": "figure",
                    "src": f"figures/{figures['curso_tecnico_distribution']}",
                    "alt": "Distribuição de Curso Técnico",
                    "caption": "Comparação entre estudantes com e sem curso técnico.",
                },
            ],
        },
        {
            "title": "Distribuição de idade",
            "blocks": [
                {
                    "type": "text",
                    "format": "paragraph",
                    "content": "A idade apresenta distribuição bem espalhada entre 17 e 50 anos, sem concentração extrema em uma faixa específica.",
                },
                {
                    "type": "figure",
                    "src": f"figures/{figures['age_distribution']}",
                    "alt": "Distribuição de idade",
                    "caption": "Histograma das idades com destaque para média e mediana.",
                },
            ],
        },
        {
            "title": "Correlação entre features",
            "blocks": [
                {
                    "type": "text",
                    "format": "paragraph",
                    "content": "Para calcular a correlação, a variável categórica `Curso_Tecnico` foi convertida para valores binários (`Sim` = 1 e `Não` = 0).",
                },
                {
                    "type": "table",
                    "data": prepare_table_for_display(correlation.round(3), "índice"),
                },
                {
                    "type": "figure",
                    "src": f"figures/{figures['feature_correlation']}",
                    "alt": "Correlação entre features",
                    "caption": "Mapa de calor com as relações lineares entre as variáveis explicativas.",
                },
            ],
        },
        {
            "title": "Média das preferências por alvo",
            "blocks": [
                {
                    "type": "table",
                    "data": prepare_table_for_display(grouped_preferences, "Graduacao_Indicada"),
                },
                {
                    "type": "figure",
                    "src": f"figures/{figures['preference_by_course']}",
                    "alt": "Mapa de calor das preferências",
                    "caption": "Média das preferências agrupadas por graduação indicada.",
                },
            ],
        },
        {
            "title": "Top 5 classes da variável alvo",
            "blocks": [
                {
                    "type": "table",
                    "data": prepare_table_for_display(
                        pd.DataFrame({"quantidade": top_classes, "porcentagem": target_percentage.head(5)}),
                        "Graduacao_Indicada",
                    ),
                }
            ],
        },
        {
            "title": "Insights",
            "blocks": [
                {
                    "type": "text",
                    "format": "list",
                    "ordered": True,
                    "items": insights,
                }
            ],
        },
        {
            "title": "Conclusão",
            "blocks": [
                {
                    "type": "text",
                    "format": "paragraph",
                    "content": (
                        "O dataset está pronto para a próxima etapa do pipeline. O principal ponto "
                        "de atenção para a modelagem é o desbalanceamento da variável alvo. Além "
                        "disso, como a base apresenta comportamento bastante regular, é importante "
                        "interpretar os resultados com cautela e validar o desempenho do modelo "
                        "antes de tirar conclusões mais fortes."
                    ),
                }
            ],
        },
    ]

    return build_structured_report(
        title="Relatório de EDA",
        subtitle="Análise exploratória do dataset de graduação indicada.",
        sections=sections,
    )


def run_eda(input_path: Path, output_dir: Path) -> tuple[Path, list[Path]]:
    """Executa o fluxo completo de EDA e salva relatório e figuras."""
    df = pd.read_csv(input_path)
    figures_dir = ensure_output_dirs(output_dir)

    figures = {
        "target_distribution": plot_target_distribution(df, figures_dir),
        "age_distribution": plot_age_distribution(df, figures_dir),
        "curso_tecnico_distribution": plot_course_tecnico_distribution(df, figures_dir),
        "feature_correlation": plot_correlation_heatmap(df, figures_dir),
        "preference_by_course": plot_preference_heatmap(df, figures_dir),
    }

    report_path = output_dir / "eda.html"
    report_content = build_report(df, input_path, figures)
    report_path.write_text(report_content, encoding="utf-8")

    figure_paths = [figures_dir / figure_name for figure_name in figures.values()]
    return report_path, figure_paths


def main() -> None:
    """Ponto de entrada do script de análise exploratória."""
    args = parse_args()
    input_path = resolve_input_path(args.input)
    output_dir = Path(args.out)
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path, figure_paths = run_eda(input_path, output_dir)

    print(f"Relatório de EDA gerado em: {report_path}")
    print("Figuras geradas:")
    for figure_path in figure_paths:
        print(f"- {figure_path}")


if __name__ == "__main__":
    main()
