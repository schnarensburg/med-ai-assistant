from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import logging
import time
import torch

# Enable 8-bit loading to reduce memory usage and make large models run on smaller GPUs
bnb_config = BitsAndBytesConfig(load_in_8bit=True, llm_int8_enable_fp32_cpu_offload=True) 

from backend.logic.cognitive_state_analyzer import classify_prompt_flan_t5
logger = logging.getLogger(__name__)

from backend.logic.interaction_logger import get_last_user_logs

# model_id="epfl-llm/meditron-7b" # meditron, 29 sec but bullshit answer
# model_id="openbiollm/med42-mistral-7b" # 64 sec
# model_id="aaditya/OpenBioLLM-Llama3-8B" # 90 sec (max_new_tokens=300), 44.5 (max_new_tokens=50, schlechter)

class RouterEngine:
    def __init__(self, mode="basic", model_id="aaditya/OpenBioLLM-Llama3-8B", hf_token=None, use_gpu=True):
        self.model_id = model_id
        self.mode = mode
        device = 0 if use_gpu and torch.cuda.is_available() else -1

        logger.info(f"[RouterEngine] Loading model: {model_id} on device: {'GPU' if device == 0 else 'CPU'}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, token=hf_token)
        
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            token=hf_token,
            device_map="auto",
            quantization_config=bnb_config,
            torch_dtype=torch.float16
        )

        self.generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=self.tokenizer,
            max_new_tokens=150,
            do_sample=True,
            temperature=0.5,
            eos_token_id=self.tokenizer.eos_token_id
        )

    def get_system_prompt(self, state):  # ✅ Jetzt innerhalb der Klasse!
        """Returns a system prompt based on the user's cognitive state and guides the assistant's tone and reasoning."""

        if state == "Explorative Constructive":
            return (
                "You are a clinical decision support system assisting a qualified physician or medical professional. "
                "The user is a clinician seeking diagnostic support, NOT a patient. "
                "Engage in professional medical discourse and encourage clinical reasoning.\n\n"
                "Format:\n"
                "1. Clinical assessment — Analyze the presented case professionally\n"
                "2. Differential diagnoses — Provide 3-4 evidence-based possibilities and how they can be tested\n"
                "3. Clinical reasoning — Discuss pathophysiology and clinical correlations\n"
                "4. Diagnostic workup — Suggest appropriate investigations\n"
                "5. Discussion points — Ask: 'What clinical findings support your working hypothesis?' or 'How would you rule out competing diagnoses?'\n\n"
                "**Professional approach:**\n"
                "- Address the clinician directly: 'Based on your clinical presentation...'\n"
                "- Encourage medical reasoning: 'What additional history or examination findings would strengthen this diagnosis?'\n"
                "- Discuss clinical decision-making and evidence-based approaches"
            )

        elif state == "Explorative Detrimental":
            return (
                "You are a diagnostic reasoning partner for a medical professional. "
                "Challenge clinical assumptions and demand evidence-based justification. "
                "The user is a clinician, not a patient. ALWAYS ask critical follow-up questions.\n\n"
                "Professional framework:\n"
                "1. Clinical summary — Restate the case objectively\n"
                "2. Critical analysis — 'What objective evidence supports this working diagnosis?'\n"
                "3. Missing data — 'What laboratory values, imaging, or physical findings are needed?'\n"
                "4. Alternative considerations — Present competing diagnoses with clinical rationale\n"
                "5. Critical questions — ALWAYS end with: 'What makes you think this approach is correct? Please provide further medical evaluation for me to confirm.'\n\n"
                "**Clinical approach:**\n"
                "- Say: 'Before confirming this diagnosis, what diagnostic criteria have been met?'\n"
                "- Ask: 'What timeline and clinical course would you expect with this condition?'\n"
                "- Challenge: 'How do you exclude other conditions in your differential?'\n"
                "- ALWAYS conclude with critical questioning about their reasoning"
            )

        elif state == "Exploitative Constructive":
            return (
                "You are supporting a clinician's diagnostic reasoning process. "
                "Help focus on the most likely diagnosis while maintaining clinical rigor. "
                "The user is a medical professional seeking clinical guidance.\n\n"
                "Clinical structure:\n"
                "1. Case analysis — Summarize key clinical features\n"
                "2. Primary diagnosis — Support the most likely condition with evidence\n"
                "3. Clinical reasoning — Explain pathophysiology and clinical correlations\n"
                "4. Differential considerations — Acknowledge important alternatives\n"
                "5. Clinical validation — 'What confirmatory tests or clinical signs would you expect?'\n\n"
                "**Medical discourse:**\n"
                "- Say: 'This clinical presentation is most consistent with [condition], supported by [evidence]'\n"
                "- Ask: 'How would you monitor treatment response or disease progression?'\n"
                "- Discuss: 'What are the key clinical decision points in this case?'"
            )

        elif state == "Exploitative Detrimental":
            return (
                "You are a clinical advisor challenging a colleague's diagnostic certainty. "
                "Demand rigorous justification and present alternative clinical scenarios. "
                "The user is a medical professional, not a patient. ALWAYS challenge their assumptions.\n\n"
                "Professional challenge:\n"
                "1. Clinical review — Summarize the case neutrally\n"
                "2. Diagnostic critique — 'What specific clinical criteria support this diagnosis?'\n"
                "3. Alternative diagnoses — Present serious competing conditions\n"
                "4. Evidence demand — 'What objective data confirms this over other possibilities?'\n"
                "5. Critical questioning — ALWAYS end with: 'What makes you think this approach is correct? Please provide further medical evaluation for me to confirm.'\n\n"
                "**Clinical challenge:**\n"
                "- Say: 'Before accepting this diagnosis, consider that [alternative conditions] presents similarlies'\n"
                "- Ask: 'What distinguishing clinical features rule out [competing diagnosis]?'\n"
                "- Require: 'Demonstrate how your proposed diagnosis explains all clinical findings'\n"
                "- ALWAYS demand justification: 'What makes you think this approach is correct? Please provide further medical evaluation for me to confirm.'"
            )

        return "You are a clinical decision support system for medical professionals. Provide evidence-based medical guidance for qualified healthcare providers."

    def analyze_state(self, user_input, user_id):
        """Detects cognitive state based on past logs."""
        logs = get_last_user_logs(user_id, n=1)
        if not logs:
            return "No previous state"
        prev_states = [log["interaction_type"] for log in logs]
        prev_prompts = [log["prompt"] for log in logs]
        return classify_prompt_flan_t5(user_input, prev_states, prev_prompts)

    def add_warning(self, output, state):
        """Injects clinical warnings into overly narrow reasoning."""
        if state == "Detrimental Exploitation":
            output += "\n\n⚠️ Clinical Reminder: Always consider alternative diagnoses and reassess if new symptoms appear."
        return output

    def route(self, user_input: str, user_id: str) -> str:
        start_time = time.time()
        state = "basic"

        # Optional: Cognitive State Routing
        if self.mode in ("routing", "warning"):
            logs = get_last_user_logs(user_id, n=1)
            if not logs:
                state = "No previous state"
            else:
                prev_states = [log["interaction_type"] for log in logs]
                prev_prompts = [log["prompt"] for log in logs]
                state = classify_prompt_flan_t5(user_input, prev_states, prev_prompts)
            logger.info(f"[RouterEngine] Detected cognitive state: {state}")
        else:
            logger.info("[RouterEngine] Running in basic mode")

        # Select system prompt
        system_prompt = self.get_system_prompt(state)

        # Build prompt
        prompt = f"Cognitive State: {state}\n\n{system_prompt.strip()}\n\nUser: {user_input}\nAssistant:"
        logger.debug(f"[RouterEngine] Using model: {self.model_id}")
        logger.debug(f"[RouterEngine] Prompt preview:\n{prompt[:500]}")

        # Generate
        output = self.generator(prompt)[0]["generated_text"]
        raw_completion = output[len(prompt):].strip()

        # Stop tokens cleanup
        for stop in ["###", "User:", "System:", "Assistant:"]:
            if stop in raw_completion:
                raw_completion = raw_completion.split(stop)[0].strip()
                break

        if not raw_completion:
            raw_completion = "I'm sorry, I need more information to provide a helpful answer."

        # Optional: Inject warning
        if self.mode == "warning":
            raw_completion = self.add_warning(raw_completion, state)

        duration = time.time() - start_time
        logger.info(f"[RouterEngine] Response generated in {duration:.2f} seconds")
        logger.debug(f"[RouterEngine] Response length (tokens): {len(self.tokenizer(raw_completion)['input_ids'])}")
        logger.debug(f"[RouterEngine] Final response:\n{raw_completion}")

        return raw_completion, state

    '''
    def route(self, user_input: str, user_id: str) -> str:
        start_time = time.time()

        # Simple system prompt
        system_prompt = (
            "You are a clinical assistant. Answer the user's medical questions clearly, accurately, and based on current medical knowledge.\n"
            "If necessary, ask for more information. Be concise and precise."
        )

        # Assemble prompt
        prompt = f"{system_prompt.strip()}\n\nUser: {user_input}\nAssistant:"

        logger.debug(f"[RouterEngine] Using model: {self.model_id}")
        logger.debug(f"[RouterEngine] Prompt preview:\n{prompt[:500]}")

        # Generate response
        output = self.generator(prompt)[0]["generated_text"]
        raw_completion = output[len(prompt):].strip()

        # Cleanup unwanted tokens
        stop_tokens = ["###", "User:", "System:", "Assistant:"]
        for stop in stop_tokens:
            if stop in raw_completion:
                raw_completion = raw_completion.split(stop)[0].strip()
                break

        # Fallback if empty
        if not raw_completion:
            raw_completion = "I'm sorry, I need more information to provide a helpful answer."

        duration = time.time() - start_time
        logger.info(f"[RouterEngine] Response generated in {duration:.2f} seconds")
        logger.debug(f"[RouterEngine] Response length (tokens): {len(self.tokenizer(raw_completion)['input_ids'])}")
        logger.debug(f"[RouterEngine] Final response:\n{raw_completion}")

        return raw_completion, "basic"
    '''