# backend/logger.py

import json
import time
from pathlib import Path

LOG_PATH = Path(__file__).parent / "logs.jsonl"

def log_interaction(prompt: str, user_id: str = "user_1"):
    entry = {
        "timestamp": time.time(),
        "user_id": user_id,
        "prompt": prompt
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
