from __future__ import annotations
"""Aplicacao FastAPI para expor a API e a interface web do projeto."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request, Response, status
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.predictor import PredictorService

EDUCATIONAL_MESSAGE = (
    "Este conteudo e destinado apenas para fins educacionais. "
    "Os dados exibidos sao ilustrativos e podem nao corresponder a situacoes reais."
)
TEMPLATES = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
REPORTS_DIR = Path("reports")
REPORT_LINKS = [
    {
        "title": "EDA",
        "description": "Analise exploratoria da base, distribuicoes, correlacoes e insights iniciais.",
        "href": "/reports/eda",
    },
    {
        "title": "Preprocessamento",
        "description": "Tratamentos aplicados, split de treino/teste e artefatos da etapa de preparacao.",
        "href": "/reports/preprocess",
    },
    {
        "title": "Treinamento",
        "description": "Comparacao entre modelos, metricas finais e selecao do melhor candidato.",
        "href": "/reports/model",
    },
]
PREFERENCE_FIELDS = [
    ("Gosta_Matematica", "Gosta de Matemática"),
    ("Gosta_Programacao", "Gosta de Programação"),
    ("Gosta_Biologia", "Gosta de Biologia"),
    ("Gosta_Fisica", "Gosta de Física"),
    ("Gosta_Quimica", "Gosta de Química"),
    ("Gosta_Arte_Design", "Gosta de Arte e Design"),
    ("Gosta_Comunicacao", "Gosta de Comunicação"),
    ("Gosta_Negocios", "Gosta de Negócios"),
    ("Gosta_Historia", "Gosta de História"),
    ("Gosta_Geografia", "Gosta de Geografia"),
]
DEFAULT_FORM_DATA = {
    "Idade": 18,
    "Curso_Tecnico": "Sim",
    "Anos_Para_Formar": 4,
    "Gosta_Matematica": 3,
    "Gosta_Programacao": 3,
    "Gosta_Biologia": 3,
    "Gosta_Fisica": 3,
    "Gosta_Quimica": 3,
    "Gosta_Arte_Design": 3,
    "Gosta_Comunicacao": 3,
    "Gosta_Negocios": 3,
    "Gosta_Historia": 3,
    "Gosta_Geografia": 3,
}


class PredictionRequest(BaseModel):
    """Schema de entrada do endpoint de predicao."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "Idade": 45,
                "Curso_Tecnico": "Sim",
                "Anos_Para_Formar": 7,
                "Gosta_Matematica": 1,
                "Gosta_Programacao": 4,
                "Gosta_Biologia": 2,
                "Gosta_Fisica": 3,
                "Gosta_Quimica": 5,
                "Gosta_Arte_Design": 3,
                "Gosta_Comunicacao": 1,
                "Gosta_Negocios": 1,
                "Gosta_Historia": 5,
                "Gosta_Geografia": 1,
            }
        }
    )

    Idade: int = Field(ge=14, le=100, description="Idade do estudante. Intervalo aceito: 14 a 100.")
    Curso_Tecnico: str = Field(
        description="Se o estudante possui curso tecnico. Valores aceitos: 'Sim' ou 'Nao'/'Não'."
    )
    Anos_Para_Formar: int = Field(
        ge=1,
        le=15,
        description="Quantidade estimada de anos para concluir a graduacao. Intervalo aceito: 1 a 15.",
    )
    Gosta_Matematica: int = Field(ge=1, le=5, description="Nivel de afinidade com matematica, de 1 a 5.")
    Gosta_Programacao: int = Field(ge=1, le=5, description="Nivel de afinidade com programacao, de 1 a 5.")
    Gosta_Biologia: int = Field(ge=1, le=5, description="Nivel de afinidade com biologia, de 1 a 5.")
    Gosta_Fisica: int = Field(ge=1, le=5, description="Nivel de afinidade com fisica, de 1 a 5.")
    Gosta_Quimica: int = Field(ge=1, le=5, description="Nivel de afinidade com quimica, de 1 a 5.")
    Gosta_Arte_Design: int = Field(ge=1, le=5, description="Nivel de afinidade com arte e design, de 1 a 5.")
    Gosta_Comunicacao: int = Field(ge=1, le=5, description="Nivel de afinidade com comunicacao, de 1 a 5.")
    Gosta_Negocios: int = Field(ge=1, le=5, description="Nivel de afinidade com negocios, de 1 a 5.")
    Gosta_Historia: int = Field(ge=1, le=5, description="Nivel de afinidade com historia, de 1 a 5.")
    Gosta_Geografia: int = Field(ge=1, le=5, description="Nivel de afinidade com geografia, de 1 a 5.")

    @field_validator("Curso_Tecnico", mode="before")
    @classmethod
    def normalize_curso_tecnico(cls, value: str) -> str:
        """Aceita pequenas variacoes textuais e padroniza a categoria."""
        return PredictorService.normalize_course_tecnico(value)


class PredictionResponse(BaseModel):
    """Schema de resposta do endpoint de predicao."""

    prediction: str = Field(description="Graduacao indicada pelo modelo.")
    probability: float = Field(description="Probabilidade estimada da classe prevista, em percentual de 0 a 100.")
    model_name: str = Field(description="Nome do modelo carregado pela API.")


class HealthResponse(BaseModel):
    """Schema de resposta do endpoint de saude."""

    status: str = Field(description="Estado geral da API.")
    model_loaded: bool = Field(description="Indica se o modelo foi carregado com sucesso.")
    preprocess_loaded: bool = Field(description="Indica se o preprocessador foi carregado com sucesso.")
    model_name: str = Field(description="Nome do modelo ativo.")
    model_variant: str = Field(description="Variante do modelo selecionada por configuracao.")
    model_path: str = Field(description="Caminho do artefato escolhido para a API.")
    error: str | None = Field(default=None, description="Mensagem de erro de carga, quando existir.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Carrega os artefatos antes da API comecar a atender requests."""
    predictor = PredictorService()
    predictor.load()
    app.state.predictor = predictor
    yield


app = FastAPI(
    title="API de Predicao de Graduacao",
    description=(
        "API local para inferencia do modelo treinado no projeto. "
        "A documentacao interativa esta disponivel no Swagger."
    ),
    version="1.0.0",
    lifespan=lifespan,
)
app.mount("/reports/figures", StaticFiles(directory=REPORTS_DIR / "figures"), name="report-figures")


def get_predictor(request: Request) -> PredictorService:
    """Recupera a instancia compartilhada do helper de inferencia."""
    return request.app.state.predictor


def render_home(
    request: Request,
    predictor: PredictorService,
    form_data: dict[str, int | str] | None = None,
    result: PredictionResponse | None = None,
    error_message: str | None = None,
    status_code: int = status.HTTP_200_OK,
) -> HTMLResponse:
    """Renderiza a pagina principal com formulario, status e resultado."""
    template_context = {
        "request": request,
        "educational_message": EDUCATIONAL_MESSAGE,
        "health": predictor.health_payload(),
        "form_data": form_data or DEFAULT_FORM_DATA,
        "result": result,
        "error_message": error_message,
        "preference_fields": [{"name": name, "label": label} for name, label in PREFERENCE_FIELDS],
        "report_links": REPORT_LINKS,
    }
    return TEMPLATES.TemplateResponse("index.html", template_context, status_code=status_code)


def run_prediction(payload: PredictionRequest, predictor: PredictorService) -> PredictionResponse:
    """Executa a predicao usando a mesma logica para JSON e formulario."""
    if not predictor.ready:
        raise HTTPException(status_code=503, detail="Artefatos do modelo nao estao disponiveis.")

    try:
        result = predictor.predict(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return PredictionResponse(
        prediction=result.prediction,
        probability=round(result.probability * 100, 2),
        model_name=result.model_name,
    )


def serve_report(filename: str, report_label: str) -> FileResponse:
    """Serve um relatorio HTML ja gerado pelo pipeline."""
    report_path = REPORTS_DIR / filename
    if not report_path.exists():
        raise HTTPException(status_code=404, detail=f"Relatorio de {report_label} nao encontrado.")

    return FileResponse(report_path, media_type="text/html")


@app.get("/", response_class=HTMLResponse, tags=["Geral"])
def read_root(request: Request) -> HTMLResponse:
    """Exibe a interface web principal do questionario."""
    predictor = get_predictor(request)
    status_code = status.HTTP_200_OK if predictor.ready else status.HTTP_503_SERVICE_UNAVAILABLE
    error_message = None if predictor.ready else predictor.load_error or "Modelo indisponivel no momento."
    return render_home(request=request, predictor=predictor, error_message=error_message, status_code=status_code)


@app.get("/health", response_model=HealthResponse, tags=["Geral"])
def health_check(request: Request, response: Response) -> HealthResponse:
    """Informa o estado da aplicacao e dos artefatos carregados."""
    predictor = get_predictor(request)
    if not predictor.ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthResponse(**predictor.health_payload())


@app.get("/reports/eda", tags=["Relatorios"])
def read_eda_report() -> FileResponse:
    """Exibe o relatorio HTML da etapa de EDA."""
    return serve_report(filename="eda.html", report_label="EDA")


@app.get("/reports/preprocess", tags=["Relatorios"])
def read_preprocess_report() -> FileResponse:
    """Exibe o relatorio HTML da etapa de preprocessamento."""
    return serve_report(filename="preprocess.html", report_label="preprocessamento")


@app.get("/reports/model", tags=["Relatorios"])
def read_model_report() -> FileResponse:
    """Exibe o relatorio HTML da etapa de treinamento."""
    return serve_report(filename="model_report.html", report_label="treinamento")


@app.post("/predict", response_model=PredictionResponse, tags=["Predicao"])
def predict(payload: PredictionRequest, request: Request) -> PredictionResponse:
    """Executa uma predicao para um unico registro bruto em formato JSON."""
    predictor = get_predictor(request)
    return run_prediction(payload=payload, predictor=predictor)


@app.post("/web/predict", response_class=HTMLResponse, tags=["Web"])
def predict_from_form(
    request: Request,
    Idade: int = Form(...),
    Curso_Tecnico: str = Form(...),
    Anos_Para_Formar: int = Form(...),
    Gosta_Matematica: int = Form(...),
    Gosta_Programacao: int = Form(...),
    Gosta_Biologia: int = Form(...),
    Gosta_Fisica: int = Form(...),
    Gosta_Quimica: int = Form(...),
    Gosta_Arte_Design: int = Form(...),
    Gosta_Comunicacao: int = Form(...),
    Gosta_Negocios: int = Form(...),
    Gosta_Historia: int = Form(...),
    Gosta_Geografia: int = Form(...),
) -> HTMLResponse:
    """Processa o formulario da interface web e renderiza o resultado na mesma pagina."""
    predictor = get_predictor(request)
    form_data = {
        "Idade": Idade,
        "Curso_Tecnico": Curso_Tecnico,
        "Anos_Para_Formar": Anos_Para_Formar,
        "Gosta_Matematica": Gosta_Matematica,
        "Gosta_Programacao": Gosta_Programacao,
        "Gosta_Biologia": Gosta_Biologia,
        "Gosta_Fisica": Gosta_Fisica,
        "Gosta_Quimica": Gosta_Quimica,
        "Gosta_Arte_Design": Gosta_Arte_Design,
        "Gosta_Comunicacao": Gosta_Comunicacao,
        "Gosta_Negocios": Gosta_Negocios,
        "Gosta_Historia": Gosta_Historia,
        "Gosta_Geografia": Gosta_Geografia,
    }

    try:
        payload = PredictionRequest(**form_data)
        result = run_prediction(payload=payload, predictor=predictor)
        return render_home(request=request, predictor=predictor, form_data=form_data, result=result)
    except ValidationError as exc:
        error_message = "; ".join(error["msg"] for error in exc.errors())
        return render_home(
            request=request,
            predictor=predictor,
            form_data=form_data,
            error_message=error_message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    except HTTPException as exc:
        return render_home(
            request=request,
            predictor=predictor,
            form_data=form_data,
            error_message=str(exc.detail),
            status_code=exc.status_code,
        )
