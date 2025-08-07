"""
main.py
FastAPI-backend for å kjøre BeeMind AI-generasjon og returnere beste modell.
"""
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from ai_engine.drones.drone_generator import generate_drone
from ai_engine.workers.worker_pool import evaluate_model
from ai_engine.queen.queen import select_best_model
from ai_engine.memory.hivememory import log_generation_result

app = FastAPI(title="BeeMind API")

# Enkel datastruktur for demo
class DatasetInput(BaseModel):
    data: list  # List of lists (rows)
    columns: list  # List of column names
    label_index: int  # Index of the label column

@app.post("/generate")
def generate_best_model(input_data: DatasetInput):
    # Konverter data
    df = pd.DataFrame(input_data.data, columns=input_data.columns)
    label_col = input_data.columns[input_data.label_index]
    X = df.drop(columns=[label_col])
    y = df[label_col]

    # Generer og evaluer droner
    drone_results = []
    for _ in range(5):
        model, metadata = generate_drone()
        result = evaluate_model(model, X, y)
        drone_results.append(result)

    # Velg beste modell
    best = select_best_model(drone_results)

    # Logg
    log_generation_result(best)

    # Returner
    return {
        "selected_model": best["metadata"]["type"],
        "roc_auc": best["roc_auc"],
        "f1_score": best["f1"],
        "params": best["metadata"]["params"]
    }
