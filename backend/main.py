import sys
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel
from backend.logic.router_engine import RouterEngine
from backend.logic.interaction_logger import get_last_user_logs

# Projekt-Root hinzufügen, falls nicht enthalten
project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    print(f"➕ Adding project root to sys.path: {project_root}")
    sys.path.append(project_root)
# Add project root to sys.path
# sys.path.append(str(Path(__file__).resolve().parents[1]))
app = FastAPI()

class ChatRequest(BaseModel):
    prompt: str
    user_id: str = "user_1"

class ChatResponse(BaseModel):
    response: str
    state: str
    number_of_prompts: int

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    router = RouterEngine(hf_token=None, user_id=req.user_id)
    logs = get_last_user_logs(req.user_id, n=1000)
    number_of_prompts = len(logs)
    response, state = router.route(req.prompt, user_id=req.user_id)
    # Optionally: save_log(...) here if you want to log every interaction
    return ChatResponse(response=response, state=state, number_of_prompts=number_of_prompts)