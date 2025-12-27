# Semantic Code Search Engine

Search any GitHub repo using natural language. Instead of grep's exact string matching, this uses semantic embeddings to understand what your code actually does—so you can query "how do we handle payments" and get back billing functions, Stripe integrations, and transaction handlers even if they never use the word "payment."

## Getting Started

Clone this repo and follow the setup instructions below to run semantic search on any public GitHub repository.

### Prerequisites

You'll need:

- **Python 3.8+**
- **Voyage AI API key** (get one at [voyage.ai](https://www.voyageai.com))
- **Git** installed on your system

### Installing

**Step 1: Clone and navigate to the project**
```bash
git clone https://github.com/Ndgandhi23/Code-Knowledge-Onboarding-Embeddings-Pipeline-.git
cd Code-Knowledge-Onboarding-Embeddings-Pipeline-
```

**Step 2: Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 3: Set up your API key**

Create a `.env` file in the project root:
```bash
echo "VOYAGE_API_KEY=your_voyage_api_key_here" > .env
```

**Step 4: Run the search engine**
```bash
python main.py
```

You'll be prompted to enter a GitHub URL. Try it with any public Python repo:
```
Enter GitHub URL: https://github.com/psf/requests
```

The system will clone, chunk, and embed the repo (this takes a minute). Then you can query:
```
Query: how does authentication work
Query: where are HTTP errors handled
Query: session management
```

Results show the most semantically relevant code chunks with file paths and line numbers.

---

## How It Works

**Pipeline: Clone → Chunk → Embed → Store → Search**

1. **Shallow clones** the target repo (latest commit only)
2. **Parses Python files** with tree-sitter into functions, classes, and methods
3. **Enriches chunks** with metadata (names, docstrings, call graphs)
4. **Embeds to 1024D vectors** using Voyage Code 3
5. **Stores in ChromaDB** with HNSW indexing
6. **Searches via cosine similarity** between query and code vectors

### Architecture Details

**Chunking**: Tree-sitter extracts discrete code units with full context—name, type, location, parent class, docstring, and functions called. Each chunk gets enriched with semantic anchors before embedding (e.g., "Method process_charge in BillingService that creates Stripe charges") so the model understands intent, not just syntax.

**Vector Storage**: ChromaDB indexes 1024-float embeddings with HNSW (Hierarchical Navigable Small World) for O(log n) approximate nearest neighbor search.

**Similarity**: Cosine similarity measures the angle between vectors in 1024D space. Direction encodes semantics—a 500-line billing module and 50-line payment helper about the same concept point the same direction. Magnitude doesn't matter.

**Embedding Space**: Voyage's model learned from millions of code examples. Related concepts cluster together—"payment", "charge", "billing", "transaction" live in the same region. Your query embeds into that space and returns everything nearby, regardless of exact terminology.

---

## Built With

- **[tree-sitter](https://tree-sitter.github.io/tree-sitter/)** - AST parsing for accurate code chunking
- **[Voyage AI](https://www.voyageai.com)** - Code-specific embeddings (voyage-code-3 model)
- **[ChromaDB](https://www.trychroma.com)** - In-memory vector database with HNSW indexing
- **[python-dotenv](https://github.com/thepracticaldev/python-dotenv)** - Environment variable management

---

## Limitations

- **Python only** (tree-sitter grammar is language-specific, but supports 40+ languages)
- **In-memory storage** (no persistence between runs)
- **Approximate search** (HNSW trades accuracy for speed)
- **Batch processing** (128 chunks per Voyage API call)

---

## Future Work

- Multi-language support beyond Python
- Persistent vector storage with database backend
- Function signature and type hint extraction
- Cross-repo search with shared vector index
- Streaming results for large repositories

---

## Authors

**Neil Gandhi** - [GitHub](https://github.com/Ndgandhi23)

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Acknowledgments

Built on the shoulders of tree-sitter for parsing, Voyage AI for embeddings, and ChromaDB for vector storage. Inspired by the idea that code search should understand meaning, not just match strings.