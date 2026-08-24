import streamlit as st
import re
from src.hybrid_retrieval import hybrid_retrieve_context
from src.llm import generate_answer
from src.config import settings

st.set_page_config(page_title="Atman Cloud RAG Q&A", page_icon="📚", layout="centered")

st.title("📚 Document Q&A System")
st.markdown("Ask questions about your uploaded documents. The AI will answer using the provided context and cite its sources.")

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

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Searching documents and generating answer..."):
            retrieval_result = hybrid_retrieve_context(prompt, k=3)
            
            if retrieval_result["is_empty_db"]:
                assistant_response = "⚠️ The document database is currently empty. Please add PDF files to `data/documents/` and run `python ingest.py`."
            elif retrieval_result["error"]:
                assistant_response = f"❌ An error occurred: {retrieval_result['error']}"
            else:
                context = retrieval_result["context"]
                conversation_history = st.session_state.messages[-6:]
                
                result = generate_answer(prompt, context, conversation_history)
                assistant_response = result["answer"]
                
                st.markdown(assistant_response)
                
                # SMART SOURCE FILTERING: Only show if citations exist and it's not a refusal
                has_citations = bool(re.search(r'(?:\[|【)\d+(?:\]|】)', assistant_response))
                is_refusal = "cannot find" in assistant_response.lower() or "could not find" in assistant_response.lower()
                
                if has_citations and not is_refusal and result["citations"]:
                    st.markdown("---")
                    st.markdown("**📎 Sources:**")
                    for source in result["citations"]:
                        st.markdown(f"- `{source}`")
                        
    st.session_state.messages.append({
        "role": "assistant", 
        "content": assistant_response
    })