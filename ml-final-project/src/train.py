from __future__ import annotations
"""Script de treinamento, avaliacao e tracking de experimentos.

Treina os dois modelos exigidos pelo escopo, compara metricas no conjunto
de teste, salva o melhor artefato e registra a execucao no MLflow local.
"""

import argparse
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_score, recall_score
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_sample_weight
from xgboost import XGBClassifier

from src.utils.mlflow_utils import log_training_experiment
from src.utils.report_utils import build_structured_report

TARGET_COLUMN = "Graduacao_Indicada"
DEPLOY_RF_N_ESTIMATORS = 80
DEPLOY_RF_MAX_DEPTH = 10
DEPLOY_XGB_N_ESTIMATORS = 100
DEPLOY_XGB_MAX_DEPTH = 4
DEPLOY_GB_N_ESTIMATORS = 100
DEPLOY_GB_MAX_DEPTH = 4


def parse_args() -> argparse.Namespace:
    """Le os argumentos de linha de comando do script de treino."""
    parser = argparse.ArgumentParser(description="Executa o treinamento e a avaliacao dos modelos.")
    parser.add_argument(
        "--data_dir",
        default="data/processed",
        help="Diretorio com os arquivos train.parquet e test.parquet.",
    )
    parser.add_argument(
        "--artifacts",
        default="artifacts",
        help="Diretorio onde o melhor modelo sera salvo.",
    )
    parser.add_argument(
        "--reports",
        default="reports",
        help="Diretorio onde o relatorio de metricas sera salvo.",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Seed fixa para reprodutibilidade.",
    )
    parser.add_argument(
        "--tracking-dir",
        default="mlruns",
        help="Diretorio local onde o MLflow vai salvar os runs.",
    )
    parser.add_argument(
        "--experiment-name",
        default="graduacao-indicada-classificacao",
        help="Nome do experimento no MLflow.",
    )
    # -- Logistic Regression --
    parser.add_argument(
        "--logreg-c",
        type=float,
        default=0.5,
        help="Valor de regularizacao C da LogisticRegression.",
    )
    parser.add_argument(
        "--logreg-max-iter",
        type=int,
        default=10000,
        help="Numero maximo de iteracoes da LogisticRegression.",
    )
    # -- Random Forest --
    parser.add_argument(
        "--rf-n-estimators",
        type=int,
        default=500,
        help="Quantidade de arvores da RandomForest.",
    )
    parser.add_argument(
        "--rf-max-depth",
        type=int,
        default=20,
        help="Profundidade maxima da RandomForest.",
    )
    # -- XGBoost --
    parser.add_argument(
        "--xgb-n-estimators",
        type=int,
        default=500,
        help="Quantidade de arvores do XGBoost.",
    )
    parser.add_argument(
        "--xgb-max-depth",
        type=int,
        default=6,
        help="Profundidade maxima das arvores do XGBoost.",
    )
    parser.add_argument(
        "--xgb-learning-rate",
        type=float,
        default=0.1,
        help="Taxa de aprendizado do XGBoost.",
    )
    # -- Gradient Boosting --
    parser.add_argument(
        "--gb-n-estimators",
        type=int,
        default=300,
        help="Quantidade de arvores do GradientBoosting.",
    )
    parser.add_argument(
        "--gb-max-depth",
        type=int,
        default=5,
        help="Profundidade maxima das arvores do GradientBoosting.",
    )
    parser.add_argument(
        "--gb-learning-rate",
        type=float,
        default=0.05,
        help="Taxa de aprendizado do GradientBoosting.",
    )
    return parser.parse_args()


def ensure_dir(path: Path) -> Path:
    """Cria o diretorio caso ele ainda nao exista."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_figures_dir(reports_dir: Path) -> Path:
    """Garante a existencia da pasta de figuras do relatorio."""
    figures_dir = reports_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    return figures_dir


def load_splits(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Carrega os datasets processados de treino e teste."""
    train_path = data_dir / "train.parquet"
    test_path = data_dir / "test.parquet"

    if not train_path.exists() or not test_path.exists():
        raise FileNotFoundError("Arquivos train.parquet e test.parquet sao obrigatorios.")

    train_df = pd.read_parquet(train_path)
    test_df = pd.read_parquet(test_path)
    return train_df, test_df


def split_xy(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Separa as features da coluna alvo."""
    X = df.drop(columns=[TARGET_COLUMN])
    y = df[TARGET_COLUMN]
    return X, y


def build_models(
    random_state: int,
    logreg_c: float,
    logreg_max_iter: int,
    rf_n_estimators: int,
    rf_max_depth: int | None,
    xgb_n_estimators: int = 500,
    xgb_max_depth: int = 6,
    xgb_learning_rate: float = 0.1,
    gb_n_estimators: int = 300,
    gb_max_depth: int = 5,
    gb_learning_rate: float = 0.05,
) -> dict[str, object]:
    """Monta os modelos de classificacao para comparacao."""
    return {
        "LogisticRegression": LogisticRegression(
            C=logreg_c,
            max_iter=logreg_max_iter,
            solver="lbfgs",
            class_weight="balanced",
            random_state=random_state,
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=rf_n_estimators,
            max_depth=rf_max_depth,
            min_samples_split=5,
            min_samples_leaf=3,
            max_features="log2",
            class_weight="balanced_subsample",
            criterion="entropy",
            random_state=random_state,
            n_jobs=-1,
        ),
        "XGBoost": XGBClassifier(
            n_estimators=xgb_n_estimators,
            max_depth=xgb_max_depth,
            learning_rate=xgb_learning_rate,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=3,
            objective="multi:softprob",
            eval_metric="mlogloss",
            random_state=random_state,
            n_jobs=-1,
        ),
        "GradientBoosting": GradientBoostingClassifier(
            n_estimators=gb_n_estimators,
            max_depth=gb_max_depth,
            learning_rate=gb_learning_rate,
            subsample=0.8,
            min_samples_split=10,
            min_samples_leaf=5,
            max_features="sqrt",
            random_state=random_state,
        ),
    }


def evaluate_model(model: object, X_test: pd.DataFrame, y_test: pd.Series) -> dict[str, object]:
    """Calcula as metricas principais de classificacao no conjunto de teste."""
    predictions = model.predict(X_test)
    return {
        "accuracy": accuracy_score(y_test, predictions),
        "precision_macro": precision_score(y_test, predictions, average="macro", zero_division=0),
        "recall_macro": recall_score(y_test, predictions, average="macro", zero_division=0),
        "f1_macro": f1_score(y_test, predictions, average="macro", zero_division=0),
        "classification_report": classification_report(y_test, predictions, zero_division=0),
    }


def choose_best_model(results: dict[str, dict[str, object]]) -> str:
    """Seleciona o melhor modelo priorizando F1 macro e depois accuracy."""
    ranking = sorted(
        results.items(),
        key=lambda item: (item[1]["f1_macro"], item[1]["accuracy"]),
        reverse=True,
    )
    return ranking[0][0]


def build_metrics_dataframe(results: dict[str, dict[str, object]]) -> pd.DataFrame:
    """Cria uma tabela consolidada com as metricas dos modelos."""
    return pd.DataFrame(
        [
            {
                "Modelo": model_name,
                "Accuracy": metrics["accuracy"],
                "Precision Macro": metrics["precision_macro"],
                "Recall Macro": metrics["recall_macro"],
                "F1 Macro": metrics["f1_macro"],
            }
            for model_name, metrics in results.items()
        ]
    )


def plot_model_comparison(metrics_df: pd.DataFrame, figures_dir: Path) -> Path:
    """Gera um grafico comparando as metricas dos modelos avaliados."""
    plot_df = metrics_df.set_index("Modelo")
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_df.plot(kind="bar", ax=ax, color=["#1d4ed8", "#0f766e", "#d97706", "#7c3aed"])
    ax.set_title("Comparacao de metricas dos modelos", fontsize=14, pad=14)
    ax.set_xlabel("Modelo")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.05)
    ax.legend(title="Metrica")
    plt.xticks(rotation=0)
    fig.tight_layout()

    output_path = figures_dir / "model_metrics_comparison.png"
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output_path


def build_report(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    metrics_df: pd.DataFrame,
    results: dict[str, dict[str, object]],
    best_model_name: str,
    comparison_figure_path: Path,
    experiment_name: str,
    tracking_dir: Path,
    model_config: dict[str, object],
) -> str:
    """Monta o relatorio de treinamento em HTML."""
    best_metrics = results[best_model_name]
    sections = [
        {
            "title": "Visao geral",
            "blocks": [
                {
                    "type": "metrics_grid",
                    "items": [
                        {
                            "label": "Shape do treino",
                            "value": train_df.shape,
                            "description": "Dimensao do conjunto usado para ajuste dos modelos.",
                        },
                        {
                            "label": "Shape do teste",
                            "value": test_df.shape,
                            "description": "Dimensao do conjunto usado na avaliacao final.",
                        },
                        {
                            "label": "Coluna alvo",
                            "value": TARGET_COLUMN,
                            "description": "Variavel prevista pelos classificadores.",
                        },
                        {
                            "label": "Modelos avaliados",
                            "value": "LogisticRegression, RandomForest, XGBoost e GradientBoosting",
                            "description": "Comparacao entre baseline linear, bagging e dois modelos de boosting.",
                        },
                        {
                            "label": "Config atual",
                            "value": (
                                f"logreg_c={model_config['logreg_c']}, "
                                f"logreg_max_iter={model_config['logreg_max_iter']}, "
                                f"rf_n_estimators={model_config['rf_n_estimators']}, "
                                f"rf_max_depth={model_config['rf_max_depth']}, "
                                f"xgb_n_estimators={model_config['xgb_n_estimators']}, "
                                f"xgb_max_depth={model_config['xgb_max_depth']}, "
                                f"xgb_learning_rate={model_config['xgb_learning_rate']}, "
                                f"gb_n_estimators={model_config['gb_n_estimators']}, "
                                f"gb_max_depth={model_config['gb_max_depth']}, "
                                f"gb_learning_rate={model_config['gb_learning_rate']}"
                            ),
                            "description": "Hiperparametros usados neste run para facilitar a comparacao.",
                        },
                    ],
                }
            ],
        },
        {
            "title": "Comparacao de metricas",
            "blocks": [
                {
                    "type": "table",
                    "data": metrics_df.round(4),
                },
                {
                    "type": "figure",
                    "src": f"figures/{comparison_figure_path.name}",
                    "alt": "Comparacao de metricas dos modelos",
                    "caption": "Comparacao visual entre Accuracy, Precision Macro, Recall Macro e F1 Macro.",
                },
            ],
        },
        {
            "title": "Melhor modelo",
            "blocks": [
                {
                    "type": "text",
                    "format": "paragraph",
                    "content": [
                        f"O melhor modelo foi `{best_model_name}`.",
                        (
                            "A escolha foi feita priorizando o `F1 macro`, porque a variavel alvo "
                            "e desbalanceada e essa metrica representa melhor o desempenho medio "
                            "entre todas as classes. Em caso de empate, a `accuracy` foi usada "
                            "como criterio de desempate."
                        ),
                        (
                            f"O modelo selecionado obteve F1 macro de `{best_metrics['f1_macro']:.4f}` "
                            f"e accuracy de `{best_metrics['accuracy']:.4f}`."
                        ),
                    ],
                }
            ],
        },
        {
            "title": "Tracking de experimentos",
            "blocks": [
                {
                    "type": "text",
                    "format": "paragraph",
                    "content": [
                        f"O experimento foi registrado no MLflow com o nome `{experiment_name}`.",
                        (
                            f"O backend local de tracking foi salvo em `{tracking_dir.as_posix()}` e o run "
                            "inclui parametros dos modelos, metricas de teste, o relatorio HTML e o artefato "
                            "do melhor modelo."
                        ),
                    ],
                }
            ],
        },
        {
            "title": "Classification report do melhor modelo",
            "blocks": [
                {
                    "type": "text",
                    "format": "pre",
                    "content": best_metrics["classification_report"],
                }
            ],
        },
    ]

    return build_structured_report(
        title="Relatorio de Treinamento de Modelos",
        subtitle="Comparacao entre modelos de classificacao treinados sobre os dados processados.",
        sections=sections,
    )


def save_model_artifact(
    model_name: str,
    model: object,
    feature_columns: list[str],
    artifacts_dir: Path,
    filename: str = "model.joblib",
) -> Path:
    """Salva o melhor modelo com metadados uteis para a proxima etapa."""
    ensure_dir(artifacts_dir)
    model_path = artifacts_dir / filename
    joblib.dump(
        {
            "model_name": model_name,
            "model": model,
            "feature_columns": feature_columns,
            "target_column": TARGET_COLUMN,
        },
        model_path,
    )
    return model_path


def build_deploy_models(random_state: int) -> dict[str, object]:
    """Monta variantes leves do modelo para deploy no Render."""
    return {
        "deploy_logreg.joblib": LogisticRegression(
            C=0.5,
            max_iter=10000,
            solver="lbfgs",
            class_weight="balanced",
            random_state=random_state,
        ),
        "deploy_rf_compacto.joblib": RandomForestClassifier(
            n_estimators=DEPLOY_RF_N_ESTIMATORS,
            max_depth=DEPLOY_RF_MAX_DEPTH,
            min_samples_split=5,
            min_samples_leaf=3,
            max_features="log2",
            class_weight="balanced_subsample",
            criterion="entropy",
            random_state=random_state,
            n_jobs=-1,
        ),
        "deploy_xgb_compacto.joblib": XGBClassifier(
            n_estimators=DEPLOY_XGB_N_ESTIMATORS,
            max_depth=DEPLOY_XGB_MAX_DEPTH,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=3,
            objective="multi:softprob",
            eval_metric="mlogloss",
            random_state=random_state,
            n_jobs=-1,
        ),
        "deploy_gb_compacto.joblib": GradientBoostingClassifier(
            n_estimators=DEPLOY_GB_N_ESTIMATORS,
            max_depth=DEPLOY_GB_MAX_DEPTH,
            learning_rate=0.05,
            subsample=0.8,
            min_samples_split=10,
            min_samples_leaf=5,
            max_features="sqrt",
            random_state=random_state,
        ),
    }


DEPLOY_FILENAME_TO_MODEL_NAME = {
    "deploy_logreg.joblib": "LogisticRegression",
    "deploy_rf_compacto.joblib": "RandomForestCompacto",
    "deploy_xgb_compacto.joblib": "XGBoostCompacto",
    "deploy_gb_compacto.joblib": "GradientBoostingCompacto",
}
DEPLOY_MODELS_NEEDING_SAMPLE_WEIGHT = {"deploy_xgb_compacto.joblib", "deploy_gb_compacto.joblib"}


def save_deploy_artifacts(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    artifacts_dir: Path,
    random_state: int,
) -> dict[str, Path]:
    """Treina e salva artefatos menores dedicados ao deploy."""
    deploy_paths: dict[str, Path] = {}
    deploy_models = build_deploy_models(random_state=random_state)
    sample_weights = compute_sample_weight("balanced", y_train)

    # LabelEncoder para XGBoost deploy
    label_encoder = LabelEncoder()
    y_train_encoded = label_encoder.fit_transform(y_train)

    for filename, model in deploy_models.items():
        if "xgb" in filename:
            model.fit(X_train, y_train_encoded, sample_weight=sample_weights)
            # Salva o label_encoder junto com o modelo XGBoost
            model_name = DEPLOY_FILENAME_TO_MODEL_NAME.get(filename, "Desconhecido")
            ensure_dir(artifacts_dir)
            model_path = artifacts_dir / filename
            joblib.dump(
                {
                    "model_name": model_name,
                    "model": model,
                    "feature_columns": X_train.columns.tolist(),
                    "target_column": TARGET_COLUMN,
                    "label_encoder": label_encoder,
                },
                model_path,
            )
            deploy_paths[filename] = model_path
        else:
            if filename in DEPLOY_MODELS_NEEDING_SAMPLE_WEIGHT:
                model.fit(X_train, y_train, sample_weight=sample_weights)
            else:
                model.fit(X_train, y_train)
            model_name = DEPLOY_FILENAME_TO_MODEL_NAME.get(filename, "Desconhecido")
            deploy_paths[filename] = save_model_artifact(
                model_name=model_name,
                model=model,
                feature_columns=X_train.columns.tolist(),
                artifacts_dir=artifacts_dir,
                filename=filename,
            )

    return deploy_paths


def save_report(report_content: str, reports_dir: Path) -> Path:
    """Salva o relatorio de metricas em HTML."""
    ensure_dir(reports_dir)
    report_path = reports_dir / "model_report.html"
    report_path.write_text(report_content, encoding="utf-8")
    return report_path


def run_training(
    data_dir: Path,
    artifacts_dir: Path,
    reports_dir: Path,
    random_state: int,
    tracking_dir: Path,
    experiment_name: str,
    logreg_c: float = 0.5,
    logreg_max_iter: int = 10000,
    rf_n_estimators: int = 500,
    rf_max_depth: int | None = 20,
    xgb_n_estimators: int = 500,
    xgb_max_depth: int = 6,
    xgb_learning_rate: float = 0.1,
    gb_n_estimators: int = 300,
    gb_max_depth: int = 5,
    gb_learning_rate: float = 0.05,
) -> tuple[Path, Path, str, dict[str, dict[str, object]], Path]:
    """Executa o fluxo completo de treino, avaliacao, persistencia e tracking."""
    train_df, test_df = load_splits(data_dir)
    X_train, y_train = split_xy(train_df)
    X_test, y_test = split_xy(test_df)

    model_config = {
        "logreg_c": logreg_c,
        "logreg_max_iter": logreg_max_iter,
        "rf_n_estimators": rf_n_estimators,
        "rf_max_depth": rf_max_depth,
        "xgb_n_estimators": xgb_n_estimators,
        "xgb_max_depth": xgb_max_depth,
        "xgb_learning_rate": xgb_learning_rate,
        "gb_n_estimators": gb_n_estimators,
        "gb_max_depth": gb_max_depth,
        "gb_learning_rate": gb_learning_rate,
    }

    models = build_models(
        random_state=random_state,
        logreg_c=logreg_c,
        logreg_max_iter=logreg_max_iter,
        rf_n_estimators=rf_n_estimators,
        rf_max_depth=rf_max_depth,
        xgb_n_estimators=xgb_n_estimators,
        xgb_max_depth=xgb_max_depth,
        xgb_learning_rate=xgb_learning_rate,
        gb_n_estimators=gb_n_estimators,
        gb_max_depth=gb_max_depth,
        gb_learning_rate=gb_learning_rate,
    )
    results: dict[str, dict[str, object]] = {}
    fitted_models: dict[str, object] = {}

    # LabelEncoder para XGBoost (requer labels numericos)
    label_encoder = LabelEncoder()
    y_train_encoded = label_encoder.fit_transform(y_train)
    y_test_encoded = label_encoder.transform(y_test)

    # sample_weight balanceado para modelos que nao suportam class_weight
    sample_weights = compute_sample_weight("balanced", y_train)
    models_needing_sample_weight = {"XGBoost", "GradientBoosting"}

    for model_name, model in models.items():
        if model_name == "XGBoost":
            model.fit(X_train, y_train_encoded, sample_weight=sample_weights)
            # XGBoost prediz indices numericos; decodificamos para labels originais
            xgb_preds_encoded = model.predict(X_test)
            xgb_preds = label_encoder.inverse_transform(xgb_preds_encoded)
            results[model_name] = {
                "accuracy": accuracy_score(y_test, xgb_preds),
                "precision_macro": precision_score(y_test, xgb_preds, average="macro", zero_division=0),
                "recall_macro": recall_score(y_test, xgb_preds, average="macro", zero_division=0),
                "f1_macro": f1_score(y_test, xgb_preds, average="macro", zero_division=0),
                "classification_report": classification_report(y_test, xgb_preds, zero_division=0),
            }
        else:
            if model_name in models_needing_sample_weight:
                model.fit(X_train, y_train, sample_weight=sample_weights)
            else:
                model.fit(X_train, y_train)
            results[model_name] = evaluate_model(model, X_test, y_test)
        fitted_models[model_name] = model

    best_model_name = choose_best_model(results)
    best_model = fitted_models[best_model_name]
    metrics_df = build_metrics_dataframe(results)
    figures_dir = ensure_figures_dir(reports_dir)
    comparison_figure_path = plot_model_comparison(metrics_df, figures_dir)

    report_content = build_report(
        train_df=train_df,
        test_df=test_df,
        metrics_df=metrics_df,
        results=results,
        best_model_name=best_model_name,
        comparison_figure_path=comparison_figure_path,
        experiment_name=experiment_name,
        tracking_dir=tracking_dir,
        model_config=model_config,
    )
    report_path = save_report(report_content, reports_dir)
    model_path = save_model_artifact(
        model_name=best_model_name,
        model=best_model,
        feature_columns=X_train.columns.tolist(),
        artifacts_dir=artifacts_dir,
    )
    save_deploy_artifacts(
        X_train=X_train,
        y_train=y_train,
        artifacts_dir=artifacts_dir,
        random_state=random_state,
    )

    tracking_dir = log_training_experiment(
        tracking_dir=tracking_dir,
        experiment_name=experiment_name,
        random_state=random_state,
        target_column=TARGET_COLUMN,
        train_df=train_df,
        test_df=test_df,
        fitted_models=fitted_models,
        results=results,
        best_model_name=best_model_name,
        model_path=model_path,
        report_path=report_path,
        comparison_figure_path=comparison_figure_path,
    )

    return model_path, report_path, best_model_name, results, tracking_dir


def main() -> None:
    """Ponto de entrada do script de treinamento."""
    args = parse_args()
    model_path, report_path, best_model_name, results, tracking_dir = run_training(
        data_dir=Path(args.data_dir),
        artifacts_dir=Path(args.artifacts),
        reports_dir=Path(args.reports),
        random_state=args.random_state,
        tracking_dir=Path(args.tracking_dir),
        experiment_name=args.experiment_name,
        logreg_c=args.logreg_c,
        logreg_max_iter=args.logreg_max_iter,
        rf_n_estimators=args.rf_n_estimators,
        rf_max_depth=args.rf_max_depth,
        xgb_n_estimators=args.xgb_n_estimators,
        xgb_max_depth=args.xgb_max_depth,
        xgb_learning_rate=args.xgb_learning_rate,
        gb_n_estimators=args.gb_n_estimators,
        gb_max_depth=args.gb_max_depth,
        gb_learning_rate=args.gb_learning_rate,
    )

    print(f"Melhor modelo: {best_model_name}")
    print(f"Modelo salvo em: {model_path}")
    print(f"Relatorio salvo em: {report_path}")
    print(f"Tracking MLflow salvo em: {tracking_dir}")
    for model_name, metrics in results.items():
        print(
            f"{model_name}: "
            f"accuracy={metrics['accuracy']:.4f}, "
            f"precision_macro={metrics['precision_macro']:.4f}, "
            f"recall_macro={metrics['recall_macro']:.4f}, "
            f"f1_macro={metrics['f1_macro']:.4f}"
        )


if __name__ == "__main__":
    main()
