from typing import List
from sentence_transformers import SentenceTransformer

from src.utils import setup_logger
from src.config import settings

logger = setup_logger(__name__)

# Initialize the model globally so it's only loaded once
logger.info(f"Loading embedding model: {settings.embedding_model_name}...")
embedding_model = SentenceTransformer(settings.embedding_model_name)
logger.info("Embedding model loaded successfully.")

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generates embeddings for a list of text chunks.
    
    Args:
        texts: List of text strings to embed.
        
    Returns:
        List of embedding vectors (list of lists of floats).
    """
    if not texts:
        logger.warning("No texts provided for embedding generation.")
        return []
    
    logger.info(f"Generating embeddings for {len(texts)} chunks...")
    
    # encode() automatically handles batching and returns a list of numpy arrays.
    # We convert them to standard Python lists for ChromaDB compatibility.
    embeddings = embedding_model.encode(texts, show_progress_bar=False).tolist()
    
    logger.info("Embedding generation complete.")
    return embeddings