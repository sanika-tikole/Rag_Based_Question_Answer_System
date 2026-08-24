"""
Hybrid retrieval combining BM25 (keyword) and semantic (vector) search.
Uses Reciprocal Rank Fusion (RRF) to combine results.
"""
from typing import List, Dict, Any
from collections import defaultdict

from src.config import settings
from src.retrieval import retrieve_context as semantic_search
from src.bm25_index import bm25_search
from src.utils import setup_logger

logger = setup_logger(__name__)

def reciprocal_rank_fusion(
    semantic_results: List[Dict[str, Any]],
    bm25_results: List[Dict[str, Any]],
    k: int = 60,  # RRF constant (higher = more weight to lower ranks)
    top_n: int = 3
) -> List[Dict[str, Any]]:
    """
    Combines two ranked lists using Reciprocal Rank Fusion.
    
    RRF score = sum(1 / (k + rank_i)) for each list i where the document appears.
    
    Args:
        semantic_results: Results from semantic search (ranked by similarity).
        bm25_results: Results from BM25 search (ranked by BM25 score).
        k: RRF constant (default 60).
        top_n: Number of final results to return.
        
    Returns:
        List of chunks ranked by RRF score.
    """
    # Dictionary to accumulate RRF scores
    rrf_scores = defaultdict(float)
    chunk_map = {}
    
    # Score semantic results
    for rank, chunk in enumerate(semantic_results):
        chunk_id = chunk.get("chunk_id", f"semantic_{rank}")
        rrf_scores[chunk_id] += 1.0 / (k + rank + 1)
        chunk_map[chunk_id] = chunk
    
    # Score BM25 results
    for rank, chunk in enumerate(bm25_results):
        chunk_id = chunk.get("chunk_id", f"bm25_{rank}")
        rrf_scores[chunk_id] += 1.0 / (k + rank + 1)
        if chunk_id not in chunk_map:
            chunk_map[chunk_id] = chunk
    
    # Sort by RRF score (descending)
    sorted_chunk_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
    
    # Return top-n results
    results = []
    for chunk_id in sorted_chunk_ids[:top_n]:
        chunk = chunk_map[chunk_id].copy()
        chunk["rrf_score"] = rrf_scores[chunk_id]
        results.append(chunk)
    
    logger.info(f"RRF fusion returned {len(results)} results from {len(semantic_results)} semantic + {len(bm25_results)} BM25")
    return results


def hybrid_retrieve_context(query: str, k: int = 3) -> Dict[str, Any]:
    """
    Performs hybrid retrieval combining semantic and BM25 search.
    
    Args:
        query: The user's question.
        k: Number of final results to return.
        
    Returns:
        Dictionary with 'context', 'is_empty_db', and 'error' keys.
    """
    try:
        # 1. Semantic search (get more results for fusion)
        semantic_result = semantic_search(query, k=k * 3)
        
        if semantic_result["is_empty_db"]:
            return semantic_result
        
        if semantic_result["error"]:
            return semantic_result
        
        semantic_results = semantic_result["context"]
        
        # 2. BM25 search (get more results for fusion)
        bm25_results = bm25_search(query, k=k * 3)
        
        # 3. Combine using RRF
        fused_results = reciprocal_rank_fusion(
            semantic_results=semantic_results,
            bm25_results=bm25_results,
            top_n=k
        )
        
        # Format results to match the expected structure
        formatted_results = []
        for chunk in fused_results:
            formatted_results.append({
                "text": chunk.get("text", ""),
                "source": chunk.get("metadata", {}).get("source", chunk.get("source", "Unknown")),
                "chunk_index": chunk.get("metadata", {}).get("chunk_index", chunk.get("chunk_index", 0)),
                "rrf_score": chunk.get("rrf_score", 0.0)
            })
        
        return {
            "context": formatted_results,
            "is_empty_db": False,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"Error during hybrid retrieval: {str(e)}")
        return {
            "context": [],
            "is_empty_db": False,
            "error": str(e)
        }