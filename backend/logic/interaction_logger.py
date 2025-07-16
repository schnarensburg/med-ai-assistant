# tests/interaction_logger.py
import json
import uuid
import os
from datetime import datetime
from pathlib import Path


SESSIONS_DIR = Path(__file__).resolve().parents[2] / "backend" / "data" / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

def save_log(prompt, response, decision, interaction_type, number_of_prompts, user_id):
    log = {
        "session_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "response": response,
        "user_decision": decision,
        "interaction_type": interaction_type,
        "number of previous prompts": number_of_prompts,
        "user_id": user_id,  # <-- NEU
    }

    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    with open(SESSIONS_DIR / f"session_{log['session_id'][:8]}.json", "w") as f:
        json.dump(log, f, indent=2)

def get_last_user_logs(user_id, n=1):
    logs = []
    for file in sorted(os.listdir(SESSIONS_DIR), key=lambda x: os.path.getmtime(os.path.join(SESSIONS_DIR, x)), reverse=True):
        with open(os.path.join(SESSIONS_DIR, file)) as f:
            entry = json.load(f)
            if entry.get("user_id") == user_id:
                logs.append(entry)
            if len(logs) == n:
                break
    return logs[::-1]
