def select_best_model(drone_results):
    return max(drone_results, key=lambda d: d["roc_auc"])
