import os
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM
import torch
from dotenv import load_dotenv

# --- Load Hugging Face token ---
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# --- 1. FLAN-T5 based Cognitive State Analyzer ---

SYSTEM_PROMPT_CSA = """
You are a Cognitive State Analyzer. Classify the user's input into one of these four cognitive states:
1) Creative Flow
2) Aimless Exploration
3) Deep Work
4) Tunnel Vision

Only respond with one of these four labels exactly as above.
"""

MODEL_NAME_CSA = "google/flan-t5-small"

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

def classify_prompt_flan_t5(prompt: str) -> str:
    input_text = SYSTEM_PROMPT_CSA.strip() + "\n\nUser input: " + prompt + "\nCognitive State:"
    outputs = generator_csa(input_text)
    raw = outputs[0]["generated_text"].strip()
    label = raw.splitlines()[0]  # take first line only
    # Defensive fallback in case model outputs something unexpected
    valid_labels = {"Creative Flow", "Aimless Exploration", "Deep Work", "Tunnel Vision"}
    if label not in valid_labels:
        label = "Aimless Exploration"  # fallback default
    return label

# --- 2. Router Engine ---

class RouterEngine:
    def __init__(self, model_id="epfl-llm/meditron-7b", hf_token=None, use_gpu=False):
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
            do_sample=True,         # Allow some sampling for varied responses
            temperature=0.7,
            eos_token_id=tokenizer.eos_token_id
        )

    def route(self, user_input: str) -> str:
        # 1. Detect cognitive state using FLAN-T5
        state = classify_prompt_flan_t5(user_input)
        print(f"[CSA] Detected cognitive state: {state}")

        # 2. System prompt selection (your original English prompts)
        if state == "Creative Flow":
            system_prompt = (
                "You are a creative and open-minded medical assistant. "
                "The user is currently in a state of creative flow — they are exploring ideas in an imaginative and constructive way. "
                "Encourage brainstorming, offer unconventional ideas, and support lateral thinking. "
                "Don't be too rigid or judgmental. Explore even unorthodox medical angles if relevant."
            )
        elif state == "Aimless Exploration":
            system_prompt = (
                "You are a concise and guiding medical assistant. "
                "The user appears to be exploring without a clear goal or direction. "
                "Gently help them clarify what they are asking, and guide them toward a more specific and medically actionable question. "
                "Be patient, but try to bring structure to the conversation."
            )
        elif state == "Deep Work":
            system_prompt = (
                "You are a focused and knowledgeable medical assistant. "
                "The user is working in a deep, goal-oriented manner and is seeking detailed, structured, and technical medical information. "
                "Provide in-depth responses that are logically ordered and medically precise. Do not oversimplify."
            )
        elif state == "Tunnel Vision":
            system_prompt = (
                "You are a reflective and broad-minded medical assistant. "
                "The user is focused, but might be thinking too narrowly. "
                "Help them consider alternative diagnoses, treatment options, or explanations. "
                "Offer counterpoints or reframe their assumptions gently."
            )
        else:
            system_prompt = "You are a helpful and supportive medical assistant."

        print(f"[RouterEngine] Using system prompt:\n{system_prompt}\n")

        # 3. Construct full prompt for Meditron
        full_prompt = f"""### System:
{system_prompt}

### User:
{user_input}

### Assistant:"""

        # 4. Generate response
        output = self.generator(full_prompt)[0]["generated_text"]
        raw_completion = output[len(full_prompt):].strip()

        # 5. Stop at role markers to avoid repetition
        stop_tokens = ["###", "User:", "System:", "Assistant:"]
        for stop in stop_tokens:
            if stop in raw_completion:
                raw_completion = raw_completion.split(stop)[0].strip()
                break

        # 6. Fallback if empty output
        if not raw_completion:
            raw_completion = "Could you please clarify your question or provide more details so I can assist you better?"

        return raw_completion


# --- 3. CLI Entry Point ---

if __name__ == "__main__":
    router = RouterEngine(hf_token=HF_TOKEN)

    print("\n💬 Type your medical questions. Type 'exit' to stop.\n")

    while True:
        user_prompt = input("🧑‍⚕️ You: ").strip()
        if user_prompt.lower() == "exit":
            print("👋 Exiting Meditron chat.")
            break

        response = router.route(user_prompt)
        print("\n🤖 Meditron:", response)
        print("-" * 50)
