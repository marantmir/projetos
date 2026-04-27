from fastapi import FastAPI, HTTPException
import pandas as pd
import joblib
from typing import List
from pydantic import BaseModel

class Carro(BaseModel):
    Marca: str
    #Modelo: str
    Ano: int
    Quilometragem: int
    #Cor: str
    #Cambio: str
    #Combustivel: str
    #Portas: int
    #idade_carro: int

app = FastAPI()

# Carregar modelo
model = joblib.load('lasso_best_full_model_pipeline.pkl')

@app.get("/")
def home():
    return {"status": "ok"}

@app.post("/forecast")
def forecast(data: List[Carro]):
    df = pd.DataFrame([item.dict() for item in data])
    #top10_features = ['Quilometragem', 'Ano', 'Marca_Toyota', 'Marca_Jeep', 'Marca_Honda',
    #    'Marca_Fiat', 'Marca_Renault', 'Marca_Volkswagen', 'Marca_Nissan',
    #    'Marca_Ford']
    
    
    # Fazer a previsão
    try:
        preds = model.predict(df)
        return {"forecast": preds.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer a previsão: {e}")