"""
FastAPI backend for Jarvis personal assistant.
Exposes /chat endpoint for RAG-powered responses.
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Load environment variables from .env file
load_dotenv()

from backend.vector_db import PineconeVectorDB
from backend.llm import OllamaLLM
from backend.rag import RAGEngine
from backend.embeddings import embed_text, embed_batch, EMBEDDING_DIMENSION


# ============================================================================
# Pydantic Models for API
# ============================================================================

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    query: str
    top_k: Optional[int] = 5


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    answer: str
    sources: list[dict]
    context_count: int


class IndexRequest(BaseModel):
    """Request model for indexing documents."""
    documents: list[dict]  # Each doc must have 'id', 'text', 'source'


# ============================================================================
# Initialize FastAPI app
# ============================================================================

app = FastAPI(title="Jarvis - Personal AI Assistant")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Global RAG Engine Instance
# ============================================================================

_rag_engine: Optional[RAGEngine] = None


def get_rag_engine() -> RAGEngine:
    """Get or initialize the RAG engine (lazy initialization)."""
    global _rag_engine
    
    if _rag_engine is None:
        try:
            # Initialize Pinecone
            pinecone_db = PineconeVectorDB(
                api_key=os.getenv("PINECONE_API_KEY"),
                index_name="jarvis"
            )
            
            # Initialize Ollama LLM
            ollama_llm = OllamaLLM(
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                model=os.getenv("OLLAMA_MODEL", "llama3")
            )
            
            # Initialize RAG engine
            _rag_engine = RAGEngine(
                vector_db=pinecone_db,
                llm=ollama_llm,
                top_k=5
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize RAG engine: {str(e)}")
    
    return _rag_engine


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "Jarvis"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat endpoint: Accept query, retrieve context, generate response.
    
    Args:
        request: ChatRequest with 'query' and optional 'top_k'
        
    Returns:
        ChatResponse with answer, sources, and context count
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        rag_engine = get_rag_engine()
        
        # Use custom top_k if provided
        if request.top_k:
            rag_engine.top_k = request.top_k
        
        # Generate answer using RAG
        result = rag_engine.answer(request.query)
        
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            context_count=result["context_count"]
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index")
def index_documents(request: IndexRequest):
    """
    Index documents in Pinecone.
    Each document must have 'id', 'text', and optionally 'source'.
    
    Args:
        request: IndexRequest with list of documents
        
    Returns:
        Success message with document count
    """
    try:
        if not request.documents:
            raise ValueError("Documents list cannot be empty")
        
        # Embed all documents
        texts = [doc["text"] for doc in request.documents]
        embeddings = embed_batch(texts)
        
        # Attach embeddings to documents
        docs_with_embeddings = []
        for doc, embedding in zip(request.documents, embeddings):
            docs_with_embeddings.append({
                "id": doc["id"],
                "text": doc["text"],
                "embedding": embedding,
                "source": doc.get("source", "unknown")
            })
        
        # Upsert to Pinecone
        rag_engine = get_rag_engine()
        rag_engine.vector_db.upsert_documents(
            docs_with_embeddings,
            embedding_dimension=EMBEDDING_DIMENSION
        )
        
        return {
            "status": "success",
            "documents_indexed": len(request.documents),
            "message": f"Successfully indexed {len(request.documents)} documents"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize RAG engine on startup."""
    try:
        get_rag_engine()
        print("✓ RAG engine initialized successfully")
    except Exception as e:
        print(f"⚠ Warning: RAG engine initialization deferred: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    # Run with: python main.py
    # Or: uvicorn main:app --reload --host 0.0.0.0 --port 8000
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )
