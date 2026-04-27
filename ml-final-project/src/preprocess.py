from __future__ import annotations
"""Script de preparação de dados para treino e teste.

Responsável por separar a variável alvo, aplicar preprocessamento reprodutível
e salvar os artefatos necessários para a etapa de modelagem.
"""

import argparse
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.utils.report_utils import build_structured_report

TARGET_COLUMN = "Graduacao_Indicada"


def parse_args() -> argparse.Namespace:
    """Lê os argumentos de linha de comando do preprocessamento."""
    parser = argparse.ArgumentParser(description="Executa a preparação de dados para modelagem.")
    parser.add_argument(
        "--input",
        default="data/dataset_graduacao_indicada.csv",
        help="Arquivo CSV de entrada.",
    )
    parser.add_argument(
        "--outdir",
        default="data/processed",
        help="Diretório para salvar os datasets processados.",
    )
    parser.add_argument(
        "--artifacts",
        default="artifacts",
        help="Diretório para salvar os artefatos do preprocessamento.",
    )
    parser.add_argument(
        "--reports",
        default="reports",
        help="Diretório onde o relatório HTML será salvo.",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Proporção do conjunto de teste.",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Seed fixa para reprodutibilidade.",
    )
    return parser.parse_args()


def resolve_input_path(raw_path: str) -> Path:
    """Resolve o caminho do CSV de entrada com fallbacks locais."""
    candidate = Path(raw_path)
    if candidate.exists():
        return candidate

    fallback = Path.cwd() / candidate.name
    if fallback.exists():
        return fallback

    data_fallback = Path.cwd() / "data" / candidate.name
    if data_fallback.exists():
        return data_fallback

    raise FileNotFoundError(f"Arquivo de entrada não encontrado: {raw_path}")


def ensure_dir(path: Path) -> Path:
    """Cria um diretório caso ele ainda não exista."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_figures_dir(reports_dir: Path) -> Path:
    """Garante a existência da pasta de figuras do relatório."""
    figures_dir = reports_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    return figures_dir


def make_one_hot_encoder() -> OneHotEncoder:
    """Cria um OneHotEncoder compatível com versões diferentes do scikit-learn."""
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def load_dataset(input_path: Path) -> pd.DataFrame:
    """Carrega o dataset e valida a presença da coluna alvo."""
    df = pd.read_csv(input_path)

    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Coluna alvo obrigatória ausente: {TARGET_COLUMN}")

    return df


def split_features_target(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Separa as variáveis explicativas da variável alvo."""
    X = df.drop(columns=[TARGET_COLUMN])
    y = df[TARGET_COLUMN]
    return X, y


def detect_feature_types(X: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Identifica colunas numéricas e categóricas a partir dos tipos do DataFrame."""
    numeric_features = X.select_dtypes(include=["number"]).columns.tolist()
    categorical_features = X.select_dtypes(exclude=["number"]).columns.tolist()
    return numeric_features, categorical_features


def build_preprocess_pipeline(
    numeric_features: list[str], categorical_features: list[str]
) -> ColumnTransformer:
    """Monta o pipeline de preprocessamento com tratamento por tipo de coluna."""
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", make_one_hot_encoder()),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_features),
            ("cat", categorical_pipeline, categorical_features),
        ]
    )


def transform_split(
    pipeline: ColumnTransformer,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Ajusta o pipeline no treino e transforma treino e teste."""
    # O fit acontece apenas no treino para evitar vazamento de dados.
    X_train_processed = pipeline.fit_transform(X_train)
    X_test_processed = pipeline.transform(X_test)

    feature_names = pipeline.get_feature_names_out().tolist()

    train_processed = pd.DataFrame(
        X_train_processed,
        columns=feature_names,
        index=X_train.index,
    )
    test_processed = pd.DataFrame(
        X_test_processed,
        columns=feature_names,
        index=X_test.index,
    )

    train_processed[TARGET_COLUMN] = y_train
    test_processed[TARGET_COLUMN] = y_test

    return train_processed, test_processed


def validate_processed_data(train_df: pd.DataFrame, test_df: pd.DataFrame) -> None:
    """Valida se os datasets processados não contêm valores nulos."""
    if train_df.isnull().any().any():
        raise ValueError("O dataset de treino processado contém valores nulos.")

    if test_df.isnull().any().any():
        raise ValueError("O dataset de teste processado contém valores nulos.")


def plot_split_distribution(
    y_train: pd.Series,
    y_test: pd.Series,
    figures_dir: Path,
) -> Path:
    """Gera um gráfico comparando a distribuição das classes em treino e teste."""
    distribution = pd.concat(
        [
            y_train.value_counts().rename("Treino"),
            y_test.value_counts().rename("Teste"),
        ],
        axis=1,
    ).fillna(0)

    fig, ax = plt.subplots(figsize=(12, 7))
    distribution.plot(kind="bar", ax=ax, color=["#0b7285", "#74c0fc"])
    ax.set_title("Distribuição da variável alvo em treino e teste", fontsize=14, pad=14)
    ax.set_xlabel("Classes")
    ax.set_ylabel("Quantidade de registros")
    ax.legend(title="Split")
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()

    output_path = figures_dir / "preprocess_split_distribution.png"
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output_path


def build_preprocess_report(
    input_path: Path,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    numeric_features: list[str],
    categorical_features: list[str],
    pipeline_path: Path,
    train_path: Path,
    test_path: Path,
    split_figure_path: Path,
    test_size: float,
    random_state: int,
) -> str:
    """Monta o relatório HTML da etapa de preparação de dados."""
    sections = [
        {
            "title": "Objetivo",
            "blocks": [
                {
                    "type": "text",
                    "format": "paragraph",
                    "content": "Transformar o dataset bruto em uma base pronta para treino e teste, com um pipeline reprodutível e sem vazamento de dados.",
                }
            ],
        },
        {
            "title": "Visão geral",
            "blocks": [
                {
                    "type": "metrics_grid",
                    "items": [
                        {"label": "Arquivo de entrada", "value": input_path.as_posix()},
                        {"label": "Coluna alvo", "value": TARGET_COLUMN},
                        {"label": "Shape do treino processado", "value": train_df.shape},
                        {"label": "Shape do teste processado", "value": test_df.shape},
                        {"label": "Proporção de teste", "value": f"{test_size:.0%}"},
                        {"label": "Seed fixa", "value": random_state},
                    ],
                }
            ],
        },
        {
            "title": "Separação de variáveis",
            "blocks": [
                {
                    "type": "table",
                    "data": pd.DataFrame(
                        [
                            {
                                "Tipo": "Numéricas",
                                "Quantidade": len(numeric_features),
                                "Colunas": ", ".join(numeric_features),
                            },
                            {
                                "Tipo": "Categóricas",
                                "Quantidade": len(categorical_features),
                                "Colunas": ", ".join(categorical_features),
                            },
                        ]
                    ),
                }
            ],
        },
        {
            "title": "Estratégia de preprocessamento",
            "blocks": [
                {
                    "type": "table",
                    "data": pd.DataFrame(
                        [
                            {
                                "Grupo de colunas": "Numéricas",
                                "Tratamento": 'SimpleImputer(strategy="median") + StandardScaler',
                            },
                            {
                                "Grupo de colunas": "Categóricas",
                                "Tratamento": 'SimpleImputer(strategy="most_frequent") + OneHotEncoder(handle_unknown="ignore")',
                            },
                        ]
                    ),
                },
                {
                    "type": "text",
                    "format": "paragraph",
                    "content": "O pipeline é ajustado apenas no conjunto de treino com `fit_transform` e depois aplicado ao conjunto de teste com `transform`, evitando vazamento de dados.",
                },
            ],
        },
        {
            "title": "Distribuição das classes em treino e teste",
            "blocks": [
                {
                    "type": "figure",
                    "src": f"figures/{split_figure_path.name}",
                    "alt": "Distribuição da variável alvo em treino e teste",
                    "caption": "Comparação visual da distribuição das classes após o split estratificado.",
                }
            ],
        },
        {
            "title": "Artefatos gerados",
            "blocks": [
                {
                    "type": "table",
                    "data": pd.DataFrame(
                        [
                            {"Artefato": "Pipeline de preprocessamento", "Arquivo": pipeline_path.as_posix()},
                            {"Artefato": "Treino processado", "Arquivo": train_path.as_posix()},
                            {"Artefato": "Teste processado", "Arquivo": test_path.as_posix()},
                        ]
                    ),
                }
            ],
        },
        {
            "title": "Validações executadas",
            "blocks": [
                {
                    "type": "table",
                    "data": pd.DataFrame(
                        [
                            {
                                "Validação": "Nulos no treino processado",
                                "Resultado": int(train_df.isnull().sum().sum()),
                            },
                            {
                                "Validação": "Nulos no teste processado",
                                "Resultado": int(test_df.isnull().sum().sum()),
                            },
                            {
                                "Validação": "Total de features transformadas",
                                "Resultado": train_df.shape[1] - 1,
                            },
                            {
                                "Validação": "Coluna alvo presente",
                                "Resultado": TARGET_COLUMN in train_df.columns and TARGET_COLUMN in test_df.columns,
                            },
                        ]
                    ),
                }
            ],
        },
    ]

    return build_structured_report(
        title="Relatório de Preparação de Dados",
        subtitle="Pipeline reprodutível de transformação do dataset para treino e teste.",
        sections=sections,
    )


def save_outputs(
    pipeline: ColumnTransformer,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    output_dir: Path,
    artifacts_dir: Path,
) -> tuple[Path, Path, Path]:
    """Salva o pipeline treinado e os datasets processados em disco."""
    ensure_dir(output_dir)
    ensure_dir(artifacts_dir)

    pipeline_path = artifacts_dir / "preprocess_pipeline.joblib"
    train_path = output_dir / "train.parquet"
    test_path = output_dir / "test.parquet"

    joblib.dump(pipeline, pipeline_path)
    train_df.to_parquet(train_path, index=False)
    test_df.to_parquet(test_path, index=False)

    return pipeline_path, train_path, test_path


def run_preprocess(
    input_path: Path,
    output_dir: Path,
    artifacts_dir: Path,
    reports_dir: Path,
    test_size: float,
    random_state: int,
) -> tuple[Path, Path, Path, Path, tuple[int, int], tuple[int, int]]:
    """Executa o fluxo completo de preparação de dados."""
    df = load_dataset(input_path)
    X, y = split_features_target(df)
    numeric_features, categorical_features = detect_feature_types(X)

    # A estratificação ajuda a manter a distribuição das classes entre treino e teste.
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    pipeline = build_preprocess_pipeline(numeric_features, categorical_features)
    train_processed, test_processed = transform_split(
        pipeline=pipeline,
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
    )
    validate_processed_data(train_processed, test_processed)

    pipeline_path, train_path, test_path = save_outputs(
        pipeline=pipeline,
        train_df=train_processed,
        test_df=test_processed,
        output_dir=output_dir,
        artifacts_dir=artifacts_dir,
    )
    figures_dir = ensure_figures_dir(reports_dir)
    split_figure_path = plot_split_distribution(y_train, y_test, figures_dir)
    report_content = build_preprocess_report(
        input_path=input_path,
        train_df=train_processed,
        test_df=test_processed,
        numeric_features=numeric_features,
        categorical_features=categorical_features,
        pipeline_path=pipeline_path,
        train_path=train_path,
        test_path=test_path,
        split_figure_path=split_figure_path,
        test_size=test_size,
        random_state=random_state,
    )
    report_path = reports_dir / "preprocess.html"
    report_path.write_text(report_content, encoding="utf-8")

    return (
        pipeline_path,
        train_path,
        test_path,
        report_path,
        train_processed.shape,
        test_processed.shape,
    )


def main() -> None:
    """Ponto de entrada do script de preprocessamento."""
    args = parse_args()
    input_path = resolve_input_path(args.input)
    output_dir = Path(args.outdir)
    artifacts_dir = Path(args.artifacts)
    reports_dir = ensure_dir(Path(args.reports))

    pipeline_path, train_path, test_path, report_path, train_shape, test_shape = run_preprocess(
        input_path=input_path,
        output_dir=output_dir,
        artifacts_dir=artifacts_dir,
        reports_dir=reports_dir,
        test_size=args.test_size,
        random_state=args.random_state,
    )

    print(f"Pipeline salvo em: {pipeline_path}")
    print(f"Treino processado salvo em: {train_path} | shape={train_shape}")
    print(f"Teste processado salvo em: {test_path} | shape={test_shape}")
    print(f"Relatório de preprocessamento salvo em: {report_path}")


if __name__ == "__main__":
    main()
