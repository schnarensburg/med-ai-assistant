"""
quick_med_assistant.py
----------------------------------------------------
Minimal‑Demo für ein medizinisches Frage‑Antwort‑System
   • Index + Embeddings     (semantische Suche)
   • Router + Cognitive State (Tonfall wählen)
   • Meditron‑LLM           (Antwort generieren)
----------------------------------------------------
ACHTUNG: Nicht als echte Diagnose verwenden!
"""

import os, json, uuid
from datetime import datetime
from pathlib import Path

# 1) ---------- Modelle laden -----------------------------------------------
from sentence_transformers import SentenceTransformer          # Embeddings
from sklearn.neighbors import NearestNeighbors                  # Index
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

LLM_MODEL      = "epfl-llm/meditron-7b"      # :contentReference[oaicite:0]{index=0}
EMBED_MODEL    = "BAAI/bge-large-en"
TOP_K          = 3                           # wie viele Fakten holen?

print("▶ Lade Embedding‑Modell …")
embedder = SentenceTransformer(EMBED_MODEL)

print("▶ Lade Meditron‑LLM (erst­maliger Download braucht Zeit) …")
tok = AutoTokenizer.from_pretrained(LLM_MODEL, use_fast=True)
meditron = AutoModelForCausalLM.from_pretrained(
    LLM_MODEL,
    device_map="auto",              # nutzt GPU, falls vorhanden
    torch_dtype="auto",
)
generate = pipeline(
    "text-generation",
    model=meditron,
    tokenizer=tok,
    max_new_tokens=512,
    temperature=0.2,
)

# 2) ---------- kleines Wissens­lager bauen ----------------------------------
def harvest_knowledge():
    """Lässt Meditron 10 Fakten produzieren (nur Demo!)."""
    seed_prompt = ("Give me 10 concise clinical facts "
                   "about common symptoms: fever, cough, abdominal pain.")
    print("▶ Erzeuge medizinische Beispiel‑Fakten …")
    raw = generate(seed_prompt, do_sample=False)[0]["generated_text"]
    lines = [l.lstrip("-• ").strip() for l in raw.split("\n") if l.strip()]
    return lines[:10]

KNOWLEDGE_TEXTS = harvest_knowledge()

print("▶ Embeddings für Fakten berechnen …")
kb_vecs = embedder.encode(KNOWLEDGE_TEXTS)
knowledge_index = NearestNeighbors(n_neighbors=TOP_K, metric="cosine").fit(kb_vecs)

# 3) ---------- Cognitive State (4‑Wege‑Eimer) -------------------------------
def classify_state(text: str) -> str:
    """Grobst‑Heuristik – genügt für Demo."""
    t = text.lower()
    if "warum" in t or "wieso" in t:
        return "explorativ"     # will Erklärung
    if "was soll" in t or "wie behandle" in t or "behandlung" in t:
        return "exploitativ"   # will To‑Do
    if "alternativ" in t or "option" in t:
        return "konstruktiv"   # will Auswahl
    return "unklar"

PROMPT_STYLE = {
    "explorativ":  "Du bist ein medizinischer Erklär‑Assistent. Erkläre Schritt für Schritt.",
    "exploitativ": "Du bist ein medizinischer Assistent. Gib klare Bullet‑Point‑Empfehlungen.",
    "konstruktiv": "Du bist ein medizinischer Berater. Stelle Alternativen mit Pro & Contra dar.",
    "unklar":      "Du bist ein medizinischer Assistent. Beantworte die Frage so gut wie möglich.",
}

# 4) ---------- Prompt bauen + LLM abfragen ----------------------------------
def retrieve_facts(question: str):
    """Top‑K ähnliche Fakten holen."""
    q_vec = embedder.encode([question])
    _, idx = knowledge_index.kneighbors(q_vec)
    return [KNOWLEDGE_TEXTS[i] for i in idx[0]]

def build_prompt(state: str, question: str, facts: list[str]) -> str:
    system = PROMPT_STYLE.get(state, PROMPT_STYLE["unklar"])
    fact_block = "\n".join(f"• {f}" for f in facts)
    return f"""{system}

Frage:
{question}

Relevante Fakten:
{fact_block}

Antworte als medizinischer Fachtext:"""

# 5) ---------- Logging ----------------------------------------------
def log_interaction(prompt, response, state):
    log = {
        "id": str(uuid.uuid4())[:8],
        "time": datetime.now().isoformat(),
        "prompt": prompt,
        "response": response,
        "state": state,
    }
    Path("sessions").mkdir(exist_ok=True)
    with open(f"sessions/{log['id']}.json", "w") as f:
        json.dump(log, f, indent=2)

# 6) ---------- Mini‑CLI‑Loop ----------------------------------------
def chat():
    print("\n===== Meditron Demo (kein Medizin­produkt) =====")
    print("» exit « zum Beenden")
    while True:
        q = input("\nIhre Frage: ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        state = classify_state(q)
        facts = retrieve_facts(q)
        prompt = build_prompt(state, q, facts)
        raw = generate(prompt)[0]["generated_text"]
        answer = raw.split(prompt)[-1].strip()
        print("\n--- Antwort ---------------------------")
        print(answer)
        print("--------------------------------------")
        log_interaction(q, answer, state)

if __name__ == "__main__":
    chat()
