import random
import logging
from typing import Tuple, Any, Dict
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from ..exceptions import ModelGenerationError, handle_exception, log_operation
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import settings

logger = logging.getLogger(__name__)

def generate_random_model() -> Any:
    """Generate a random ML model with basic hyperparameters"""
    try:
        model_type = random.choice(settings.MODEL_TYPES)
        
        if model_type == "xgb":
            model = XGBClassifier(
                n_estimators=random.randint(settings.XGB_N_ESTIMATORS_MIN, settings.XGB_N_ESTIMATORS_MAX),
                max_depth=random.randint(settings.XGB_MAX_DEPTH_MIN, settings.XGB_MAX_DEPTH_MAX),
                learning_rate=random.uniform(settings.XGB_LEARNING_RATE_MIN, settings.XGB_LEARNING_RATE_MAX),
                random_state=settings.RANDOM_STATE
            )
        elif model_type == "rf":
            model = RandomForestClassifier(
                n_estimators=random.randint(settings.RF_N_ESTIMATORS_MIN, settings.RF_N_ESTIMATORS_MAX),
                max_depth=random.randint(settings.RF_MAX_DEPTH_MIN, settings.RF_MAX_DEPTH_MAX),
                min_samples_split=random.randint(settings.RF_MIN_SAMPLES_SPLIT_MIN, settings.RF_MIN_SAMPLES_SPLIT_MAX),
                random_state=settings.RANDOM_STATE
            )
        elif model_type == "gb":
            model = GradientBoostingClassifier(
                n_estimators=random.randint(settings.GB_N_ESTIMATORS_MIN, settings.GB_N_ESTIMATORS_MAX),
                max_depth=random.randint(settings.GB_MAX_DEPTH_MIN, settings.GB_MAX_DEPTH_MAX),
                learning_rate=random.uniform(settings.GB_LEARNING_RATE_MIN, settings.GB_LEARNING_RATE_MAX),
                random_state=settings.RANDOM_STATE
            )
        else:  # lr
            model = LogisticRegression(
                C=random.uniform(settings.LR_C_MIN, settings.LR_C_MAX),
                max_iter=settings.LR_MAX_ITER,
                random_state=settings.RANDOM_STATE
            )
        
        logger.info(f"Generated {model_type.upper()} model with params: {model.get_params()}")
        return model
        
    except Exception as e:
        raise ModelGenerationError(
            f"Failed to generate random model: {str(e)}",
            model_type=model_type if 'model_type' in locals() else None
        )

@handle_exception
def generate_drone() -> Tuple[Any, Dict[str, Any]]:
    """Generate a drone (ML model) with metadata"""
    log_operation("generate_drone", {"step": "starting"})
    
    try:
        model = generate_random_model()
        metadata = {
            "type": type(model).__name__,
            "params": model.get_params(),
            "generation_timestamp": log_operation.__name__
        }
        
        log_operation("generate_drone", {
            "step": "completed",
            "model_type": metadata["type"],
            "params_count": len(metadata["params"])
        })
        
        return model, metadata
        
    except Exception as e:
        raise ModelGenerationError(
            f"Failed to generate drone: {str(e)}",
            model_type=type(model).__name__ if 'model' in locals() else None
        )
