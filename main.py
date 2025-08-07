from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import traceback
import os

from ai_engine.drones.drone_generator import generate_drone
from ai_engine.workers.worker_pool import evaluate_model
from ai_engine.queen.queen import select_best_model
from ai_engine.memory.hivememory import log_generation_result
from cors_config import setup_cors

app = FastAPI(
    title="BeeMind API",
    description="Evolutionary AI system inspired by bee colony dynamics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Strategic CORS setup for api.beemind.dev
app = setup_cors(app)

@app.get("/")
def root():
    return {"message": "BeeMind API is running!", "version": "1.0.0"}

@app.get("/health")
def health_check():
    """Health check endpoint for load balancer and monitoring"""
    return {
        "status": "healthy", 
        "service": "BeeMind",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/api/health")
def api_health_check():
    """Alternative health endpoint for nginx routing"""
    return {
        "status": "healthy", 
        "service": "BeeMind API",
        "timestamp": pd.Timestamp.now().isoformat()
    }

@app.options("/{path:path}")
def options_handler(path: str):
    """Handle preflight OPTIONS requests for CORS"""
    return {"message": "OK"}

class DatasetInput(BaseModel):
    data: list
    columns: list
    label_index: int

@app.post("/generate")
def generate_best_model(input_data: DatasetInput):
    try:
        print(f"Received data: {len(input_data.data)} rows, {len(input_data.columns)} columns")
        
        # Create DataFrame
        df = pd.DataFrame(input_data.data, columns=input_data.columns)
        label_col = input_data.columns[input_data.label_index]
        X = df.drop(columns=[label_col])
        y = df[label_col]
        
        print(f"Features shape: {X.shape}, Labels shape: {y.shape}")
        print(f"Unique labels: {y.unique()}")
        
        # Generate and evaluate drones
        drone_results = []
        for i in range(5):
            try:
                print(f"Generating drone {i+1}/5...")
                model, metadata = generate_drone()
                print(f"Generated {metadata['type']} model")
                
                result = evaluate_model(model, X, y)
                print(f"Evaluation result: ROC AUC={result['roc_auc']:.3f}, F1={result['f1']:.3f}")
                drone_results.append(result)
            except Exception as e:
                print(f"Error with drone {i+1}: {e}")
                continue
        
        if not drone_results:
            return {
                "error": "No drones could be evaluated successfully",
                "selected_model": "None",
                "roc_auc": 0.0,
                "f1_score": 0.0,
                "params": {}
            }
        
        # Select best model
        best = select_best_model(drone_results)
        print(f"Best model: {best['metadata']['type']} with ROC AUC: {best['roc_auc']:.3f}")
        
        # Log result
        try:
            log_generation_result(best)
        except Exception as e:
            print(f"Logging failed: {e}")
        
        return {
            "selected_model": best["metadata"]["type"],
            "roc_auc": best["roc_auc"],
            "f1_score": best["f1"],
            "params": best["metadata"]["params"],
            "total_drones": len(drone_results)
        }
        
    except Exception as e:
        print(f"Critical error in generate_best_model: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": "BeeMind Generation Error",
                "message": "Failed to generate and evaluate drone models"
            }
        )
