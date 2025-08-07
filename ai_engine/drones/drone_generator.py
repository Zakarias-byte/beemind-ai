import random
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression

def generate_random_model():
    model_type = random.choice(["xgb", "rf", "gb", "lr"])
    if model_type == "xgb":
        return XGBClassifier()
    elif model_type == "rf":
        return RandomForestClassifier()
    elif model_type == "gb":
        return GradientBoostingClassifier()
    else:
        return LogisticRegression()

def generate_drone():
    model = generate_random_model()
    metadata = {
        "type": type(model).__name__,
        "params": model.get_params()
    }
    return model, metadata
