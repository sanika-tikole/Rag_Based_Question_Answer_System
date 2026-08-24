from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.utils import setup_logger
from src.config import settings

logger = setup_logger(__name__)

def chunk_documents(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Splits extracted documents into smaller, overlapping chunks.
    
    Args:
        documents: List of dictionaries containing 'source', 'text', and 'page_count'.
        
    Returns:
        A list of chunk dictionaries with added 'chunk_id' and 'metadata'.
    """
    if not documents:
        logger.warning("No documents provided for chunking.")
        return []

    logger.info(f"Starting chunking process for {len(documents)} document(s)...")
    logger.info(f"Using chunk_size={settings.chunk_size}, chunk_overlap={settings.chunk_overlap}")

    # Initialize the recursive text splitter
    # It tries to split by paragraphs (\n\n), then sentences (.), then words ( )
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )

    all_chunks = []
    total_original_chars = 0
    total_chunk_chars = 0

    for doc in documents:
        source = doc["source"]
        text = doc["text"]
        page_count = doc.get("page_count", 0)
        
        total_original_chars += len(text)
        
        # Split the text into chunks
        split_texts = text_splitter.split_text(text)
        
        for i, chunk_text in enumerate(split_texts):
            total_chunk_chars += len(chunk_text)
            
            chunk = {
                "chunk_id": f"{source}_chunk_{i}",
                "source": source,
                "page_count": page_count,
                "chunk_index": i,
                "text": chunk_text,
                "metadata": {
                    "source": source,
                    "chunk_index": i,
                    "page_count": page_count
                }
            }
            all_chunks.append(chunk)
            
    logger.info(f"Chunking complete! Split {total_original_chars} characters into {len(all_chunks)} chunks.")
    return all_chunks