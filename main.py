import os
from dotenv import load_dotenv

from ingestion import clone_repo, Chunker
from embeddings import Embedder
from storage import VectorStore
from search import SearchEngine


def main():
    load_dotenv()
    
    api_key = os.environ.get("VOYAGE_API_KEY")
    if not api_key:
        print("Set VOYAGE_API_KEY in .env file")
        return
    
    # Get repo URL
    repo_url = input("GitHub repo URL: ").strip()
    if not repo_url:
        print("No URL provided")
        return
    
    # Initialize components
    chunker = Chunker()
    embedder = Embedder(api_key)
    store = VectorStore()
    engine = SearchEngine(embedder, store)
    
    # Clone and process
    print(f"\nCloning {repo_url}...")
    with clone_repo(repo_url) as repo_path:
        print("Parsing code...")
        chunks = chunker.chunk_repo(repo_path)
        print(f"Found {len(chunks)} chunks")
        
        if not chunks:
            print("No Python code found")
            return
        
        print("Embedding chunks...")
        chunks_with_embeddings = embedder.embed_chunks(chunks)
        
        print("Indexing...")
        store.add(chunks_with_embeddings)
        
        print("\nReady! Ask questions about the codebase.")
        print("Type 'quit' to exit.\n")
        
        # Query loop
        while True:
            query = input("Query: ").strip()
            
            if query.lower() in ("quit", "exit", "q"):
                break
            
            if not query:
                continue
            
            results = engine.search(query)
            
            print(f"\n{'='*60}\n")
            for i, r in enumerate(results, 1):
                name = f"{r['class']}.{r['name']}" if r['class'] else r['name']
                
                print(f"{i}. {name} ({r['type']})")
                print(f"   {r['file']}:{r['line']}")
                print(f"   Score: {r['score']:.3f}")
                
                if r['docstring']:
                    print(f"   \"{r['docstring'][:80]}\"")
                
                # Show first 8 lines of code
                preview = '\n'.join(r['code'].split('\n')[:8])
                print(f"\n{preview}\n")
            
            print(f"{'='*60}\n")


if __name__ == "__main__":
    main()