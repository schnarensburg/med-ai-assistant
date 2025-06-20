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
