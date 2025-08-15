import json
import uuid
import os
from datetime import datetime
from pathlib import Path

# Define where session logs will be stored (backend/data/sessions)
# Creates directory if it doesn't exist
SESSIONS_DIR = Path(__file__).resolve().parents[2] / "backend" / "data" / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

def save_log(prompt, response, decision, interaction_type, number_of_prompts, user_id):
    """
    Saves an interaction log as JSON file with timestamp and unique session ID.
    Args:
        prompt: User's input text
        response: System's generated response
        decision: User's final decision/action
        interaction_type: Type of interaction (e.g., "diagnosis", "feedback")
        number_of_prompts: Count of previous prompts in session
        user_id: Identifier for the current user
    """
    log = {
        "session_id": str(uuid.uuid4()),  # Unique identifier for this session   
        "timestamp": datetime.now().isoformat(), 
        "prompt": prompt,
        "response": response,
        "user_decision": decision,
        "interaction_type": interaction_type,
        "number of previous prompts": number_of_prompts,
        "user_id": user_id,  # For filtering user-specific logs
    }

    # Create filename with timestamp and shortened session ID
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    filename = f"{timestamp_str}_session_{log['session_id'][:8]}.json"

    with open(SESSIONS_DIR / filename, "w") as f:
        json.dump(log, f, indent=2)

def get_last_user_logs(user_id, n=1):
    """
    Retrieves the last n logs for a specific user.
    Args:
        user_id: User to filter logs for
        n: Number of recent logs to retrieve (default: 1)
    Returns:
        List of log entries in chronological order (oldest first)
    """
    logs = []
    # Sort files by modification time (newest first)
    for file in sorted(os.listdir(SESSIONS_DIR), key=lambda x: os.path.getmtime(os.path.join(SESSIONS_DIR, x)), reverse=True):
        with open(os.path.join(SESSIONS_DIR, file)) as f:
            entry = json.load(f)
            if entry.get("user_id") == user_id:
                logs.append(entry)
            if len(logs) == n:
                break
    return logs[::-1]  # Reverse to return oldest-first
