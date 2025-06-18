# backend/chains/cognitive_state_analyzer_chain.py

import os
from dotenv import load_dotenv
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from sentence_transformers import SentenceTransformer
import numpy as np
from backend.config import settings


# 1. Deine vier Labels
LABELS = [
    "Kreativer Flow",        # Exploration + Constructive
    "Zielloses Erkunden",    # Exploration + Detrimental
    "Vertiefendes Arbeiten", # Exploitation + Constructive
    "Tunneldenken"           # Exploitation + Detrimental
]

# 2. Einmaliges Laden des Embedding-Modells
model = SentenceTransformer("all-MiniLM-L6-v2",
                            use_auth_token=settings.hf_hub_token
                            )

# 3. Label-Embeddings vorab berechnen
label_embeddings = model.encode(LABELS, normalize_embeddings=True)

def classify_prompt(prompt: str) -> str:
    """
    Nimmt den Nutzer-Prompt, erstellt sein Embedding,
    vergleicht es via Cosine Similarity mit den vordefinierten Label-Embeddings
    und liefert das Label mit der höchsten Ähnlichkeit zurück.
    """
    # 1. Prompt einbetten und normalisieren
    prompt_emb = model.encode([prompt], normalize_embeddings=True)[0]

    # 2. Kosinus-Ähnlichkeit zu jedem Label
    #    vector dot-product reicht, da wir schon normalisiert haben
    sims = np.dot(label_embeddings, prompt_emb)

    # 3. Index des Top-Similarity-Labels
    best_idx = int(np.argmax(sims))
    return LABELS[best_idx]

'''
# backend/chains/cognitive_state_analyzer_chain.py

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
from backend.config import settings

# 1. System-Prompt, das deine 4 Felder beschreibt
SYSTEM_PROMPT = """
Du bist ein Cognitive State Analyzer. Ordne jede Nutzeranfrage in eines von vier Feldern ein:
1) Exploration + Constructive  → Kreativer Flow
2) Exploration + Detrimental   → Zielloses Erkunden
3) Exploitation + Constructive → Vertiefendes Arbeiten
4) Exploitation + Detrimental  → Tunneldenken

Gib nur den Namen des Feldes zurück, "Kreativer Flow", "Zielloses Erkunden", "Vertiefendes Arbeiten", oder "Tunneldenken".
"""

# 2. Lade FLAN-T5-small (ca. 300 MB) lokal
MODEL_NAME = "google/flan-t5-small"
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    use_auth_token=settings.hf_hub_token
)
model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME,
    use_auth_token=settings.hf_hub_token
)

# 3. Baue einen einfachen Text2Text-Generator-Pipeline
generator = pipeline(
    "text2text-generation",
    model=model,
    tokenizer=tokenizer,
    device=-1,  # -1 = CPU; für GPU gib hier ggf. 0,1,...
    max_new_tokens=16,  # ausreichend für ein kurzes Label
    clean_up_tokenization_spaces=True,
    # use_auth_token=settings.hf_hub_token
)


def classify_prompt(prompt: str) -> str:
    """
    Packt System-Prompt + die User-Anfrage zusammen,
    lässt das Modell das passende Label (nur den Namen) generieren
    und gibt es zurück.
    """
    # Inputtexte zusammensetzen
    input_text = SYSTEM_PROMPT.strip() + "\n\nNutzeranfrage: " + prompt + "\nKategorie:"

    # Generiere Output
    outputs = generator(input_text)
    raw = outputs[0]["generated_text"].strip()

    # Gib nur die erste Zeile zurück (Label)
    label = raw.splitlines()[0]
    return label
'''
