# Jarvis Architecture & Implementation Guide

## System Overview

Jarvis is a production-ready personal AI assistant that combines:
1. **Local LLM** (LLaMA 3 8B via Ollama) for text generation
2. **Vector Database** (Pinecone) for semantic search
3. **RAG Pipeline** for grounded, accurate responses
4. **Web UI** (Streamlit) for easy interaction

## Component Breakdown

### 1. Backend (`backend/main.py`)

**FastAPI Application** with two main endpoints:

#### `/chat` (POST)
```python
Request: {
    "query": "What is RAG?",
    "top_k": 5  # Number of documents to retrieve
}

Response: {
    "answer": "RAG is...",
    "sources": [...],
    "context_count": 3
}
```

**Process:**
1. Accepts user query
2. Calls RAG engine
3. Returns structured response with sources

#### `/index` (POST)
```python
Request: {
    "documents": [
        {
            "id": "doc_001",
            "text": "Content here",
            "source": "Wikipedia"
        }
    ]
}

Response: {
    "status": "success",
    "documents_indexed": 8
}
```

**Process:**
1. Receives documents
2. Embeds each document
3. Upserts to Pinecone

### 2. RAG Engine (`backend/rag.py`)

Orchestrates the retrieval-augmented generation pipeline:

```
User Query
    ↓
Embed Query (384-dim vector)
    ↓
Search Pinecone (top-k similar documents)
    ↓
Build Prompt:
    [System Instructions]
    [Retrieved Context]
    [User Question]
    ↓
Send to LLaMA 3 8B
    ↓
Return Answer + Sources
```

**Key Features:**
- Automatic query embedding
- Semantic similarity search
- Prompt templating for clarity
- Source attribution

### 3. Vector Database Integration (`backend/vector_db.py`)

**PineconeVectorDB Class:**

```python
# Initialize
db = PineconeVectorDB(api_key="...", index_name="jarvis")

# Index documents
db.upsert_documents([
    {
        "id": "doc_001",
        "text": "...",
        "embedding": [...],  # 384-dim vector
        "source": "..."
    }
])

# Query for similar documents
results = db.query_top_k(query_embedding, top_k=5)
# Returns: [{"id": "...", "text": "...", "score": 0.92, "source": "..."}]
```

**How It Works:**
- Documents are stored as vectors in Pinecone
- Query is converted to same vector space
- Cosine similarity finds closest matches
- Top-k results are returned with metadata

### 4. Embeddings (`backend/embeddings.py`)

**Text-to-Vector Conversion:**

```python
from embeddings import embed_text, embed_batch

# Single text
embedding = embed_text("What is machine learning?")
# → [0.123, 0.456, ..., 0.789]  # 384-dimensional vector

# Multiple texts (faster)
embeddings = embed_batch(["text1", "text2", "text3"])
# → [[...], [...], [...]]
```

**Model: all-MiniLM-L6-v2**
- Dimension: 384
- Size: 22MB
- Speed: ~1000 texts/sec
- Quality: Excellent for semantic search
- Training: Fine-tuned on 1B sentence pairs

### 5. LLM Inference (`backend/llm.py`)

**OllamaLLM Wrapper:**

```python
llm = OllamaLLM(
    base_url="http://localhost:11434",
    model="llama3"
)

response = llm.generate(
    prompt="You are helpful assistant...",
    temperature=0.7,
    max_tokens=512
)
```

**Features:**
- Local inference (no API calls)
- Configurable temperature (creativity)
- Token limits
- Error handling for connection issues

**Why LLaMA 3 8B:**
- 8 billion parameters = good quality
- Fits in 16GB RAM
- Fast inference (~50-100 tokens/sec on consumer GPU)
- Excellent instruction-following
- Open source

### 6. Frontend (`frontend/app.py`)

**Streamlit Application:**

**Features:**
- Chat-style interface
- Message history
- Source document display
- Backend health check
- Configurable top-k parameter
- Responsive design

**Flow:**
1. User types query
2. Hits send button
3. Calls FastAPI backend
4. Displays answer and sources
5. Maintains conversation history

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT UI (Frontend)                  │
│                  - Chat interface                           │
│                  - Message history                          │
│                  - Source display                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │ HTTP POST /chat
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    FASTAPI BACKEND                          │
│                    main.py                                  │
│            - Accepts user query                             │
│            - Initializes RAG engine                         │
│            - Returns structured response                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    RAG ENGINE                               │
│                    rag.py                                   │
│  1. Embed query → 384-dim vector                            │
│  2. Search Pinecone → retrieve top-k docs                   │
│  3. Build RAG prompt with context                           │
│  4. Call Ollama LLM                                         │
│  5. Return answer + sources                                 │
└──┬──────────────────────────┬──────────────────────────┬────┘
   │                          │                          │
   ▼                          ▼                          ▼
┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ embeddings   │  │  vector_db       │  │  llm             │
│ .py          │  │  (Pinecone)      │  │  (Ollama)        │
│              │  │                  │  │                  │
│ - embed_text │  │ - query_top_k    │  │ - generate       │
│ - embed_batch│  │ - upsert_docs    │  │                  │
└──────────────┘  └──────────────────┘  └──────────────────┘
```

## Execution Flow Example

```
User: "What is RAG?"

1. FRONTEND
   Streamlit sends POST to /chat
   Body: {"query": "What is RAG?", "top_k": 5}

2. BACKEND (main.py)
   Receives request → creates ChatRequest object
   Calls: rag_engine.answer(query)

3. RAG ENGINE (rag.py)
   Step 1: Embed query
     query_embedding = embed_text("What is RAG?")
     → [0.15, 0.82, ..., 0.34]  (384-dim)
   
   Step 2: Retrieve documents
     docs = vector_db.query_top_k(query_embedding, top_k=5)
     → 5 documents about RAG
   
   Step 3: Build prompt
     prompt = """You are helpful assistant...
     
     CONTEXT:
     [Document 1] (source) RAG fundamentals text...
     [Document 2] (source) Vector DB primer text...
     [...]
     
     USER QUESTION:
     What is RAG?
     
     ANSWER:"""
   
   Step 4: Generate
     response = llm.generate(prompt)
     → "RAG is a technique that combines retrieval..."
   
   Step 5: Return result
     {
       "answer": "RAG is...",
       "sources": [
         {"id": "doc_004", "text": "RAG fundamentals..."},
         {"id": "doc_005", "text": "Vector DB primer..."},
         ...
       ],
       "context_count": 5
     }

4. BACKEND (main.py)
   Wraps response in ChatResponse model
   Sends HTTP 200 with JSON

5. FRONTEND (app.py)
   Receives response
   Displays answer
   Shows collapsible "Sources" section
   Adds to message history
```

## Why This Architecture?

### Retrieval (Pinecone)
- **Problem**: LLMs can hallucinate facts
- **Solution**: Retrieve relevant documents first
- **Benefit**: Answers are grounded in actual data

### Augmentation (Prompt Building)
- **Problem**: Raw query might be ambiguous
- **Solution**: Add context to the prompt
- **Benefit**: LLM has necessary information

### Generation (LLaMA 3)
- **Problem**: Cloud APIs are expensive
- **Solution**: Run LLM locally on Ollama
- **Benefit**: No API costs, full privacy

### Vector Database (Pinecone)
- **Problem**: Keyword search is unreliable
- **Solution**: Semantic search via embeddings
- **Benefit**: Finds similar content even with different words

## Key Design Principles

1. **Simplicity**: ~400 lines of core code
2. **Clarity**: Extensive comments in all files
3. **Production-Ready**: Error handling, logging, validation
4. **No Cloud Dependency**: Works offline (except Pinecone)
5. **Scalable**: Easy to add more documents or change models

## Configuration Points

### Model Selection
- Edit `OLLAMA_MODEL` in `.env` to switch models
- Available: llama3, mistral, neural-chat, etc.

### Embedding Model
- Edit `backend/embeddings.py` to use different model
- Alternative: all-mpnet-base-v2 (larger, more accurate)

### Retrieval Count
- UI slider controls `top_k` (1-10 documents)
- Higher = more context, slower response

### Temperature
- Controls creativity (0-1 range)
- Default: 0.7 (balanced)
- Lower = more deterministic

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Embed query | ~100ms | CPU-based, 384-dim |
| Pinecone search | ~200ms | Network + server |
| LLM generation | 5-10sec | Depends on response length |
| Total latency | ~6-11sec | Most time in LLM generation |

**To Optimize:**
- Use GPU for embeddings
- Reduce `max_tokens` in LLM
- Use smaller model (mistral 7B)
- Cache embeddings locally

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "Cannot connect to Ollama" | Server not running | `ollama serve` |
| "PINECONE_API_KEY not found" | Missing env var | Add to `.env` |
| "Index jarvis does not exist" | Index not created | Create in Pinecone UI |
| "Connection timeout" | Slow response | Check network/resources |

All errors are caught and returned as HTTP responses in the API.

## Security Considerations

1. **API Keys**: Store in `.env`, never in code
2. **Local Processing**: No data sent to external cloud
3. **Input Validation**: All user inputs are validated
4. **Error Messages**: Sanitized (no sensitive info leaks)

## Testing

To test manually:

```bash
# Terminal 1: Ollama
ollama serve

# Terminal 2: Backend
cd backend
python main.py

# Terminal 3: Index documents
cd data
python init_data.py

# Terminal 4: Test API
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Python?", "top_k": 5}'

# Terminal 5: Frontend
cd frontend
streamlit run app.py
```

## Future Enhancements

- [ ] User authentication
- [ ] Document management UI
- [ ] Multi-turn conversations with memory
- [ ] Document reranking for better retrieval
- [ ] Streaming responses
- [ ] Conversation export (PDF/JSON)
- [ ] Analytics dashboard
- [ ] Admin panel for index management
