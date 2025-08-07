#!/usr/bin/env python3
"""
BeeMind HTTP API - Robust implementation using working components
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import json
import logging
import time
from typing import List, Dict, Any
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="🐝 BeeMind API",
    description="Evolutionary AI system inspired by bee colony dynamics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DatasetInput(BaseModel):
    data: List[List[float]]
    columns: List[str]
    label_index: int

class BeeMindResponse(BaseModel):
    selected_model: str
    roc_auc: float
    f1_score: float
    params: Dict[str, Any]
    total_drones: int
    generation_time: float
    status: str

def run_beemind_generation(data, columns, label_index):
    """Core BeeMind generation logic - isolated from HTTP context"""
    try:
        # Import components locally to avoid HTTP context issues
        from ai_engine.drones.drone_generator import generate_drone
        from ai_engine.workers.worker_pool import evaluate_model
        from ai_engine.queen.queen import select_best_model
        from ai_engine.memory.hivememory import log_generation_result
        
        logger.info("🐝 Starting BeeMind generation...")
        
        # Create DataFrame
        df = pd.DataFrame(data, columns=columns)
        label_col = columns[label_index]
        X = df.drop(columns=[label_col])
        y = df[label_col]
        
        logger.info(f"📊 Data: X{X.shape}, y{y.shape}, classes: {y.unique()}")
        
        # Generate and evaluate drones
        drone_results = []
        for i in range(5):
            try:
                logger.info(f"🤖 Generating drone {i+1}/5...")
                model, metadata = generate_drone()
                
                logger.info(f"👷 Evaluating {metadata['type']}...")
                result = evaluate_model(model, X, y)
                
                drone_results.append(result)
                logger.info(f"✅ Drone {i+1}: {metadata['type']} - ROC AUC={result['roc_auc']:.3f}")
                
            except Exception as e:
                logger.warning(f"⚠️ Drone {i+1} failed: {e}")
                continue
        
        if not drone_results:
            raise Exception("No drones succeeded")
        
        # Select best model
        best = select_best_model(drone_results)
        logger.info(f"👑 Best model: {best['metadata']['type']} with ROC AUC: {best['roc_auc']:.3f}")
        
        # Log result
        try:
            log_generation_result(best)
            logger.info("🧠 Result logged to HiveMemory")
        except Exception as e:
            logger.warning(f"⚠️ Logging failed: {e}")
        
        return {
            "selected_model": best["metadata"]["type"],
            "roc_auc": float(best["roc_auc"]),
            "f1_score": float(best["f1"]),
            "params": best["metadata"]["params"],
            "total_drones": len(drone_results),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"💥 Generation failed: {e}")
        raise e

@app.get("/")
def root():
    """Root endpoint - API status"""
    return {
        "message": "🐝 BeeMind API is running!",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": ["/generate", "/health", "/docs", "/hivememory"]
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Test component imports
        from ai_engine.drones.drone_generator import generate_drone
        from ai_engine.workers.worker_pool import evaluate_model
        from ai_engine.queen.queen import select_best_model
        from ai_engine.memory.hivememory import log_generation_result
        
        return {
            "status": "healthy",
            "service": "BeeMind",
            "components": {
                "drone_generator": "✅",
                "worker_pool": "✅", 
                "queen_selector": "✅",
                "hive_memory": "✅"
            },
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }

@app.get("/hivememory")
def get_hivememory():
    """Get HiveMemory logs"""
    try:
        with open("hivememory_log.json", "r") as f:
            logs = json.load(f)
        return {
            "status": "success",
            "total_entries": len(logs),
            "logs": logs[-10:]  # Return last 10 entries
        }
    except FileNotFoundError:
        return {
            "status": "success",
            "total_entries": 0,
            "logs": [],
            "message": "No logs found yet"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate", response_model=BeeMindResponse)
def generate_best_model(input_data: DatasetInput):
    """
    Generate and evaluate drone models, select the best one
    
    🐝 BeeMind Evolution Process:
    1. 🤖 Generate 5 random drone models (genetic diversity)
    2. 👷 Evaluate each drone on provided dataset (fitness test)
    3. 👑 Queen selects the best performing drone (natural selection)
    4. 🧠 Log evolution to HiveMemory (collective intelligence)
    5. 📊 Return best model's DNA and performance
    """
    start_time = time.time()
    
    try:
        logger.info(f"🔄 Processing generation request: {len(input_data.data)} rows, {len(input_data.columns)} columns")
        
        # Validate input
        if not input_data.data:
            raise HTTPException(status_code=400, detail="No data provided")
        
        if len(input_data.data) < 4:
            raise HTTPException(status_code=400, detail="Need at least 4 data points for training")
        
        if input_data.label_index >= len(input_data.columns):
            raise HTTPException(status_code=400, detail="Invalid label_index")
        
        # Run BeeMind generation
        result = run_beemind_generation(
            input_data.data, 
            input_data.columns, 
            input_data.label_index
        )
        
        generation_time = time.time() - start_time
        result["generation_time"] = generation_time
        
        logger.info(f"🎉 Generation completed in {generation_time:.2f}s")
        
        return BeeMindResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Critical error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": "BeeMind Generation Error",
                "message": "Failed to generate and evaluate drone models"
            }
        )

if __name__ == "__main__":
    logger.info("🚀 Starting BeeMind API server...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        access_log=True
    )
