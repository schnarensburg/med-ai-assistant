from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

model_pipeline = None

def load_model():
    global model_pipeline
    if model_pipeline is None:
        tokenizer = AutoTokenizer.from_pretrained("epfl-llm/meditron-7b")
        model = AutoModelForCausalLM.from_pretrained("epfl-llm/meditron-7b")
        model_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)
    return model_pipeline


def query_model(pipe, prompt, max_tokens=300):
    output = pipe(prompt, max_new_tokens=max_tokens, do_sample=True)
    return output[0]["generated_text"]