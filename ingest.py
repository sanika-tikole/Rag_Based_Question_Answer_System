"""
CLI script to run the document ingestion pipeline.
Usage: python ingest.py
"""
import sys
from src.config import settings, DOCUMENTS_DIR
from src.ingestion import load_documents
from src.chunking import chunk_documents
from src.embeddings import generate_embeddings
from src.vector_store import add_documents_to_vector_store
from src.bm25_index import build_bm25_index
from src.utils import setup_logger

logger = setup_logger("ingest_cli")

def main():
    logger.info("Starting Document Ingestion Pipeline...")
    logger.info(f"Target directory: {DOCUMENTS_DIR}")
    
    # Step 1: Load and extract text from PDFs
    documents = load_documents(DOCUMENTS_DIR)
    if not documents:
        logger.info("No documents to process. Exiting.")
        sys.exit(0)
    
    # Step 2: Chunk the extracted documents
    chunks = chunk_documents(documents)
    if not chunks:
        logger.error("Chunking failed or produced no chunks. Exiting.")
        sys.exit(1)
    
    # Step 3: Generate embeddings for the chunks
    chunk_texts = [chunk["text"] for chunk in chunks]
    embeddings = generate_embeddings(chunk_texts)
    
    # Step 4: Add to Vector Store (ChromaDB)
    add_documents_to_vector_store(chunks, embeddings)
    
    # Step 5: Build BM25 index for hybrid search
    build_bm25_index(chunks)
    
    # Step 6: Print a quick summary
    logger.info("--- Pipeline Summary ---")
    logger.info(f"Documents Processed: {len(documents)}")
    logger.info(f"Total Chunks Generated: {len(chunks)}")
    logger.info(f"Vector Store Location: {settings.chroma_persist_dir}")
    logger.info("Ingestion pipeline finished successfully!")

if __name__ == "__main__":
    main()