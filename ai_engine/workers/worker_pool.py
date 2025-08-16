import logging
from typing import Dict, Any, Tuple
from datetime import datetime
from sklearn.metrics import roc_auc_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import numpy as np
import math
import pandas as pd
from ..exceptions import ModelEvaluationError, DataValidationError, handle_exception, log_operation

logger = logging.getLogger(__name__)

def validate_input_data(X, y) -> None:
    """Validate input data for model evaluation"""
    try:
        # Check if X and y are not empty
        if X is None or y is None:
            raise DataValidationError("Input data X or y is None")
        
        # Convert to numpy arrays if needed
        if not isinstance(X, (np.ndarray, pd.DataFrame)):
            X = np.array(X)
        if not isinstance(y, (np.ndarray, pd.Series)):
            y = np.array(y)
        
        # Check shapes
        if len(X) == 0 or len(y) == 0:
            raise DataValidationError("Input data is empty")
        
        if len(X) != len(y):
            raise DataValidationError(f"X and y have different lengths: X={len(X)}, y={len(y)}")
        
        # Check for NaN values
        if np.isnan(X).any():
            raise DataValidationError("X contains NaN values")
        if np.isnan(y).any():
            raise DataValidationError("y contains NaN values")
        
        # Check for infinite values
        if np.isinf(X).any():
            raise DataValidationError("X contains infinite values")
        if np.isinf(y).any():
            raise DataValidationError("y contains infinite values")
        
        logger.info(f"Data validation passed: X shape={X.shape}, y unique values={len(np.unique(y))}")
        
    except Exception as e:
        if isinstance(e, DataValidationError):
            raise
        raise DataValidationError(f"Data validation failed: {str(e)}")

@handle_exception
def evaluate_model(model, X, y, test_size=0.2, random_state=42) -> Dict[str, Any]:
    """Evaluate a model with proper error handling and logging"""
    log_operation("evaluate_model", {
        "model_type": type(model).__name__,
        "data_shape": X.shape if hasattr(X, 'shape') else len(X),
        "test_size": test_size
    })
    
    try:
        # Validate input data
        validate_input_data(X, y)
        
        # Ensure we have enough data
        if len(X) < 4:
            logger.warning("Insufficient data for evaluation (less than 4 samples)")
            return {
                "model": model,
                "roc_auc": 0.0,
                "f1": 0.0,
                "metadata": {
                    "type": type(model).__name__,
                    "params": model.get_params(),
                    "error": "Insufficient data"
                }
            }
        
        # Encode labels
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        
        # Check if we have enough classes
        unique_classes = np.unique(y_encoded)
        if len(unique_classes) < 2:
            logger.warning(f"Insufficient classes for evaluation: {len(unique_classes)} class(es)")
            return {
                "model": model,
                "roc_auc": 0.0,
                "f1": 0.0,
                "metadata": {
                    "type": type(model).__name__,
                    "params": model.get_params(),
                    "error": f"Insufficient classes: {len(unique_classes)}"
                }
            }
        
        # Split data with stratification if possible
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=test_size, random_state=random_state, 
                stratify=y_encoded
            )
        except ValueError:
            # Fallback to non-stratified split if stratification fails
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=test_size, random_state=random_state
            )
        
        # Ensure test set has data
        if len(X_test) == 0 or len(y_test) == 0:
            logger.warning("Empty test set after data split")
            return {
                "model": model,
                "roc_auc": 0.0,
                "f1": 0.0,
                "metadata": {
                    "type": type(model).__name__,
                    "params": model.get_params(),
                    "error": "Empty test set"
                }
            }
        
        # Train model
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        # Calculate ROC AUC
        roc = 0.0
        try:
            if hasattr(model, 'predict_proba'):
                y_proba = model.predict_proba(X_test)
                if len(unique_classes) == 2:
                    # Binary classification
                    roc = roc_auc_score(y_test, y_proba[:, 1])
                else:
                    # Multi-class classification - use one-vs-rest approach
                    from sklearn.preprocessing import label_binarize
                    y_test_bin = label_binarize(y_test, classes=unique_classes)
                    if y_test_bin.shape[1] == 1:
                        # Edge case: only one class in test set
                        roc = 0.5
                    else:
                        roc = roc_auc_score(y_test_bin, y_proba, multi_class='ovr', average='weighted')
        except Exception as e:
            logger.warning(f"ROC AUC calculation failed: {e}")
            roc = 0.0
        
        # Handle NaN/inf values
        if math.isnan(roc) or math.isinf(roc):
            roc = 0.0
        
        # Calculate F1 score
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
        if math.isnan(f1) or math.isinf(f1):
            f1 = 0.0
        
        result = {
            "model": model,
            "roc_auc": float(roc),
            "f1": float(f1),
            "metadata": {
                "type": type(model).__name__,
                "params": model.get_params(),
                "evaluation_timestamp": datetime.utcnow().isoformat()
            }
        }
        
        log_operation("evaluate_model", {
            "step": "completed",
            "model_type": result["metadata"]["type"],
            "roc_auc": result["roc_auc"],
            "f1_score": result["f1"]
        })
        
        return result
        
    except Exception as e:
        logger.error(f"Model evaluation failed: {e}")
        raise ModelEvaluationError(
            f"Model evaluation failed: {str(e)}",
            model_type=type(model).__name__,
            dataset_info={"X_shape": X.shape if hasattr(X, 'shape') else len(X), "y_unique": len(np.unique(y))}
        )
