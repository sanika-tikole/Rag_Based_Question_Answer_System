import chromadb
from typing import List, Dict, Any

from src.utils import setup_logger
from src.config import settings

logger = setup_logger(__name__)

def get_vector_store():
    """
    Initializes and returns a persistent ChromaDB client and collection.
    """
    logger.info(f"Initializing ChromaDB at: {settings.chroma_persist_dir}")
    
    # Initialize persistent client
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    
    # Get or create the collection
    # We use cosine similarity, which is standard for sentence transformers
    collection = client.get_or_create_collection(
        name=settings.chroma_collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    
    logger.info(f"Collection '{settings.chroma_collection_name}' is ready.")
    return client, collection

def add_documents_to_vector_store(chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> None:
    """
    Adds chunked documents and their embeddings to the ChromaDB collection.
    
    Args:
        chunks: List of chunk dictionaries (must contain 'chunk_id', 'text', 'metadata').
        embeddings: List of embedding vectors corresponding to the chunks.
    """
    if not chunks or not embeddings:
        logger.warning("No chunks or embeddings provided to add to vector store.")
        return
    
    if len(chunks) != len(embeddings):
        logger.error(f"Mismatch: {len(chunks)} chunks but {len(embeddings)} embeddings.")
        return

    _, collection = get_vector_store()
    
    # Extract data into lists required by ChromaDB
    ids = [chunk["chunk_id"] for chunk in chunks]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]
    
    logger.info(f"Adding {len(chunks)} documents to ChromaDB collection...")
    
    # ChromaDB has a limit on batch size (around 40k-50k depending on version), 
    # but for typical document ingestion, adding them all at once is fine.
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )
    
    logger.info("Successfully added documents to vector store.")