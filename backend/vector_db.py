"""
Pinecone vector database integration.
Handles document indexing and semantic search.
"""

import os
from typing import Optional
from pinecone import Pinecone


class PineconeVectorDB:
    """Wrapper for Pinecone vector database operations."""
    
    def __init__(self, api_key: Optional[str] = None, index_name: str = "jarvis"):
        """
        Initialize Pinecone client.
        
        Args:
            api_key: Pinecone API key (default: from PINECONE_API_KEY env var)
            index_name: Name of the index to use
        """
        if api_key is None:
            api_key = os.getenv("PINECONE_API_KEY")
            if not api_key:
                raise ValueError(
                    "PINECONE_API_KEY not found. Set it as environment variable."
                )
        
        self.client = Pinecone(api_key=api_key)
        self.index_name = index_name
        
        # Initialize or get the index
        self.index = self.client.Index(index_name)
    
    def upsert_documents(
        self,
        documents: list[dict],
        embedding_dimension: int = 384
    ) -> None:
        """
        Upsert documents (embeddings) into Pinecone.
        
        Args:
            documents: List of dicts with 'id', 'text', and 'embedding' keys
            embedding_dimension: Expected dimension of embeddings
        """
        vectors_to_upsert = []
        
        for doc in documents:
            vector_tuple = (
                doc["id"],  # Unique ID
                doc["embedding"],  # The embedding vector
                {
                    "text": doc["text"],  # Store original text as metadata
                    "source": doc.get("source", "unknown")
                }
            )
            vectors_to_upsert.append(vector_tuple)
        
        # Upsert in batches of 100 to avoid timeouts
        batch_size = 100
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i : i + batch_size]
            self.index.upsert(vectors=batch)
        
        print(f"✓ Upserted {len(documents)} documents to Pinecone")
    
    def query_top_k(self, query_embedding: list[float], top_k: int = 5) -> list[dict]:
        """
        Retrieve top-k most similar documents from Pinecone.
        
        Args:
            query_embedding: The embedding vector of the query
            top_k: Number of results to return
            
        Returns:
            List of dicts with 'text', 'score', and 'id' keys
        """
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        formatted_results = []
        for match in results["matches"]:
            formatted_results.append({
                "id": match["id"],
                "text": match["metadata"].get("text", ""),
                "score": match["score"],
                "source": match["metadata"].get("source", "unknown")
            })
        
        return formatted_results
