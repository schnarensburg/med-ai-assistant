# backend/config.py
import os
from dotenv import load_dotenv

# .env in Projekt-Root laden
load_dotenv()

class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    hf_hub_token: str = os.getenv("HF_HUB_TOKEN", "")

settings = Settings()
