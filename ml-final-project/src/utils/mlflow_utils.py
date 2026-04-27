from __future__ import annotations
"""Helpers para tracking de experimentos com MLflow."""

import warnings
from pathlib import Path

import mlflow
import pandas as pd


def configure_mlflow_tracking(tracking_dir: Path, experiment_name: str) -> Path:
    """Configura o MLflow para usar tracking local em disco."""
    tracking_dir.mkdir(parents=True, exist_ok=True)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=".*filesystem tracking backend.*", category=FutureWarning)
        mlflow.set_tracking_uri(tracking_dir.resolve().as_uri())
        mlflow.set_experiment(experiment_name)
    return tracking_dir


def extract_model_params(model: object) -> dict[str, object]:
    """Extrai os parametros relevantes do estimador para log no MLflow."""
    if not hasattr(model, "get_params"):
        return {}

    params = model.get_params()
    selected_keys = (
        "C",
        "class_weight",
        "colsample_bytree",
        "criterion",
        "eval_metric",
        "learning_rate",
        "max_depth",
        "max_features",
        "max_iter",
        "min_child_weight",
        "min_samples_leaf",
        "min_samples_split",
        "multi_class",
        "n_estimators",
        "n_jobs",
        "objective",
        "penalty",
        "random_state",
        "solver",
        "subsample",
    )
    return {key: params[key] for key in selected_keys if key in params}


def log_training_experiment(
    tracking_dir: Path,
    experiment_name: str,
    random_state: int,
    target_column: str,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    fitted_models: dict[str, object],
    results: dict[str, dict[str, object]],
    best_model_name: str,
    model_path: Path,
    report_path: Path,
    comparison_figure_path: Path,
) -> Path:
    """Registra parametros, metricas e artefatos do treino no MLflow.

    Cria um run separado para cada modelo, facilitando a comparacao
    na UI do MLflow.
    """
    configure_mlflow_tracking(tracking_dir=tracking_dir, experiment_name=experiment_name)

    for model_name, model in fitted_models.items():
        is_best = model_name == best_model_name
        with mlflow.start_run(run_name=f"treino-{model_name.lower()}"):
            mlflow.log_param("target_column", target_column)
            mlflow.log_param("random_state", random_state)
            mlflow.log_param("train_rows", int(train_df.shape[0]))
            mlflow.log_param("train_columns", int(train_df.shape[1]))
            mlflow.log_param("test_rows", int(test_df.shape[0]))
            mlflow.log_param("test_columns", int(test_df.shape[1]))
            mlflow.log_param("model_name", model_name)
            mlflow.log_param("is_best_model", is_best)

            for param_name, param_value in extract_model_params(model).items():
                mlflow.log_param(param_name, param_value)

            metrics = results[model_name]
            mlflow.log_metric("accuracy", float(metrics["accuracy"]))
            mlflow.log_metric("precision_macro", float(metrics["precision_macro"]))
            mlflow.log_metric("recall_macro", float(metrics["recall_macro"]))
            mlflow.log_metric("f1_macro", float(metrics["f1_macro"]))

            if is_best:
                mlflow.log_artifact(str(report_path), artifact_path="reports")
                mlflow.log_artifact(str(comparison_figure_path), artifact_path="reports/figures")
                mlflow.log_artifact(str(model_path), artifact_path="model")

    return tracking_dir
