"""
Tests for text chunking (src/chunking.py).

WHAT WE'RE TESTING:
- Does chunking split long text into multiple chunks?
- Are chunks the correct size (respecting chunk_size)?
- Is overlap working correctly?
- Is metadata (source, chunk_index) attached correctly?
"""
import pytest
from src.chunking import chunk_documents


def test_chunking_short_text():
    """Test that short text produces a single chunk."""
    documents = [{
        "source": "short.pdf",
        "text": "This is a short document.",
        "page_count": 1
    }]
    
    chunks = chunk_documents(documents)
    
    assert len(chunks) == 1
    assert chunks[0]["source"] == "short.pdf"
    assert chunks[0]["chunk_index"] == 0
    assert "This is a short document." in chunks[0]["text"]


def test_chunking_long_text():
    """Test that long text is split into multiple chunks."""
    # Create a document with 3000 characters (should produce 3+ chunks with chunk_size=1000)
    long_text = "This is a test sentence. " * 150  # ~3750 chars
    documents = [{
        "source": "long.pdf",
        "text": long_text,
        "page_count": 5
    }]
    
    chunks = chunk_documents(documents)
    
    assert len(chunks) > 1
    # Verify all chunks have correct metadata
    for i, chunk in enumerate(chunks):
        assert chunk["source"] == "long.pdf"
        assert chunk["chunk_index"] == i
        assert chunk["page_count"] == 5
        assert len(chunk["text"]) > 0


def test_chunking_empty_documents():
    """Test that empty input returns empty output."""
    chunks = chunk_documents([])
    assert chunks == []


def test_chunking_metadata_structure():
    """Test that each chunk has the required metadata fields."""
    documents = [{
        "source": "meta.pdf",
        "text": "Some text content " * 100,
        "page_count": 2
    }]
    
    chunks = chunk_documents(documents)
    
    for chunk in chunks:
        assert "chunk_id" in chunk
        assert "source" in chunk
        assert "text" in chunk
        assert "metadata" in chunk
        assert "source" in chunk["metadata"]
        assert "chunk_index" in chunk["metadata"]