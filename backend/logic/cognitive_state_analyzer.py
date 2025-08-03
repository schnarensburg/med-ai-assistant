# tests/kognitive_state_analyzer.py
import os
import json
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM
import torch
from dotenv import load_dotenv

# --- Load Hugging Face token ---
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

SYSTEM_PROMPT_CSA = """
You are a Cognitive State Analyzer. Classify the user's input into one of these four cognitive states exactly:
1) Explorative Constructive: The user actively reflects, considers alternatives, asks for more information, or provides medical expertise to deepen understanding.
2) Explotative Detrimental: The user focuses on one diagnosis, provides medical expertise, or reviews your answer without exploring alternatives.
3) Exploitative Constructive: The user asks questions or explores superficially without medical reasoning or further relevant input.
4) Exploitative Detrimental: The user blindly follows suggestions without critical thinking, feedback, or additional data.
Only respond with one of these four labels exactly as above.
"""

MODEL_NAME_CSA = "google/flan-t5-large"

tokenizer_csa = AutoTokenizer.from_pretrained(MODEL_NAME_CSA, use_auth_token=HF_TOKEN)
model_csa = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME_CSA, use_auth_token=HF_TOKEN)

generator_csa = pipeline(
    "text2text-generation",
    model=model_csa,
    tokenizer=tokenizer_csa,
    device=0 if torch.cuda.is_available() else -1,
    max_new_tokens=16,
    clean_up_tokenization_spaces=True,
)

def classify_prompt_flan_t5(current_prompt: str, prev_states=None, prev_prompts=None) -> str:
    prev_states = prev_states or []
    prev_prompts = prev_prompts or []
    input_text = (
        SYSTEM_PROMPT_CSA.strip() +
        (f"\n\nPrevious user states: {', '.join(prev_states)}" if prev_states else "") +
        (f"\nPrevious user prompts: {', '.join(prev_prompts)}" if prev_prompts else "") +
        f"\n\nCurrent user input: {current_prompt}\nCognitive State:"
    )
    outputs = generator_csa(input_text)
    raw = outputs[0]["generated_text"].strip()
    label = raw.splitlines()[0]
    valid_labels = {
    "Explorative Constructive",
    "Exploitative Detrimental",
    "Exploitative Constructive",
    "Exploitative Detrimental"
}
    if label not in valid_labels:
        label = "Exploitative Detrimental"
    return label