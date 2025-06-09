from modules.model_settings import embedding_model
from sklearn.neighbors import NearestNeighbors
from modules.index_harvester import harvest_knowledge
knowledge_texts = harvest_knowledge(meditron_generate)  # Diese Funktion musst du definieren
