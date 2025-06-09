from modules.model_settings import embedding_model
from sklearn.neighbors import NearestNeighbors

def harvest_knowledge(meditron_generate):
    prompt = (
        "Gib mir 10 kurze medizinische Fakten zu häufigen Symptomen wie Fieber, Husten, Bauchschmerzen, etc. "
        "Formuliere sie jeweils als einzelner klinischer Satz."
    )
    result = meditron_generate(prompt)
    return [line.strip("- ").strip() for line in result.split("\n") if line.strip()]

def build_knowledge_index(knowledge_texts):
    embeddings = embedding_model.encode(knowledge_texts)
    return NearestNeighbors(n_neighbors=3, metric="cosine").fit(embeddings)

def build_summary_index(summary_texts):
    embeddings = embedding_model.encode(summary_texts)
    return NearestNeighbors(n_neighbors=3, metric="cosine").fit(embeddings)
