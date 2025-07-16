# router_engine_full.py

"""
This script combines:
1. Your existing Cognitive State Analyzer (CSA)
2. A RouterEngine that maps cognitive states to tailored system prompts
3. Integration with Meditron (a local HuggingFace model)

Usage:
    HF_TOKEN=your_token python router_engine_full.py "your user prompt here"
"""

import os
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
import sys
from dotenv import load_dotenv

# --- Load Hugging Face token ---
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# --- 1. Cognitive State Analyzer (CSA) ---
LABELS = [
    "Kreativer Flow",        # Exploration + Constructive
    "Zielloses Erkunden",    # Exploration + Detrimental
    "Vertiefendes Arbeiten", # Exploitation + Constructive
    "Tunneldenken"           # Exploitation + Detrimental
]

# Load sentence transformer model once
embedding_model = SentenceTransformer("all-MiniLM-L6-v2", use_auth_token=HF_TOKEN)
label_embeddings = embedding_model.encode(LABELS, normalize_embeddings=True)

def classify_prompt(prompt: str) -> str:
    """
    Embeds the user prompt and compares it with predefined labels using cosine similarity.
    Returns the label with the highest similarity.
    """
    prompt_emb = embedding_model.encode([prompt], normalize_embeddings=True)[0]
    sims = np.dot(label_embeddings, prompt_emb)
    best_idx = int(np.argmax(sims))
    return LABELS[best_idx]

# --- 2. Router Engine ---
STATE_TO_SYSTEM_PROMPT = {
    "Kreativer Flow":        "You are a creative medical assistant. Brainstorm innovative and lateral solutions.",
    "Zielloses Erkunden":    "You are a concise assistant. Gently help the user clarify their medical question.",
    "Vertiefendes Arbeiten": "You are a focused assistant. Provide detailed, structured, in-depth medical information.",
    "Tunneldenken":          "You are a reflective assistant. Help the user consider alternative diagnoses or perspectives."
}

class RouterEngine:
    def __init__(self, model_id="epfl-llm/meditron-7b", hf_token=None, use_gpu=False):
        """
        Initializes the Router Engine with a Meditron model.
        :param model_id: Local path or Hugging Face model ID.
        :param hf_token: Hugging Face access token.
        :param use_gpu: Whether to use GPU (if available).
        """
        device = 0 if use_gpu and torch.cuda.is_available() else -1

        print("[RouterEngine] Loading Meditron model...")
        tokenizer = AutoTokenizer.from_pretrained(model_id, token=hf_token)
        model = AutoModelForCausalLM.from_pretrained(model_id, token=hf_token)

        self.generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device=device,
            max_new_tokens=300,
            do_sample=False
        )

    def route(self, user_input: str) -> str:
        """
        Runs the full pipeline: CSA → prompt mapping → Meditron.
        :param user_input: Original user prompt.
        :return: Generated answer from Meditron.
        """
        # 1. Detect cognitive state
        state = classify_prompt(user_input)
        print(f"[CSA] Detected state: {state}")

        # 2. Get system prompt via if-elif-else
        if state == "Kreativer Flow":
            system_prompt = "You are a creative medical assistant. Brainstorm innovative and lateral solutions."
        elif state == "Zielloses Erkunden":
            system_prompt = "You are a concise assistant. Gently help the user clarify their medical question."
        elif state == "Vertiefendes Arbeiten":
            system_prompt = "You are a focused assistant. Provide detailed, structured, in-depth medical information."
        elif state == "Tunneldenken":
            system_prompt = "You are a reflective assistant. Help the user consider alternative diagnoses or perspectives."
        else:
            system_prompt = "You are a helpful medical assistant."

        print(f"[RouterEngine] Using system prompt: {system_prompt}")

        # 3. Build final prompt
        full_prompt = f"{system_prompt}\n\nUser: {user_input}\nAssistant:"

        # 4. Generate Meditron response
        output = self.generator(full_prompt)[0]["generated_text"]
        response = output[len(full_prompt):].strip()
        return response


# --- 3. CLI Entry Point ---

if __name__ == "__main__":
    hf_token = HF_TOKEN

    router = RouterEngine(hf_token=hf_token)

    print("\n💬 Type your medical questions. Type 'exit' to stop.\n")

    while True:
        user_prompt = input("🧑‍⚕️ You: ")
        if user_prompt.lower() in {"exit"}:
            print("👋 Exiting Meditron chat.")
            break

        response = router.route(user_prompt)
        print("\n🤖 Meditron:", response)
        print("-" * 50)
