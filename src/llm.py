import re
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
    """
    # 1. INTERCEPT GREETINGS EARLY
    lower_query = query.lower().strip()
    greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "how are you", "greetings"]
    
    is_greeting = any(
        lower_query == g or 
        lower_query.startswith(g + " ") or 
        lower_query.startswith(g + ",") 
        for g in greetings
    )
    
    if is_greeting and len(lower_query.split()) <= 4:
        return {
            "answer": "Hello! 👋 I'm your Atman Cloud Document Q&A assistant. How can I help you with our products, policies, or API today?",
            "citations": []
        }

    # 2. HANDLE EMPTY CONTEXT
    if not context:
        return {
            "answer": "I could not find any relevant information in the documents to answer your question.",
            "citations": []
        }

    # 3. FORMAT CONTEXT WITH CITATION MARKERS
    context_str = ""
    for i, chunk in enumerate(context):
        context_str += f"[{i+1}] Source: {chunk['source']}\nText: {chunk['text']}\n\n"
        
    # 4. CONSTRUCT STRICT SYSTEM PROMPT
    system_prompt = f"""You are a helpful and precise AI assistant. 
Answer the user's question based ONLY on the provided context. 
If the context does not contain the answer, state clearly: "I cannot find the answer in the provided documents."

CRITICAL RULE: You MUST cite your sources using simple brackets like [1], [2], etc., corresponding to the context provided. 
DO NOT use complex citation formats like 【1†L1-L2】 or (Source 1). Use ONLY [1], [2], etc.

Context:
{context_str}
"""

    # 5. BUILD MESSAGES LIST
    messages = [{"role": "system", "content": system_prompt}]
    
    if conversation_history:
        for msg in conversation_history:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
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
        
        # 6. DYNAMIC CITATION MAPPING (THE FIX)
        # Find all citation numbers the AI actually used in its answer (e.g., [1], [2], or 【1】)
        cited_numbers = re.findall(r'(?:\[|【)(\d+)(?:\]|】)', answer)
        
        # Map those numbers back to the specific source files
        used_sources = set()
        for num_str in cited_numbers:
            idx = int(num_str) - 1  # Convert 1-based citation to 0-based list index
            if 0 <= idx < len(context):
                used_sources.add(context[idx]['source'])
        
        return {
            "answer": answer,
            "citations": list(used_sources)  # Only return sources actually cited!
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Groq API error: {error_msg}")
        
        return {
            "answer": f"❌ **Error from Groq API:**\n\n```\n{error_msg}\n```\n\nPlease check:\n1. Your API key is valid\n2. The model name `{settings.llm_model_name}` exists\n3. You have access to this model on your Groq account",
            "citations": []
        }