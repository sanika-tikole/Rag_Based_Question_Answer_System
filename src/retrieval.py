import chromadb
from typing import List, Dict, Any
from src.config import settings
from src.utils import setup_logger

logger = setup_logger(__name__)

def retrieve_context(query: str, k: int = 3) -> Dict[str, Any]:
    """
    Retrieves the top-k most relevant chunks from the vector store.
    Returns a dictionary with 'context', 'is_empty_db', and 'error' keys for safe UI handling.
    """
    try:
        client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        
        # Use get_or_create to prevent crashes if the collection doesn't exist yet
        collection = client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Check if the database is completely empty
        if collection.count() == 0:
            logger.warning("Vector store is empty. No documents have been ingested yet.")
            return {"context": [], "is_empty_db": True, "error": None}

        logger.info(f"Retrieving top {k} chunks for query: '{query[:50]}...'")
        
        from src.embeddings import embedding_model
        query_embedding = embedding_model.encode(query).tolist()
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "text": results['documents'][0][i],
                    "source": results['metadatas'][0][i].get('source', 'Unknown'),
                    "chunk_index": results['metadatas'][0][i].get('chunk_index', 0)
                })
                
        logger.info(f"Retrieved {len(formatted_results)} relevant chunks.")
        return {"context": formatted_results, "is_empty_db": False, "error": None}
        
    except Exception as e:
        logger.error(f"Error during retrieval: {str(e)}")
        return {"context": [], "is_empty_db": False, "error": str(e)}