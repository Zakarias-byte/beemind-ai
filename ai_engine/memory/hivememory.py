import json
import os
from datetime import datetime

HIVE_LOG_FILE = "hivememory_log.json"

def log_generation_result(result):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "type": result["metadata"]["type"],
        "roc_auc": result["roc_auc"],
        "f1": result["f1"],
        "params": result["metadata"]["params"]
    }

    if not os.path.exists(HIVE_LOG_FILE):
        with open(HIVE_LOG_FILE, "w") as f:
            json.dump([log_entry], f, indent=2)
    else:
        with open(HIVE_LOG_FILE, "r+") as f:
            data = json.load(f)
            data.append(log_entry)
            f.seek(0)
            json.dump(data, f, indent=2)
