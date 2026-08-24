from typing import List, Dict, Any
from groq import Groq

from src.config import settings
from src.utils import setup_logger

logger = setup_logger(__name__)

if not settings.groq_api_key:
    logger.warning("GROQ_API_KEY is not set. LLM generation will fail.")
    
groq_client = Groq(api_key=settings.groq_api_key)

def generate_answer(query: str, context: List[Dict[str, Any]], conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Generates an answer using Groq based on the retrieved context and conversation history.
    
    Args:
        query: The user's question.
        context: List of retrieved chunks.
        conversation_history: Optional list of previous messages for context.
        
    Returns:
        A dictionary containing the 'answer' and 'citations' (list of sources).
    """
    if not context:
        return {
            "answer": "I could not find any relevant information in the documents to answer your question.",
            "citations": []
        }

    # Format context into a readable string with citation markers
    context_str = ""
    sources = set()
    for i, chunk in enumerate(context):
        context_str += f"[{i+1}] Source: {chunk['source']}\nText: {chunk['text']}\n\n"
        sources.add(chunk['source'])
        
    # Construct the system prompt
    system_prompt = f"""You are a helpful and precise AI assistant. 
Answer the user's question based ONLY on the provided context. 
If the context does not contain the answer, state clearly: "I cannot find the answer in the provided documents."
Always cite your sources using the format [1], [2], etc., corresponding to the context provided.

Context:
{context_str}
"""

    # Build messages list with conversation history
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history (if provided)
    if conversation_history:
        for msg in conversation_history:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Add current query
    messages.append({"role": "user", "content": query})

    logger.info(f"Sending request to Groq (Model: {settings.llm_model_name})...")
    
    try:
        response = groq_client.chat.completions.create(
            model=settings.llm_model_name,
            messages=messages,
            temperature=settings.llm_temperature,
            max_tokens=1024
        )
        
        answer = response.choices[0].message.content.strip()
        logger.info("Successfully generated answer from Groq.")
        
        return {
            "answer": answer,
            "citations": list(sources)
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Groq API error: {error_msg}")
        
        return {
            "answer": f"❌ **Error from Groq API:**\n\n```\n{error_msg}\n```\n\nPlease check:\n1. Your API key is valid\n2. The model name `{settings.llm_model_name}` exists\n3. You have access to this model on your Groq account",
            "citations": []
        }