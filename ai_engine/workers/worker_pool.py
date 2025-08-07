from sklearn.metrics import roc_auc_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import numpy as np
import math

def evaluate_model(model, X, y, test_size=0.2, random_state=42):
    try:
        # Ensure we have enough data
        if len(X) < 4:
            return {
                "model": model,
                "roc_auc": 0.0,
                "f1": 0.0,
                "metadata": {
                    "type": type(model).__name__,
                    "params": model.get_params()
                }
            }
        
        # Encode labels
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        
        # Check if we have enough classes
        unique_classes = np.unique(y_encoded)
        if len(unique_classes) < 2:
            return {
                "model": model,
                "roc_auc": 0.0,
                "f1": 0.0,
                "metadata": {
                    "type": type(model).__name__,
                    "params": model.get_params()
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
            return {
                "model": model,
                "roc_auc": 0.0,
                "f1": 0.0,
                "metadata": {
                    "type": type(model).__name__,
                    "params": model.get_params()
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
            print(f"ROC AUC calculation failed: {e}")
            roc = 0.0
        
        # Handle NaN/inf values
        if math.isnan(roc) or math.isinf(roc):
            roc = 0.0
        
        # Calculate F1 score
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
        if math.isnan(f1) or math.isinf(f1):
            f1 = 0.0
        
        return {
            "model": model,
            "roc_auc": float(roc),
            "f1": float(f1),
            "metadata": {
                "type": type(model).__name__,
                "params": model.get_params()
            }
        }
        
    except Exception as e:
        print(f"Model evaluation failed: {e}")
        return {
            "model": model,
            "roc_auc": 0.0,
            "f1": 0.0,
            "metadata": {
                "type": type(model).__name__,
                "params": model.get_params()
            }
        }
