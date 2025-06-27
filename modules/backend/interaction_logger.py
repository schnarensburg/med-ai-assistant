# modules/interaction_logger.py
import json
import uuid
from datetime import datetime
from pathlib import Path

def save_log(prompt, response, decision, interaction_type):
    log = {
        "session_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "response": response,
        "user_decision": decision,
        "interaction_type": interaction_type
    }
    Path("sessions").mkdir(exist_ok=True)
    with open(f"sessions/session_{log['session_id'][:8]}.json", "w") as f:
        json.dump(log, f, indent=2)
