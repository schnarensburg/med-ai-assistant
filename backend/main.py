import sys
from pathlib import Path
import logging

from fastapi import FastAPI
from pydantic import BaseModel

# Add project root to sys.path (nur einmal!)
project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    print(f"➕ Adding project root to sys.path: {project_root}")
    sys.path.append(project_root)

from backend.logic.router_engine_simple import RouterEngine
from backend.logic.interaction_logger import get_last_user_logs, save_log
from backend.logging_config import setup_logger

setup_logger()

app = FastAPI()
router = RouterEngine(mode="warning", hf_token=None)

@app.get("/")
async def root():
    return {"message": "Medical AI Assistant Backend is running!", "status": "OK"}

class ChatRequest(BaseModel):
    prompt: str
    user_id: str = "user_1"

class ChatResponse(BaseModel):
    response: str
    state: str
    number_of_prompts: int

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    logs = get_last_user_logs(req.user_id, n=1000)
    number_of_prompts = len(logs)
    response, state = router.route(req.prompt, user_id=req.user_id)
    
    save_log(
        prompt=req.prompt,
        response=response,
        decision=state,
        interaction_type="chat_endpoint",
        number_of_prompts=number_of_prompts,
        user_id=req.user_id
    )
    
    return ChatResponse(response=response, state=state, number_of_prompts=number_of_prompts)