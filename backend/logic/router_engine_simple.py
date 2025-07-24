from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import logging
import time
import torch

# Enable 8-bit loading to reduce memory usage and make large models run on smaller GPUs
bnb_config = BitsAndBytesConfig(load_in_8bit=True, llm_int8_enable_fp32_cpu_offload=True) 

logger = logging.getLogger(__name__)

# model_id="epfl-llm/meditron-7b" # meditron, 29 sec but bullshit answer
# model_id="openbiollm/med42-mistral-7b" # 64 sec
# model_id="aaditya/OpenBioLLM-Llama3-8B" # 90 sec (max_new_tokens=300), 44.5 (max_new_tokens=50, schlechter)

class RouterEngine:
    def __init__(self, mode="basic", model_id="aaditya/OpenBioLLM-Llama3-8B", hf_token=None, use_gpu=True): # Set use_gpu to True 
        self.model_id = model_id
        self.mode = mode
        device = 0 if use_gpu and torch.cuda.is_available() else -1

        logger.info(f"[RouterEngine] Loading model: {model_id} on device: {'GPU' if device == 0 else 'CPU'}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, token=hf_token)
        '''model = AutoModelForCausalLM.from_pretrained(model_id, token=hf_token)'''
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            token=hf_token,
            device_map="auto",
            quantization_config=bnb_config, # Enable 8-bit quantization
            torch_dtype=torch.float16 # Use FP16 for faster inference   
        )

        self.generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=self.tokenizer,
            #device=device # Take this out otherwise wont run
            max_new_tokens=150, # Decreased max new tokens from 200 to 150 to speed up model response
            do_sample=True,
            temperature=0.5, # Decreased temperature from 0.7 to 0.5 to get balanced and more deterministic answers 
            eos_token_id=self.tokenizer.eos_token_id
        )

    def get_system_prompt(self, state):
        """Returns a system prompt based on cognitive state."""
        if state == "Detrimental Exploration":
            return "...Prompt for exploratory overload..."
        elif state == "Detrimental Exploitation":
            return "...Prompt with reflection encouragement..."
        elif state == "Constructive Exploration":
            return "...Prompt for exploratory knowledge..."
        elif state == "Constructive Exploitation":
            return "...Prompt for detailed focus..."
        return "...Default prompt..."


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
        prompt = f"{system_prompt.strip()}\n\nUser: {user_input}\nAssistant:"
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