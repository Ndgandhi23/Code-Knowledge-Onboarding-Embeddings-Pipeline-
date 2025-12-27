from embeddings import Embedder
from storage import VectorStore


class SearchEngine:
    """Ties together embedding and search."""
    
    def __init__(self, embedder: Embedder, store: VectorStore):
        self.embedder = embedder
        self.store = store
    
    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Search codebase with natural language query."""
        query_embedding = self.embedder.embed_query(query)
        results = self.store.search(query_embedding, top_k=top_k)
        return results