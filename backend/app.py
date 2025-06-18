# backend/app.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.logger import log_interaction
from backend.chains.cognitive_state_analyzer_chain import classify_prompt
from backend.config import settings

app = FastAPI()

class ChatRequest(BaseModel):
    prompt: str
    user_id: str = "user_1"  # Standardwert zum Testen

class ChatResponse(BaseModel):
    answer: str


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    # 1. Logge die Interaktion
    log_interaction(req.prompt, req.user_id)

    # 2. Klassifikation
    category = classify_prompt(req.prompt)
    if not category:
        raise HTTPException(status_code=500, detail="Kategorisierung fehlgeschlagen")
    answer = f"Kategorisierte Anfrage: {category}"

    # 3. Routing, RAG...

    return ChatResponse(answer=answer)
