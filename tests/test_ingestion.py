"""
Tests for PDF text extraction (src/ingestion.py).

WHAT WE'RE TESTING:
- Can we extract text from a valid PDF?
- Does the function handle missing files gracefully?
- Does the returned dictionary contain all required fields?
"""
import pytest
import pymupdf
from pathlib import Path
from src.ingestion import extract_text_from_pdf, load_documents


@pytest.fixture
def sample_pdf(tmp_path):
    """Create a temporary PDF with known text for testing."""
    pdf_path = tmp_path / "test.pdf"
    doc = pymupdf.open()
    page = doc.new_page()
    # Insert text at position (72, 72) with font size 12
    page.insert_text((72, 72), "Hello, this is a test PDF document.", fontsize=12)
    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)


def test_extract_text_from_valid_pdf(sample_pdf):
    """Test that we can extract text from a valid PDF."""
    result = extract_text_from_pdf(sample_pdf)
    
    assert result["error"] is None
    assert result["page_count"] == 1
    assert "Hello, this is a test PDF document." in result["text"]
    assert result["source"] == "test.pdf"


def test_extract_text_from_missing_file():
    """Test that missing files are handled gracefully."""
    result = extract_text_from_pdf("/nonexistent/path/file.pdf")
    
    assert result["error"] == "File not found"
    assert result["text"] == ""
    assert result["page_count"] == 0


def test_load_documents_empty_directory(tmp_path):
    """Test that an empty directory returns an empty list."""
    result = load_documents(str(tmp_path))
    assert result == []


def test_load_documents_with_pdfs(sample_pdf, tmp_path):
    """Test that load_documents finds and processes all PDFs in a directory."""
    result = load_documents(str(tmp_path))
    
    assert len(result) == 1
    assert result[0]["source"] == "test.pdf"
    assert len(result[0]["text"]) > 0