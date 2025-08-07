#!/usr/bin/env python3
"""
Advanced Drone Generator - More sophisticated AI model generation
"""

import random
import numpy as np
from sklearn.ensemble import (
    RandomForestClassifier, 
    GradientBoostingClassifier,
    ExtraTreesClassifier,
    AdaBoostClassifier
)
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

class AdvancedDroneGenerator:
    """
    Advanced drone generator with genetic-inspired parameter evolution
    """
    
    def __init__(self):
        self.model_types = [
            "random_forest",
            "gradient_boosting", 
            "extra_trees",
            "ada_boost",
            "logistic_regression",
            "ridge_classifier",
            "svc",
            "mlp_classifier",
            "gaussian_nb",
            "decision_tree"
        ]
        
        if XGBOOST_AVAILABLE:
            self.model_types.append("xgboost")
    
    def generate_random_hyperparameters(self, model_type):
        """Generate random hyperparameters for each model type"""
        
        if model_type == "random_forest":
            return {
                'n_estimators': random.choice([50, 100, 200, 300]),
                'max_depth': random.choice([3, 5, 7, 10, None]),
                'min_samples_split': random.choice([2, 5, 10]),
                'min_samples_leaf': random.choice([1, 2, 4]),
                'max_features': random.choice(['sqrt', 'log2', None]),
                'bootstrap': random.choice([True, False])
            }
        
        elif model_type == "gradient_boosting":
            return {
                'n_estimators': random.choice([50, 100, 200]),
                'learning_rate': random.choice([0.01, 0.1, 0.2, 0.3]),
                'max_depth': random.choice([3, 4, 5, 6]),
                'min_samples_split': random.choice([2, 5, 10]),
                'min_samples_leaf': random.choice([1, 2, 4]),
                'subsample': random.choice([0.8, 0.9, 1.0])
            }
        
        elif model_type == "extra_trees":
            return {
                'n_estimators': random.choice([50, 100, 200]),
                'max_depth': random.choice([3, 5, 7, None]),
                'min_samples_split': random.choice([2, 5, 10]),
                'min_samples_leaf': random.choice([1, 2, 4]),
                'max_features': random.choice(['sqrt', 'log2', None])
            }
        
        elif model_type == "ada_boost":
            return {
                'n_estimators': random.choice([50, 100, 200]),
                'learning_rate': random.choice([0.1, 0.5, 1.0, 1.5]),
                'algorithm': random.choice(['SAMME', 'SAMME.R'])
            }
        
        elif model_type == "logistic_regression":
            return {
                'C': random.choice([0.1, 1.0, 10.0, 100.0]),
                'penalty': random.choice(['l1', 'l2', 'elasticnet', None]),
                'solver': random.choice(['liblinear', 'lbfgs', 'saga']),
                'max_iter': random.choice([100, 200, 500, 1000])
            }
        
        elif model_type == "ridge_classifier":
            return {
                'alpha': random.choice([0.1, 1.0, 10.0, 100.0]),
                'solver': random.choice(['auto', 'svd', 'cholesky', 'lsqr', 'saga'])
            }
        
        elif model_type == "svc":
            return {
                'C': random.choice([0.1, 1.0, 10.0]),
                'kernel': random.choice(['linear', 'poly', 'rbf']),
                'gamma': random.choice(['scale', 'auto']),
                'probability': True  # Always enable for ROC AUC calculation
            }
        
        elif model_type == "mlp_classifier":
            return {
                'hidden_layer_sizes': random.choice([(50,), (100,), (50, 50), (100, 50)]),
                'activation': random.choice(['relu', 'tanh', 'logistic']),
                'solver': random.choice(['adam', 'lbfgs']),
                'alpha': random.choice([0.0001, 0.001, 0.01]),
                'learning_rate': random.choice(['constant', 'adaptive']),
                'max_iter': 500  # Fixed to avoid convergence warnings
            }
        
        elif model_type == "gaussian_nb":
            return {
                'var_smoothing': random.choice([1e-9, 1e-8, 1e-7, 1e-6])
            }
        
        elif model_type == "decision_tree":
            return {
                'max_depth': random.choice([3, 5, 7, 10, None]),
                'min_samples_split': random.choice([2, 5, 10]),
                'min_samples_leaf': random.choice([1, 2, 4]),
                'criterion': random.choice(['gini', 'entropy']),
                'max_features': random.choice(['sqrt', 'log2', None])
            }
        
        elif model_type == "xgboost" and XGBOOST_AVAILABLE:
            return {
                'n_estimators': random.choice([50, 100, 200]),
                'learning_rate': random.choice([0.01, 0.1, 0.2]),
                'max_depth': random.choice([3, 4, 5, 6]),
                'subsample': random.choice([0.8, 0.9, 1.0]),
                'colsample_bytree': random.choice([0.8, 0.9, 1.0])
            }
        
        return {}
    
    def create_model(self, model_type, params):
        """Create model instance with given parameters"""
        
        try:
            if model_type == "random_forest":
                return RandomForestClassifier(**params, random_state=42)
            
            elif model_type == "gradient_boosting":
                return GradientBoostingClassifier(**params, random_state=42)
            
            elif model_type == "extra_trees":
                return ExtraTreesClassifier(**params, random_state=42)
            
            elif model_type == "ada_boost":
                return AdaBoostClassifier(**params, random_state=42)
            
            elif model_type == "logistic_regression":
                # Handle solver compatibility
                if params.get('penalty') == 'l1' and params.get('solver') not in ['liblinear', 'saga']:
                    params['solver'] = 'liblinear'
                elif params.get('penalty') == 'elasticnet' and params.get('solver') != 'saga':
                    params['solver'] = 'saga'
                    params['l1_ratio'] = 0.5
                return LogisticRegression(**params, random_state=42)
            
            elif model_type == "ridge_classifier":
                return RidgeClassifier(**params, random_state=42)
            
            elif model_type == "svc":
                return SVC(**params, random_state=42)
            
            elif model_type == "mlp_classifier":
                return MLPClassifier(**params, random_state=42)
            
            elif model_type == "gaussian_nb":
                return GaussianNB(**params)
            
            elif model_type == "decision_tree":
                return DecisionTreeClassifier(**params, random_state=42)
            
            elif model_type == "xgboost" and XGBOOST_AVAILABLE:
                return XGBClassifier(**params, random_state=42, eval_metric='logloss')
            
            else:
                # Fallback to simple random forest
                return RandomForestClassifier(random_state=42)
                
        except Exception as e:
            print(f"⚠️ Failed to create {model_type} with params {params}: {e}")
            # Fallback to simple model
            return RandomForestClassifier(random_state=42)
    
    def generate_drone(self):
        """Generate a new drone with random model and hyperparameters"""
        
        # Select random model type
        model_type = random.choice(self.model_types)
        
        # Generate random hyperparameters
        params = self.generate_random_hyperparameters(model_type)
        
        # Create model
        model = self.create_model(model_type, params)
        
        # Create metadata
        metadata = {
            "type": type(model).__name__,
            "model_family": model_type,
            "params": model.get_params(),
            "generation_id": random.randint(1000, 9999),
            "drone_dna": {
                "base_type": model_type,
                "hyperparams": params
            }
        }
        
        return model, metadata

# Global instance for backward compatibility
advanced_generator = AdvancedDroneGenerator()

def generate_advanced_drone():
    """Generate an advanced drone - main interface function"""
    return advanced_generator.generate_drone()

# Backward compatibility
def generate_drone():
    """Generate drone - backward compatible interface"""
    return generate_advanced_drone()

if __name__ == "__main__":
    # Test the advanced drone generator
    print("🧪 Testing Advanced Drone Generator...")
    
    for i in range(5):
        model, metadata = generate_advanced_drone()
        print(f"🤖 Drone {i+1}: {metadata['type']} ({metadata['model_family']})")
        print(f"   DNA: {metadata['drone_dna']['base_type']}")
        print(f"   Generation ID: {metadata['generation_id']}")
        print()
