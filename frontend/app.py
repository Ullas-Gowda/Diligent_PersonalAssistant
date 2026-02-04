"""
Enterprise Knowledge Assistant UI - Streamlit Implementation
Connects to FastAPI backend for product knowledge and support.

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
PAGE_TITLE = "Knowledge Assistant"

st.set_page_config(
    page_title=PAGE_TITLE,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# Professional Styling
# ============================================================================

st.markdown("""
<style>
    /* Remove default styling */
    .main {
        padding: 2rem 1rem;
    }
    
    /* Header styling */
    .header-section {
        background: linear-gradient(135deg, #0d47a1 0%, #1565c0 100%);
        border: 3px solid #0d47a1;
        padding: 2rem 1.5rem;
        margin-bottom: 2rem;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(13, 71, 161, 0.3);
    }
    
    .header-title {
        font-size: 36px;
        font-weight: 900;
        color: #ffffff;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .header-subtitle {
        font-size: 14px;
        color: #e3f2fd;
        margin-top: 0.75rem;
        font-weight: 500;
    }
    
    /* Two-column layout */
    .content-wrapper {
        display: flex;
        gap: 2rem;
    }
    
    .left-panel {
        flex: 0 0 320px;
        min-height: 600px;
    }
    
    .right-panel {
        flex: 1;
    }
    
    /* Panel styling */
    .panel-header {
        font-size: 16px;
        font-weight: 900;
        color: #ffffff;
        background: linear-gradient(135deg, #1976d2 0%, #2196f3 100%);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 1.5rem;
        padding: 1rem 1.25rem;
        border-radius: 6px;
        box-shadow: 0 2px 8px rgba(25, 118, 210, 0.4);
    }
    
    .source-item {
        background: linear-gradient(135deg, #e3f2fd 0%, #f5f5f5 100%);
        border: 2px solid #1976d2;
        border-radius: 6px;
        padding: 1rem;
        margin-bottom: 1rem;
        font-size: 12px;
        box-shadow: 0 2px 6px rgba(25, 118, 210, 0.15);
    }
    
    .source-item-title {
        font-weight: 900;
        color: #0d47a1;
        margin-bottom: 0.75rem;
        font-size: 13px;
    }
    
    .source-item-text {
        color: #1a1a1a;
        line-height: 1.5;
        font-weight: 500;
    }
    
    /* Query/Response cards */
    .query-card {
        background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
        border: 2px solid #2e7d32;
        border-left: 5px solid #43a047;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border-radius: 6px;
        box-shadow: 0 2px 8px rgba(46, 125, 50, 0.15);
    }
    
    .query-label {
        font-size: 12px;
        font-weight: 900;
        color: #1b5e20;
        background: #c8e6c9;
        padding: 0.5rem 0.75rem;
        border-radius: 4px;
        text-transform: uppercase;
        margin-bottom: 0.75rem;
        display: inline-block;
        letter-spacing: 0.5px;
    }
    
    .query-text {
        font-size: 14px;
        color: #1a1a1a;
        line-height: 1.6;
        font-weight: 500;
    }
    
    .response-card {
        background: linear-gradient(135deg, #e1f5fe 0%, #f5f5f5 100%);
        border: 2px solid #0277bd;
        border-left: 5px solid #0288d1;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border-radius: 6px;
        box-shadow: 0 2px 8px rgba(2, 119, 189, 0.15);
    }
    
    .response-label {
        font-size: 12px;
        font-weight: 900;
        color: #01579b;
        background: #b3e5fc;
        padding: 0.5rem 0.75rem;
        border-radius: 4px;
        text-transform: uppercase;
        margin-bottom: 0.75rem;
        display: inline-block;
        letter-spacing: 0.5px;
    }
    
    .response-text {
        font-size: 14px;
        color: #1a1a1a;
        line-height: 1.6;
        font-weight: 500;
    }
    
    /* Input section */
    .input-section {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        padding: 1.5rem;
        margin-top: 2rem;
    }
    
    .input-label {
        font-size: 12px;
        font-weight: 600;
        color: #666;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }
    
    /* Status indicators */
    .status-online {
        display: inline-block;
        width: 8px;
        height: 8px;
        background: #4caf50;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    
    .status-text {
        font-size: 12px;
        color: #666;
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 2rem;
        color: #999;
    }
    
    .empty-state-text {
        font-size: 14px;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Initialize Session State
# ============================================================================

if "queries" not in st.session_state:
    st.session_state.queries = []

if "responses" not in st.session_state:
    st.session_state.responses = []

if "context_history" not in st.session_state:
    st.session_state.context_history = []

if "backend_healthy" not in st.session_state:
    st.session_state.backend_healthy = False


# ============================================================================
# Check Backend Health
# ============================================================================

def check_backend():
    """Check if backend is available."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


st.session_state.backend_healthy = check_backend()


# ============================================================================
# Header Section
# ============================================================================

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("""
    <div class="header-section">
        <div class="header-title">Knowledge Assistant</div>
        <div class="header-subtitle">Internal Product Knowledge & Support</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if st.session_state.backend_healthy:
        st.markdown("""
        <div style="text-align: right; padding-top: 1rem;">
            <span class="status-online"></span>
            <span class="status-text">Service Online</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: right; padding-top: 1rem; color: #d32f2f;">
            <span style="display: inline-block; width: 8px; height: 8px; background: #d32f2f; border-radius: 50%; margin-right: 0.5rem;"></span>
            <span class="status-text">Service Unavailable</span>
        </div>
        """, unsafe_allow_html=True)


# ============================================================================
# Main Content Area
# ============================================================================

if not st.session_state.backend_healthy:
    st.error("⚠️ Service unavailable. Ensure the backend is running on localhost:8000")
else:
    # Create two-column layout
    left_col, right_col = st.columns([1, 2], gap="large")
    
    # ========================================================================
    # LEFT PANEL: Knowledge Sources / Context
    # ========================================================================
    
    with left_col:
        st.markdown('<div class="panel-header">Retrieved Context</div>', unsafe_allow_html=True)
        
        if not st.session_state.context_history:
            st.markdown("""
            <div class="empty-state">
                <div style="font-size: 24px;">📋</div>
                <div class="empty-state-text">No queries yet.<br>Context will appear here.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Show most recent context
            latest_context = st.session_state.context_history[-1]
            
            if latest_context:
                for idx, source in enumerate(latest_context, 1):
                    st.markdown(f"""
                    <div class="source-item">
                        <div class="source-item-title">Source {idx}</div>
                        <div class="source-item-text">{source['text'][:150]}...</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # ========================================================================
    # RIGHT PANEL: Conversation
    # ========================================================================
    
    with right_col:
        st.markdown('<div class="panel-header">Query History</div>', unsafe_allow_html=True)
        
        # Display conversation history
        conversation_container = st.container()
        
        with conversation_container:
            if not st.session_state.queries:
                st.markdown("""
                <div class="empty-state">
                    <div style="font-size: 32px;">🔍</div>
                    <div class="empty-state-text">No queries submitted yet.<br>Ask a question to get started.</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                for i, (query, response) in enumerate(zip(st.session_state.queries, st.session_state.responses)):
                    # User Query Card
                    st.markdown(f"""
                    <div class="query-card">
                        <div class="query-label">User Query</div>
                        <div class="query-text">{query}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # System Response Card
                    st.markdown(f"""
                    <div class="response-card">
                        <div class="response-label">System Response</div>
                        <div class="response-text">{response}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Input Section
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.markdown('<div class="input-label">New Query</div>', unsafe_allow_html=True)
        
        user_input = st.text_input(
            label="Query input",
            placeholder="Search internal knowledge or ask a product question",
            label_visibility="collapsed"
        )
        
        col_submit, col_clear = st.columns([3, 1])
        
        with col_submit:
            submit_button = st.button("Get Answer", use_container_width=True, type="primary")
        
        with col_clear:
            if st.button("Clear History", use_container_width=True):
                st.session_state.queries = []
                st.session_state.responses = []
                st.session_state.context_history = []
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ====================================================================
        # Process User Input
        # ====================================================================
        
        if submit_button and user_input.strip():
            with st.spinner("Retrieving knowledge and generating response..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/chat",
                        json={
                            "query": user_input,
                            "top_k": 3
                        },
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Store in session state
                        st.session_state.queries.append(user_input)
                        st.session_state.responses.append(result["answer"])
                        st.session_state.context_history.append(result["sources"])
                        
                        st.rerun()
                    
                    else:
                        st.error(f"Error: {response.status_code}")
                        st.write(response.text)
                
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. Please try again.")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


# ============================================================================
# Footer
# ============================================================================

st.divider()
st.markdown("""
<div style="text-align: center; color: #999; font-size: 12px; margin-top: 2rem;">
    <p>Enterprise Knowledge Assistant | Powered by Advanced Retrieval & Generation</p>
    <p>© 2026 | All rights reserved</p>
</div>
""", unsafe_allow_html=True)
