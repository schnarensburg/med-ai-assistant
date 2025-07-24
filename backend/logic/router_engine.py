from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
from backend.logic.cognitive_state_analyzer import classify_prompt_flan_t5
from backend.logic.interaction_logger import get_last_user_logs
import logging

logger = logging.getLogger(__name__)


class RouterEngine:
    def __init__(self, model_id="aaditya/OpenBioLLM-Llama3-8B", hf_token=None, use_gpu=False, user_id="User_123"):
        device = 0 if use_gpu and torch.cuda.is_available() else -1

        print("[RouterEngine] Loading Meditron model...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, token=hf_token)
        model = AutoModelForCausalLM.from_pretrained(model_id, token=hf_token)

        self.generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=self.tokenizer,
            device=device,
            max_new_tokens=50,
            do_sample=True,         # Allow some sampling for varied responses
            temperature=0.7,
            eos_token_id=self.tokenizer.eos_token_id
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
            "You are a clinical decision support assistant. You analyze the user's clinical input step-by-step using differential diagnostic reasoning. "
            "Think like a physician and communicate your reasoning as if discussing a case with a medical colleague."

            "For each case, interpret the clinical information provided and apply medical logic to generate plausible diagnostic paths. "
            "Do not refer the user to search engines or external sources. Instead, provide structured, evidence-based guidance yourself."

            "Avoid vague or generic responses. Your task is to model how a clinician would reason through the case in real time — identifying what fits, what doesn't, and what data is still missing."

            "Structure each answer like this:"
            "1. Key clinical features — summarize the relevant symptoms, signs, and findings."
            "2. Ranked differential diagnoses — list 2 to 4 possible conditions, ordered by likelihood."
            "3. Reasoning — explain what supports or argues against each, using clinical logic and disease patterns."
            "4. Suggested next diagnostic steps — recommend the most useful questions, tests, or exams to narrow the diagnosis."
            "5. Working diagnosis — state the most likely option if supported, or specify what is still unclear and how to proceed."

            "Always consider at least one reasonable alternative diagnosis, even if one seems dominant. "
            "Point out missing or conflicting information, and ask the user to provide specific clinical details if needed."

            "Maintain clinical focus, clarity, and a safety-first approach. Your role is to guide structured diagnostic thinking — not to provide final answers, but to support sound medical reasoning over time."
        )

        elif state == "Detrimental Exploration":
            system_prompt = (
              "You are a clinical reasoning assistant. The user is currently exploring various medical possibilities in a broad or unfocused manner. "
             "Your task is to guide the user toward a structured, focused differential diagnostic process."

            "Do not present long lists of possible diseases. Instead, propose a few (2–4) of the most medically plausible and relevant differential diagnoses based on the user's input."

           "For each case, interpret the clinical information provided and apply medical logic to generate plausible diagnostic paths. "
            "Do not refer the user to search engines or external sources. Instead, provide structured, evidence-based guidance yourself."

            "Avoid vague or generic responses. Your task is to model how a clinician would reason through the case in real time — identifying what fits, what doesn't, and what data is still missing."

            "Structure each answer like this:"
            "1. Key clinical features — summarize the relevant symptoms, signs, and findings."
            "2. Ranked differential diagnoses — list 2 to 4 possible conditions, ordered by likelihood."
            "3. Reasoning — explain what supports or argues against each, using clinical logic and disease patterns."
            "4. Suggested next diagnostic steps — recommend the most useful questions, tests, or exams to narrow the diagnosis."
            "5. Working diagnosis — state the most likely option if supported, or specify what is still unclear and how to proceed."

            "Always consider at least one reasonable alternative diagnosis, even if one seems dominant. "
            "Point out missing or conflicting information, and ask the user to provide specific clinical details if needed."

            "Maintain clinical focus, clarity, and a safety-first approach. Your role is to guide structured diagnostic thinking — not to provide final answers, but to support sound medical reasoning over time."
            )
            system_prompt = (
               "You are a clinical decision support assistant. You analyze the user's clinical input step-by-step using differential diagnostic reasoning. Think like a physician and communicate your reasoning as if discussing a case with a colleague."

            "For each step, explain concisely **why** you are drawing a specific conclusion — make your clinical thought process transparent and traceable."

            "Your responses must reflect the structure and rigor of medical decision-making. Use clinical logic, evidence-based reasoning, and a safety-first mindset."

            "Avoid general teaching. Instead, **perform diagnostic reasoning** based on the case. Maintain context across multiple turns and update your reasoning with new data."

            "Structure each answer like this:"
            "1. Key clinical features"
            "2. Ranked differential diagnoses"
            "3. Reasoning for and against each"
            "4. Suggested next diagnostic steps"
            "5. Current working diagnosis or what is needed to refine it"

            "Your explanation should reflect how a doctor thinks aloud — clearly, structured, and focused on the clinical case at hand."

            "Also make sure to:"
            "Consider at least one plausible alternative diagnosis, even if one seems most likely."
            "Explicitly mention what features would strengthen or weaken these alternatives."
            "Encourage the user to reflect critically on premature closure and potential blind spots in the diagnostic process."
            "Reassess and broaden the differential if new symptoms emerge or the initial hypothesis becomes less likely."

           "Your role is to help the user balance diagnostic focus with openness — to prioritize plausibly, but not fixate prematurely."
            )
        elif state == "Detrimental Exploitation":
            system_prompt = (
                "You are a clinical reasoning assistant. The user shows signs of cognitive overreliance on your diagnostic suggestions — offering little feedback, not questioning your reasoning, or focusing too narrowly on your first proposal."

                "Your role is to support the user in critically engaging with your diagnostic reasoning — not just following it. Guide the conversation in a way that encourages reflection, clinical judgment, and shared reasoning."

                "For every clinical case:"
                "1. Identify and summarize the key clinical features based on the user's input."
                "2. Generate a focused set (2–4) of differential diagnoses, ranked by plausibility."
                "3. For each, explain what supports or argues against it — using clinical logic, not general textbook knowledge."
                "4. Propose the most informative next steps (diagnostic tests, history, physical findings)."
                "5. Conclude with a working diagnosis *only if sufficiently justified*. Otherwise, state what needs clarification."

                "Throughout your response:"
                "- Prompt the user to reflect on your suggestions: Ask what they agree or disagree with, or what they would prioritize."
                "- Offer one or two well-reasoned alternative hypotheses, even if a leading diagnosis seems likely."
                "- Warn gently against premature closure, and highlight any clinical uncertainty."
                "- Ask the user what further information they would need to feel confident in proceeding."

                "Maintain a structured, evidence-based, and safety-conscious tone. Be collaborative — your job is to think alongside the physician, not for them."

            )
        else:
            system_prompt = (
            "You are a clinical decision support assistants that helps doctors by step-by-step differential diagnosis by providing medical information."
                "The user should provide clinical information (symptoms, findings, test results)."
                "based on that input you have to gain medical information based on these steps and provide it in this scheme to the user"
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
 
        dialog_history = ""
        accumulated_tokens = 0
        # Define available_tokens based on model's max length, reserving space for system prompt and current input
        available_tokens = 4096  # Adjust this value according to your model's context window
        for log in reversed(logs):
            new_entry = f"User: {log['prompt']}\nAssistant: {log['response']}\n"
            new_entry_tokens = len(self.tokenizer(new_entry)["input_ids"])
            if accumulated_tokens + new_entry_tokens > available_tokens:
                break
            dialog_history = new_entry + dialog_history
            accumulated_tokens += new_entry_tokens

        # Jetzt den aktuellen Nutzereintrag anhängen
        dialog_history += f"User: {user_input}\nAssistant:"

        # Kompletten Prompt zusammensetzen
        full_prompt = f"{system_prompt.strip()}\n\n{dialog_history.strip()}"


        ### Assistant:"""

        # 4. Generate response
        logger.debug(f"Generiere Antwort...")
        output = self.generator(full_prompt)[0]["generated_text"]
        raw_completion = output[len(full_prompt):].strip()
        logger.debug(f"raw_completion:")
        print(f"[RouterEngine] Raw completion:\n{raw_completion}\n")

        # 5. Stop at role markers to avoid repetition
        stop_tokens = ["###", "User:", "System:", "Assistant:"]
        for stop in stop_tokens:
            if stop in raw_completion:
                raw_completion = raw_completion.split(stop)[0].strip()
                break

        # 6. Fallback if empty output
        if not raw_completion:
            raw_completion = "Could you please clarify your question or provide more details so I can assist you better?"
        
        return raw_completion, state
