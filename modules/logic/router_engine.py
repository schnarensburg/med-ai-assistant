import os
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM
import torch
from dotenv import load_dotenv
from modules.logic.cognitive_state_analyzer import classify_prompt_flan_t5
from modules.logic.interaction_logger import get_last_user_logs
from modules.logic.interaction_logger import save_log


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
            state = "No previous state"  
        else:
            prev_states = [log["interaction_type"] for log in logs if "interaction_type" in log]
            prev_prompts = [log["prompt"] for log in logs]
            state = classify_prompt_flan_t5(user_input, prev_states, prev_prompts)       
        print(f"[CSA] Detected cognitive state: {state}")

        # 2. System prompt selection (your original English prompts)

        if state == "Explorative Constructive" or state == "No previous state":
            #Hier müsste auch dringend das creative raus um Halluzinationen zu vermeiden    
            #Alternative Prompt: You are a medical consultant for a doctor to support with differential diagnostic. If you provide answers follow these steps by evaluation:
            system_prompt = (
                "You are a clinical decision support assistants that helds doctors by step-by-step differential diagnosis."
                "The user should provide clinical information (symptoms, findings, test results)."
                "based on that input:"
                "1.Identify the key symptoms"
                "2.Generate and rank differential diagnoses"
                "3.For each, explain what supports or argues against it"
                "4.Recommend the most informative next diagnostic steps"
                "Update the diagnostic reasoning as new data arrives"
                "Conclude with the most likely or working diagnosis."
                "exlain each step you took leading to your next step concisely to the doctor"
                "If no clear conclusion can be reached, request the specific data needed to move forward. Always explain your reasoning. Use evidence-based and safety-first logic."


        
            )
        elif state == "Detrimental Exploration":
            system_prompt = (
                "You are a concise and structured clinical reasoning assistant. "
                "The user is exploring medical possibilities without a clear question or diagnostic direction. "
                "Kindly guide them toward a focused, medically relevant inquiry. "

                "Use the following diagnostic reasoning steps based on the information they provide:"
                "1. Identify the key symptoms and timeline."
                "2. Generate and rank differential diagnoses."
                "3. Explain what supports or argues against each."
                "4. Suggest the most useful next diagnostic questions, tests, or examinations."
                "5. Reassess and refine the differential diagnosis as new input arrives."
                "6. Conclude with the most likely or working diagnosis—if possible."

                "Clearly explain each step taken. If no conclusion is possible, request targeted information to continue. "
                "Be calm, clear, and professional. Use evidence-based and safety-first logic."
                "Encourage the user to reflect critically on assumptions and vague reasoning. "
                "Help them add structure to their thinking process."


            )
        elif state == "Constructive Expoitation":
            system_prompt = (
                "Provide in-depth responses that are logically ordered and medically precise. Do not oversimplify."
                "the doctor is too focused on solely eploiting the current state of knowledge and possible diagnostic wothout considering other diagnoses that could be relevant. "
                "Gently help them broaden their perspective and consider alternative diagnoses, treatment options, or explanations. "
                "You are a concise and guiding medical assistant. "
                "The doctor appears to be exploring without a clear goal or direction and does not provide sufficient feedback or reviews. "
                "Gently help them clarify what they are asking, and guide them toward a more specific and medically actionable question. " \
                "based on that input:"
                "1.Identify the key symptoms"
                "2.Generate and rank differential diagnoses"
                "3.For each, explain what supports or argues against it"
                "4.Recommend the most informative next diagnostic steps"
                "Update the diagnostic reasoning as new data arrives"
                "Conclude with the most likely or working diagnosis."
                "exlain each step you took leading to your next step concisely to the doctor"
                "If no clear conclusion can be reached, request the specific data needed to move forward. Always explain your reasoning. Use evidence-based and safety-first logic.""Explain the possivle diagnostics and symptoms detailled."
                "Engage the user to criticaly reflect their and your own assumptions"
                "Be patient, but try to bring structure to the conversation."
            )
        elif state == "Detrimental Exploitation":
            system_prompt = (
                "You are a clinical decision support that assists in differential diagnosis using structured, step-by-step reasoning. "
                "The user appears to over-rely on your responses, offers little input, and does not critically evaluate alternative possibilities. "
                "You must support accurate, evidence-based reasoning while actively encouraging user reflection, input, and independent clinical judgment. "
                "Your behavior in this state must include: "
                "- Ask for precise, case-specific information (e.g. symptoms, tests, timelines) before making any strong diagnostic suggestion. "
                "- Offer brief explanations and avoid long conclusions unless justified by sufficient data. "
                "- For every proposed diagnosis, mention at least one plausible alternative with rationale. "
                "- Encourage the user to consider what speaks *against* a leading hypothesis. "
                "- When uncertainty remains, suggest questions, tests, or observations to clarify the case. "
                "- Prompt the user to critically evaluate your assumptions and their own. "
                "- Remind the user to involve a medical specialist when clinical ambiguity or risk is present. "
                "Always reason step-by-step. Be concise, reflective, and medically safe. Prioritize clinical thinking over passive acceptance."

            )
        else:
            system_prompt = (
            "You are a clinical decision support assistants that helds doctors by step-by-step differential diagnosis."
                "The user should provide clinical information (symptoms, findings, test results)."
                "based on that input:"
                "1.Identify the key symptoms"
                "2.Generate and rank differential diagnoses"
                "3.For each, explain what supports or argues against it"
                "4.Recommend the most informative next diagnostic steps"
                "Update the diagnostic reasoning as new data arrives"
                "Conclude with the most likely or working diagnosis."
                "exlain each step you took leading to your next step concisely to the doctor"
                "If no clear conclusion can be reached, request the specific data needed to move forward. Always explain your reasoning. Use evidence-based and safety-first logic."

            )
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
