from sklearn.preprocessing import normalize
from llama_index.embeddings.base import BaseEmbedding
from qdrant_client import QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index import VectorStoreIndex, ServiceContext
from llama_index.readers.file import SimpleDirectoryReader
from sentence_transformers import SentenceTransformer
embedding_model = SentenceTransformer("BAAI/bge-large-en")