from modules.router_engine import build_knowledge_index, build_summary_index
from modules.index_harvester import harvest_knowledge
from modules.model_settings import embedding_model
from modules.prompts import build_full_prompt, CHAIN_OF_THOUGHT_SYSTEMPROMPT

class QueryEngine:
    def __init__(self, meditron_generate, summary_texts):
        # Wissen dynamisch generieren und Indexe bauen 
        self.knowledge_texts = harvest_knowledge(meditron_generate)
        self.knowledge_index = build_knowledge_index(self.knowledge_texts)
        self.summary_texts = summary_texts
        self.summary_index = build_summary_index(self.summary_texts)
        self.embedding_model = embedding_model

    def query(self, user_prompt, system_prompt=CHAIN_OF_THOUGHT_SYSTEMPROMPT):
        # Embedding für die Anfrage
        user_emb = self.embedding_model.encode([user_prompt])
        # Wissen suchen
        _, k_idx = self.knowledge_index.kneighbors(user_emb)
        relevant_knowledge = [self.knowledge_texts[i] for i in k_idx[0]]
        # Erklärung suchen
        _, s_idx = self.summary_index.kneighbors(user_emb)
        relevant_summary = [self.summary_texts[i] for i in s_idx[0]]
        # Prompt bauen
        prompt = build_full_prompt(system_prompt, user_prompt, relevant_knowledge, relevant_summary)
        return prompt