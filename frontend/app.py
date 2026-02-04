"""
Streamlit chatbot UI for Jarvis personal assistant.
Connects to FastAPI backend and displays chat interface.

Run with: streamlit run app.py
"""

import streamlit as st
import requests
import json
from datetime import datetime


# ============================================================================
# Configuration
# ============================================================================

BACKEND_URL = "http://localhost:8000"
PAGE_TITLE = "Jarvis - Personal AI Assistant"
PAGE_ICON = "🤖"

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# Styling
# ============================================================================

st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 1rem;
    }
    
    /* Chat messages */
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        font-size: 0.95rem;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Sidebar
# ============================================================================

with st.sidebar:
    st.title("⚙️ Settings")
    
    # Backend health check
    try:
        health_response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        if health_response.status_code == 200:
            st.success("✓ Backend Connected", icon="✅")
        else:
            st.error("✗ Backend Error", icon="⚠️")
    except:
        st.error("✗ Cannot reach backend", icon="⚠️")
        st.info("Ensure FastAPI server is running on localhost:8000")
    
    st.divider()
    
    # Configuration parameters
    top_k = st.slider(
        "Retrieve top-k documents",
        min_value=1,
        max_value=10,
        value=5,
        help="Number of relevant documents to retrieve for context"
    )
    
    st.divider()
    
    # Instructions
    st.markdown("""
    ### 📖 Instructions
    
    1. **Type your question** in the input box below
    2. **Hit Enter** or click the send button
    3. Jarvis will retrieve relevant documents and generate an answer
    4. **Sources** are displayed for transparency
    
    ### 🔧 System Info
    - **Model**: LLaMA 3 8B (via Ollama)
    - **Embeddings**: all-MiniLM-L6-v2
    - **Vector DB**: Pinecone
    - **Inference**: Local + Semantic Search
    """)

# ============================================================================
# Initialize Session State
# ============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "show_sources" not in st.session_state:
    st.session_state.show_sources = {}

# ============================================================================
# Main Chat Interface
# ============================================================================

st.title(f"{PAGE_ICON} {PAGE_TITLE}")
st.write("Ask me anything! I'll search my knowledge base and provide accurate answers.")

# Display chat history
chat_container = st.container()

with chat_container:
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(
                f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message['content']}
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="chat-message assistant-message">
                    <strong>🤖 Jarvis:</strong> {message['content']}
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Show sources if available
            if message.get("sources"):
                with st.expander(f"📚 Sources ({len(message['sources'])} documents)"):
                    for j, source in enumerate(message["sources"], 1):
                        st.write(f"**Document {j}** (ID: {source['id']})")
                        st.write(f"> {source['text']}")
                        st.divider()

# ============================================================================
# Input Handler
# ============================================================================

st.divider()

# Input form
col1, col2 = st.columns([20, 1])

with col1:
    user_input = st.text_input(
        "Ask a question:",
        placeholder="What is RAG? How does Ollama work? Tell me about Python...",
        label_visibility="collapsed"
    )

with col2:
    send_button = st.button("📤", help="Send message")

# Process input
if send_button and user_input.strip():
    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Show thinking indicator
    with st.spinner("🤔 Thinking..."):
        try:
            # Call backend API
            response = requests.post(
                f"{BACKEND_URL}/chat",
                json={
                    "query": user_input,
                    "top_k": top_k
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Add assistant response to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result["sources"],
                    "context_count": result["context_count"]
                })
                
                # Rerun to display new messages
                st.rerun()
            
            else:
                st.error(f"Backend error: {response.status_code}")
                st.write(response.text)
        
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Backend may be slow or unresponsive.")
        except requests.exceptions.ConnectionError:
            st.error(
                "❌ Cannot connect to backend. "
                "Make sure FastAPI server is running on localhost:8000"
            )
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# ============================================================================
# Footer
# ============================================================================

st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #666; font-size: 0.85rem; margin-top: 2rem;">
        <p>Jarvis - Personal AI Assistant | Built with Streamlit, FastAPI, and Ollama</p>
        <p>Using RAG with Pinecone for accurate, source-backed answers</p>
    </div>
    """,
    unsafe_allow_html=True
)
