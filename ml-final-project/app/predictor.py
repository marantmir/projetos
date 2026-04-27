from __future__ import annotations
"""Helper simples para carga de artefatos e inferencia da API."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

DEFAULT_MODEL_VARIANT = "logreg"
DEPLOY_MODEL_PATHS = {
    "logreg": Path("artifacts/deploy_logreg.joblib"),
    "rf_compacto": Path("artifacts/deploy_rf_compacto.joblib"),
    "xgb_compacto": Path("artifacts/deploy_xgb_compacto.joblib"),
    "gb_compacto": Path("artifacts/deploy_gb_compacto.joblib"),
}
COURSE_TECHNICAL_NORMALIZATION = {
    "sim": "Sim",
    "nao": "N\u00e3o",
    "n\u00e3o": "N\u00e3o",
}
RAW_FEATURE_COLUMNS = [
    "Idade",
    "Curso_Tecnico",
    "Anos_Para_Formar",
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


@dataclass
class PredictionResult:
    """Representa a saida de uma predicao unica."""

    prediction: str
    probability: float
    model_name: str


class PredictorService:
    """Carrega os artefatos do projeto e executa inferencia."""

    def __init__(
        self,
        model_path: str | Path | None = None,
        preprocess_path: str | Path = "artifacts/preprocess_pipeline.joblib",
        model_variant: str | None = None,
    ) -> None:
        self.model_variant = (model_variant or os.getenv("MODEL_VARIANT", DEFAULT_MODEL_VARIANT)).strip()
        self.model_path = Path(model_path) if model_path is not None else None
        self.preprocess_path = Path(preprocess_path)
        self.model_bundle: dict[str, Any] | None = None
        self.preprocess_pipeline: Any | None = None
        self.load_error: str | None = None

    def _resolve_model_path(self, model_path: str | Path | None) -> Path:
        """Resolve o caminho do artefato a partir da variante configurada."""
        if model_path is not None:
            return Path(model_path)

        if self.model_variant not in DEPLOY_MODEL_PATHS:
            valid_variants = ", ".join(sorted(DEPLOY_MODEL_PATHS))
            raise ValueError(
                f"MODEL_VARIANT invalida: '{self.model_variant}'. Variantes aceitas: {valid_variants}."
            )

        return DEPLOY_MODEL_PATHS[self.model_variant]

    def load(self) -> None:
        """Carrega modelo e pipeline uma unica vez na inicializacao."""
        self.load_error = None
        try:
            if self.model_path is None:
                self.model_path = self._resolve_model_path(None)
            self.model_bundle = joblib.load(self.model_path)
            self.preprocess_pipeline = joblib.load(self.preprocess_path)
        except Exception as exc:  # noqa: BLE001
            self.model_bundle = None
            self.preprocess_pipeline = None
            self.load_error = str(exc)

    @property
    def ready(self) -> bool:
        """Indica se os artefatos estao prontos para servir predicoes."""
        return self.model_bundle is not None and self.preprocess_pipeline is not None

    @property
    def model_name(self) -> str:
        """Retorna o nome do modelo carregado."""
        if not self.model_bundle:
            return "indisponivel"
        return str(self.model_bundle.get("model_name", "desconhecido"))

    def health_payload(self) -> dict[str, Any]:
        """Retorna o status basico da API para o endpoint de saude."""
        return {
            "status": "ok" if self.ready else "degraded",
            "model_loaded": self.model_bundle is not None,
            "preprocess_loaded": self.preprocess_pipeline is not None,
            "model_name": self.model_name,
            "model_variant": self.model_variant,
            "model_path": str(self.model_path) if self.model_path is not None else "indisponivel",
            "error": self.load_error,
        }

    def predict(self, payload: dict[str, Any]) -> PredictionResult:
        """Aplica preprocessamento e modelo para um unico registro bruto."""
        if not self.ready:
            raise RuntimeError("Artefatos do modelo nao foram carregados.")

        normalized_payload = self._normalize_payload(payload)
        model = self.model_bundle["model"]
        feature_columns = list(self.model_bundle["feature_columns"])
        dataframe = pd.DataFrame(
            [[normalized_payload[column] for column in RAW_FEATURE_COLUMNS]],
            columns=RAW_FEATURE_COLUMNS,
        )
        transformed_array = self.preprocess_pipeline.transform(dataframe)
        transformed = pd.DataFrame(transformed_array, columns=feature_columns)

        raw_prediction = model.predict(transformed)[0]
        label_encoder = self.model_bundle.get("label_encoder")
        if label_encoder is not None:
            prediction = str(label_encoder.inverse_transform([raw_prediction])[0])
        else:
            prediction = str(raw_prediction)
        probability = self._prediction_probability(
            model=model, transformed=transformed, prediction=raw_prediction if label_encoder else prediction,
        )
        return PredictionResult(
            prediction=prediction,
            probability=probability,
            model_name=self.model_name,
        )

    def _normalize_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Padroniza os campos crus para o mesmo formato usado no treino."""
        normalized_payload = dict(payload)
        normalized_payload["Curso_Tecnico"] = self.normalize_course_tecnico(
            normalized_payload["Curso_Tecnico"]
        )
        return normalized_payload

    @staticmethod
    def normalize_course_tecnico(value: Any) -> str:
        """Normaliza a categoria de curso tecnico para os valores esperados."""
        normalized = str(value).strip().lower()
        if normalized not in COURSE_TECHNICAL_NORMALIZATION:
            valid_values = ", ".join(sorted(set(COURSE_TECHNICAL_NORMALIZATION.values())))
            raise ValueError(
                f"Valor invalido para Curso_Tecnico: '{value}'. Valores aceitos: {valid_values}."
            )

        return COURSE_TECHNICAL_NORMALIZATION[normalized]

    @staticmethod
    def _prediction_probability(model: Any, transformed: Any, prediction: str) -> float:
        """Retorna a probabilidade da classe vencedora quando disponivel."""
        if not hasattr(model, "predict_proba"):
            return 0.0

        probabilities = model.predict_proba(transformed)[0]
        classes = list(model.classes_)
        probability_by_class = dict(zip(classes, probabilities))
        return float(probability_by_class.get(prediction, max(probabilities)))
