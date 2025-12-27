import chromadb


class VectorStore:
    """Store and search code embeddings using ChromaDB."""
    
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.create_collection(
            name="code",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add(self, chunks_with_embeddings: list[tuple]):
        """Store chunks with their embeddings."""
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        for chunk, embedding in chunks_with_embeddings:
            chunk_id = f"{chunk.file_path}:{chunk.name}:{chunk.start_line}"
            
            ids.append(chunk_id)
            embeddings.append(embedding)
            documents.append(chunk.content)
            metadatas.append({
                "name": chunk.name,
                "type": chunk.chunk_type,
                "file": chunk.file_path,
                "line": chunk.start_line,
                "class": chunk.parent_class or "",
                "docstring": chunk.docstring or "",
            })
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
    
    def search(self, query_embedding: list[float], top_k: int = 5) -> list[dict]:
        """Find most similar chunks to query."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        formatted = []
        for i in range(len(results["ids"][0])):
            meta = results["metadatas"][0][i]
            formatted.append({
                "name": meta["name"],
                "type": meta["type"],
                "file": meta["file"],
                "line": meta["line"],
                "class": meta["class"] if meta["class"] else None,
                "docstring": meta["docstring"] if meta["docstring"] else None,
                "code": results["documents"][0][i],
                "score": 1 - results["distances"][0][i]
            })
        
        return formatted