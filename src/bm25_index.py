"""
BM25 keyword search index for hybrid retrieval.
"""
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
import pickle
from pathlib import Path

from src.config import settings
from src.utils import setup_logger

logger = setup_logger(__name__)

# Path to persist the BM25 index
BM25_INDEX_PATH = Path(settings.chroma_persist_dir) / "bm25_index.pkl"

def build_bm25_index(chunks: List[Dict[str, Any]]) -> None:
    """
    Builds a BM25 index from text chunks and saves it to disk.
    
    Args:
        chunks: List of chunk dictionaries with 'text' and 'metadata' keys.
    """
    if not chunks:
        logger.warning("No chunks provided to build BM25 index.")
        return
    
    logger.info(f"Building BM25 index for {len(chunks)} chunks...")
    
    # Extract text and tokenize (simple whitespace + lowercase)
    corpus = [chunk["text"].lower().split() for chunk in chunks]
    
    # Build BM25 index
    bm25 = BM25Okapi(corpus)
    
    # Save index and metadata to disk
    index_data = {
        "bm25": bm25,
        "chunks": chunks,
        "corpus": corpus
    }
    
    BM25_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(BM25_INDEX_PATH, "wb") as f:
        pickle.dump(index_data, f)
    
    logger.info(f"BM25 index saved to {BM25_INDEX_PATH}")


def load_bm25_index():
    """
    Loads the BM25 index from disk.
    
    Returns:
        Tuple of (BM25Okapi instance, list of chunks) or (None, None) if not found.
    """
    if not BM25_INDEX_PATH.exists():
        logger.warning(f"BM25 index not found at {BM25_INDEX_PATH}")
        return None, None
    
    logger.info(f"Loading BM25 index from {BM25_INDEX_PATH}...")
    with open(BM25_INDEX_PATH, "rb") as f:
        index_data = pickle.load(f)
    
    return index_data["bm25"], index_data["chunks"]


def bm25_search(query: str, k: int = 10) -> List[Dict[str, Any]]:
    """
    Performs BM25 keyword search and returns top-k results.
    
    Args:
        query: The search query.
        k: Number of results to return.
        
    Returns:
        List of chunk dictionaries with added 'bm25_score' key.
    """
    bm25, chunks = load_bm25_index()
    
    if bm25 is None or chunks is None:
        logger.warning("BM25 index not available. Returning empty results.")
        return []
    
    # Tokenize query
    query_tokens = query.lower().split()
    
    # Get BM25 scores
    scores = bm25.get_scores(query_tokens)
    
    # Get top-k indices
    top_k_indices = scores.argsort()[-k:][::-1]
    
    # Format results
    results = []
    for idx in top_k_indices:
        chunk = chunks[idx].copy()
        chunk["bm25_score"] = float(scores[idx])
        results.append(chunk)
    
    logger.info(f"BM25 search returned {len(results)} results for query: '{query[:50]}...'")
    return results