"""
Sample data initialization script.
Indexes sample documents into Pinecone for testing.
Run this once before starting the app.
"""

import requests
import json


# Sample knowledge base documents
SAMPLE_DOCUMENTS = [
    {
        "id": "doc_001",
        "text": """Python is a high-level, interpreted programming language known for its simplicity 
        and readability. It was created by Guido van Rossum in 1991. Python is used for web development, 
        data science, machine learning, automation, and many other applications.""",
        "source": "Python Basics"
    },
    {
        "id": "doc_002",
        "text": """FastAPI is a modern web framework for building APIs with Python. It's built on top of 
        Starlette and Pydantic. FastAPI is extremely fast, easy to use, and great for production applications. 
        It automatically generates interactive API documentation.""",
        "source": "FastAPI Guide"
    },
    {
        "id": "doc_003",
        "text": """Machine learning is a subset of artificial intelligence that enables systems to learn 
        and improve from experience without being explicitly programmed. Common techniques include supervised learning, 
        unsupervised learning, and reinforcement learning.""",
        "source": "ML Concepts"
    },
    {
        "id": "doc_004",
        "text": """RAG (Retrieval-Augmented Generation) combines information retrieval with text generation. 
        It retrieves relevant documents from a database and uses them to augment the prompt for a language model, 
        reducing hallucinations and improving answer quality.""",
        "source": "RAG Fundamentals"
    },
    {
        "id": "doc_005",
        "text": """Vector databases like Pinecone store embeddings and enable semantic search. 
        They convert text to dense vectors and find similar items quickly using metrics like cosine similarity. 
        This is essential for RAG systems.""",
        "source": "Vector DB Primer"
    },
    {
        "id": "doc_006",
        "text": """Ollama is a tool for running large language models locally on your machine. 
        It simplifies the process of downloading and running models like LLaMA, Mistral, and others without needing cloud APIs.""",
        "source": "Ollama Intro"
    },
    {
        "id": "doc_007",
        "text": """Streamlit is a Python library for quickly building and sharing web apps for machine learning and data science. 
        It allows you to turn Python scripts into interactive web apps with minimal code.""",
        "source": "Streamlit Basics"
    },
    {
        "id": "doc_008",
        "text": """Embeddings are dense vector representations of text. Modern embedding models like sentence-transformers 
        convert sentences into fixed-size vectors that capture semantic meaning, enabling similarity comparisons.""",
        "source": "Embeddings Explained"
    }
]


def index_sample_documents(backend_url: str = "http://localhost:8000"):
    """
    Upload sample documents to the backend for indexing.
    
    Args:
        backend_url: URL of the FastAPI backend
    """
    try:
        response = requests.post(
            f"{backend_url}/index",
            json={"documents": SAMPLE_DOCUMENTS},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✓ Sample documents indexed successfully!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.text)
    
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to backend at {backend_url}")
        print("Make sure the FastAPI server is running on localhost:8000")
    except Exception as e:
        print(f"✗ Error: {str(e)}")


if __name__ == "__main__":
    print("Indexing sample documents...")
    index_sample_documents()
