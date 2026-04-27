from __future__ import annotations
"""Executa o pipeline completo do projeto em sequência."""

import argparse
from pathlib import Path

from src.eda import resolve_input_path, run_eda
from src.preprocess import run_preprocess
from src.train import run_training


def parse_args() -> argparse.Namespace:
    """Lê os argumentos de linha de comando do pipeline completo."""
    parser = argparse.ArgumentParser(description="Executa EDA, preprocessamento e treinamento.")
    parser.add_argument(
        "--input",
        default="data/dataset_graduacao_indicada.csv",
        help="Arquivo CSV de entrada.",
    )
    parser.add_argument(
        "--reports",
        default="reports",
        help="Diretório onde os relatórios HTML serão salvos.",
    )
    parser.add_argument(
        "--processed",
        default="data/processed",
        help="Diretório onde os datasets processados serão salvos.",
    )
    parser.add_argument(
        "--artifacts",
        default="artifacts",
        help="Diretório onde os artefatos serão salvos.",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Proporção do conjunto de teste no preprocessamento.",
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


def main() -> None:
    """Executa todas as etapas do pipeline do projeto."""
    args = parse_args()
    input_path = resolve_input_path(args.input)
    reports_dir = Path(args.reports)
    processed_dir = Path(args.processed)
    artifacts_dir = Path(args.artifacts)
    tracking_dir = Path(args.tracking_dir)

    reports_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    tracking_dir.mkdir(parents=True, exist_ok=True)

    eda_report_path, figure_paths = run_eda(input_path=input_path, output_dir=reports_dir)
    (
        preprocess_pipeline_path,
        train_dataset_path,
        test_dataset_path,
        preprocess_report_path,
        train_shape,
        test_shape,
    ) = run_preprocess(
        input_path=input_path,
        output_dir=processed_dir,
        artifacts_dir=artifacts_dir,
        reports_dir=reports_dir,
        test_size=args.test_size,
        random_state=args.random_state,
    )
    model_path, model_report_path, best_model_name, results, mlflow_tracking_dir = run_training(
        data_dir=processed_dir,
        artifacts_dir=artifacts_dir,
        reports_dir=reports_dir,
        random_state=args.random_state,
        tracking_dir=tracking_dir,
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

    print("Pipeline concluído com sucesso.")
    print(f"Relatório EDA: {eda_report_path}")
    print(f"Figuras EDA: {len(figure_paths)} arquivos")
    print(f"Pipeline de preprocessamento: {preprocess_pipeline_path}")
    print(f"Treino processado: {train_dataset_path} | shape={train_shape}")
    print(f"Teste processado: {test_dataset_path} | shape={test_shape}")
    print(f"Relatório de preprocessamento: {preprocess_report_path}")
    print(f"Melhor modelo: {best_model_name}")
    print(f"Artefato do modelo: {model_path}")
    print(f"Relatório de treinamento: {model_report_path}")
    print(f"Tracking MLflow: {mlflow_tracking_dir}")
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
