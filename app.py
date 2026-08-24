import streamlit as st
import re  # <-- Added for smart source filtering
from src.hybrid_retrieval import hybrid_retrieve_context
from src.llm import generate_answer
from src.config import settings

# Page configuration
st.set_page_config(page_title="Atman Cloud RAG Q&A", page_icon="📚", layout="centered")

st.title("📚 Document Q&A System")
st.markdown("Ask questions about your uploaded documents. The AI will answer using the provided context and cite its sources.")

# Sidebar for configuration/status
with st.sidebar:
    st.header("System Status")
    st.info(f"LLM Provider: **{settings.llm_provider.upper()}**")
    st.info(f"Model: **{settings.llm_model_name}**")
    st.info(f"Embedding Model: **{settings.embedding_model_name}**")
    st.info(f"Retrieval: **Hybrid (BM25 + Semantic)**")
    
   
    st.divider()
    st.markdown("### Conversation")
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Generate AI response
    with st.chat_message("assistant"):
        with st.spinner("Searching documents and generating answer..."):
            # 1. Retrieve with hybrid search
            retrieval_result = hybrid_retrieve_context(prompt, k=3)
            
            if retrieval_result["is_empty_db"]:
                st.warning("⚠️ The document database is currently empty.")
                st.markdown("Please add PDF files to the `data/documents/` folder and run `python ingest.py` in your terminal to process them.")
                assistant_response = "The document database is empty. Please ingest documents first."
            elif retrieval_result["error"]:
                st.error(f"❌ An error occurred while searching the database: {retrieval_result['error']}")
                assistant_response = "Sorry, I encountered an error while searching the documents."
            else:
                # 2. Generate with conversation history
                context = retrieval_result["context"]
                
                # Build conversation history (last 3 turns to avoid token overflow)
                conversation_history = []
                for msg in st.session_state.messages[-6:]:
                    conversation_history.append(msg)
                
                result = generate_answer(prompt, context, conversation_history)
                assistant_response = result["answer"]
                
                # 3. Display Answer
                st.markdown(assistant_response)
                
                # 4. Display Citations (SMART FILTERING)
                # Check if the answer actually contains citation markers like [1], [2], etc.
                has_citations = bool(re.search(r'\[\d+\]', assistant_response))
                
                # Check if the LLM refused to answer (e.g., "I cannot find the answer...")
                is_refusal = "cannot find" in assistant_response.lower() or "could not find" in assistant_response.lower()
                
                # Only show the Sources section if it cited them AND didn't refuse
                if has_citations and not is_refusal and result["citations"]:
                    st.markdown("---")
                    st.markdown("**📎 Sources:**")
                    for source in result["citations"]:
                        st.markdown(f"- `{source}`")
                        
    # Add AI message to state
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})