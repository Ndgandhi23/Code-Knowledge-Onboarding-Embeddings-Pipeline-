import voyageai


class Embedder:
    """Generate embeddings using Voyage AI."""
    
    MODEL = "voyage-code-3"
    BATCH_SIZE = 128
    
    def __init__(self, api_key: str):
        self.client = voyageai.Client(api_key=api_key)
    
    def embed_chunks(self, chunks: list) -> list[tuple]:
        """Embed all chunks, return (chunk, embedding) pairs."""
        texts = [self._chunk_to_text(c) for c in chunks]
        
        all_embeddings = []
        for i in range(0, len(texts), self.BATCH_SIZE):
            batch = texts[i:i + self.BATCH_SIZE]
            result = self.client.embed(batch, model=self.MODEL, input_type="document")
            all_embeddings.extend(result.embeddings)
        
        return list(zip(chunks, all_embeddings))
    
    def embed_query(self, query: str) -> list[float]:
        """Embed a search query."""
        result = self.client.embed([query], model=self.MODEL, input_type="query")
        return result.embeddings[0]
    
    def _chunk_to_text(self, chunk) -> str:
        """Convert chunk to embedding-friendly text."""
        parts = []
        
        if chunk.parent_class:
            parts.append(f"Method {chunk.name} in class {chunk.parent_class}")
        elif chunk.chunk_type == "class":
            parts.append(f"Class {chunk.name}")
        else:
            parts.append(f"Function {chunk.name}")
        
        if chunk.docstring:
            parts.append(f"Description: {chunk.docstring}")
        
        if chunk.calls:
            parts.append(f"Calls: {', '.join(chunk.calls)}")
        
        parts.append(f"Code:\n{chunk.content}")
        
        return "\n".join(parts)