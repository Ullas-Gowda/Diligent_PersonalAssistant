"""
RAG (Retrieval-Augmented Generation) engine.
Combines document retrieval with LLM generation.
"""

from typing import Optional
from backend.embeddings import embed_text
from backend.vector_db import PineconeVectorDB
from backend.llm import OllamaLLM


class RAGEngine:
    """Orchestrates RAG pipeline: embed → retrieve → generate."""
    
    def __init__(
        self,
        vector_db: PineconeVectorDB,
        llm: OllamaLLM,
        top_k: int = 5
    ):
        """
        Initialize RAG engine.
        
        Args:
            vector_db: PineconeVectorDB instance for retrieval
            llm: OllamaLLM instance for generation
            top_k: Number of documents to retrieve
        """
        self.vector_db = vector_db
        self.llm = llm
        self.top_k = top_k
    
    def _build_rag_prompt(
        self,
        query: str,
        retrieved_docs: list[dict]
    ) -> str:
        """
        Build the final prompt combining context and query.
        
        Args:
            query: User's question
            retrieved_docs: Retrieved documents from Pinecone
            
        Returns:
            Formatted prompt for the LLM
        """
        # Format retrieved documents as context
        context_text = "\n\n".join([
            f"[Document {i+1}] ({doc['source']})\n{doc['text']}"
            for i, doc in enumerate(retrieved_docs)
        ])
        
        # Build the prompt with explicit instructions
        prompt = f"""You are a helpful personal assistant named Jarvis.
Use the provided context to answer the user's question accurately.
If the context doesn't contain relevant information, say "I don't have enough information to answer that."
Do not make up information.

---
CONTEXT:
{context_text}

---
USER QUESTION:
{query}

---
ANSWER:
"""
        return prompt
    
    def answer(self, query: str) -> dict:
        """
        Generate an answer using RAG pipeline.
        
        Args:
            query: User's question
            
        Returns:
            Dict with 'answer', 'sources', and 'context_count'
        """
        # Step 1: Embed the query
        query_embedding = embed_text(query)
        
        # Step 2: Retrieve relevant documents
        retrieved_docs = self.vector_db.query_top_k(
            query_embedding,
            top_k=self.top_k
        )
        
        # Step 3: Build RAG prompt
        rag_prompt = self._build_rag_prompt(query, retrieved_docs)
        
        # Step 4: Generate response
        answer_text = self.llm.generate(
            prompt=rag_prompt,
            temperature=0.7,
            max_tokens=512
        )
        
        # Step 5: Return structured response
        return {
            "answer": answer_text,
            "sources": [
                {"text": doc["text"][:100] + "...", "id": doc["id"]}
                for doc in retrieved_docs
            ],
            "context_count": len(retrieved_docs)
        }
