import os
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM
import torch
from dotenv import load_dotenv
from modules.backend.cognitive_state_analyzer import classify_prompt_flan_t5
from modules.backend.interaction_logger import get_last_user_logs
from modules.backend.interaction_logger import save_log


class RouterEngine:
    def __init__(self, model_id="epfl-llm/meditron-7b", hf_token=None, use_gpu=False, user_id="User_123"):
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

    def route(self, user_input: str, user_id) -> str:
        # 1. Detect cognitive state using FLAN-T5
        logs = get_last_user_logs(user_id, n=1)
        if len(logs) == 0:
    # Erste Anfrage: Default-State setzen, nicht klassifizieren
            state = "Creative Flow"  
        else:
            prev_states = [log["interaction_type"] for log in logs if "interaction_type" in log]
            prev_prompts = [log["prompt"] for log in logs]
            state = classify_prompt_flan_t5(user_input, prev_states, prev_prompts)       
        print(f"[CSA] Detected cognitive state: {state}")

        # 2. System prompt selection (your original English prompts)

        if state == "Creative Flow":
            #Hier müsste auch dringend das creative raus um Halluzinationen zu vermeiden    
            #Alternative Prompt: You are a medical consultant for a doctor to support with differential diagnostic. If you provide answers follow these steps by evaluation:
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
