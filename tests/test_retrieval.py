"""
Tests for semantic retrieval (src/retrieval.py).
"""
import pytest
import chromadb
from src.config import settings
from src.retrieval import retrieve_context

@pytest.fixture
def setup_test_collection():
    """Set up a test collection with known documents."""
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    collection = client.get_or_create_collection(
        name="test_collection",
        metadata={"hnsw:space": "cosine"}
    )
    
    # Add test documents
    from src.embeddings import generate_embeddings
    texts = [
        "The API rate limit for the Standard plan is 600 requests per minute.",
        "Employees receive 10 paid sick days per year.",
        "Python is a popular programming language for machine learning."
    ]
    embeddings = generate_embeddings(texts)
    
    collection.add(
        ids=["test_1", "test_2", "test_3"],
        embeddings=embeddings,
        documents=texts,
        metadatas=[
            {"source": "api.pdf", "chunk_index": 0},
            {"source": "hr.pdf", "chunk_index": 1},
            {"source": "tech.pdf", "chunk_index": 2}
        ]
    )
    
    yield collection
    
    # Cleanup after test
    client.delete_collection("test_collection")


def test_retrieve_context_returns_results(setup_test_collection, monkeypatch):
    """Test that retrieval returns results for a valid query."""
    # Monkeypatch the collection name to use our test collection
    monkeypatch.setattr(settings, "chroma_collection_name", "test_collection")
    
    result = retrieve_context("What is the API rate limit?", k=2)
    
    # Now result is a Dict, so we can access keys safely
    assert result["error"] is None
    assert result["is_empty_db"] is False
    assert len(result["context"]) == 2
    assert "rate limit" in result["context"][0]["text"].lower() or "api" in result["context"][0]["text"].lower()


def test_retrieve_context_empty_database(monkeypatch):
    """Test that retrieval handles an empty database gracefully."""
    # Use a completely new, empty collection name
    monkeypatch.setattr(settings, "chroma_collection_name", "empty_test_collection_xyz_123")
    
    result = retrieve_context("Any query", k=3)
    
    # Because we use get_or_create_collection, it won't crash. 
    # It will just see count() == 0 and return is_empty_db=True
    assert result["is_empty_db"] is True
    assert result["context"] == []
    assert result["error"] is None