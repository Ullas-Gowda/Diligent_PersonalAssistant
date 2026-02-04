"""
Embedding generation module using sentence-transformers.
Converts text to dense vectors for semantic search.
"""

from sentence_transformers import SentenceTransformer

# Initialize the embedding model (lightweight, fast)
# all-MiniLM-L6-v2 is 22MB and works great for semantic search
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
EMBEDDING_DIMENSION = 384  # Output dimension of all-MiniLM-L6-v2


def embed_text(text: str) -> list[float]:
    """
    Generate embedding for a single text.
    
    Args:
        text: Input text to embed
        
    Returns:
        List of floats representing the embedding vector
    """
    embedding = EMBEDDING_MODEL.encode(text, convert_to_tensor=False)
    return embedding.tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for multiple texts (batch processing).
    More efficient than processing one at a time.
    
    Args:
        texts: List of texts to embed
        
    Returns:
        List of embedding vectors
    """
    embeddings = EMBEDDING_MODEL.encode(texts, convert_to_tensor=False)
    return [emb.tolist() for emb in embeddings]
