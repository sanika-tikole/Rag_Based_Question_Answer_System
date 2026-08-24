import os
import pymupdf  # Updated to avoid deprecation warning
from pathlib import Path
from typing import List, Dict, Any

from src.utils import setup_logger
from src.config import settings

logger = setup_logger(__name__)

def extract_text_from_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Extracts text from a single PDF file using PyMuPDF.
    """
    path = Path(pdf_path)
    if not path.exists():
        logger.error(f"File not found: {pdf_path}")
        return {"source": path.name, "text": "", "page_count": 0, "error": "File not found"}

    try:
        logger.info(f"Extracting text from: {path.name}")
        doc = pymupdf.open(pdf_path)  # Updated from fitz.open
        page_count = len(doc)
        full_text = []
        
        for page_num in range(page_count):
            page = doc.load_page(page_num)
            text = page.get_text("text")  # Extract plain text
            full_text.append(text)
            
        doc.close()
        
        extracted_text = "\n\n".join(full_text).strip()
        logger.info(f"Successfully extracted {len(extracted_text)} characters from {page_count} pages.")
        
        return {
            "source": path.name,
            "page_count": page_count,
            "text": extracted_text,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"Failed to extract text from {path.name}: {str(e)}")
        return {"source": path.name, "text": "", "page_count": 0, "error": str(e)}


def load_documents(directory: str) -> List[Dict[str, Any]]:
    """
    Scans a directory for PDF files and extracts text from all of them.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        logger.warning(f"Directory does not exist: {directory}. Creating it.")
        dir_path.mkdir(parents=True, exist_ok=True)
        return []

    pdf_files = list(dir_path.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {directory}. Please add PDFs to this folder.")
        return []

    logger.info(f"Found {len(pdf_files)} PDF file(s) in {directory}. Starting extraction...")
    
    documents = []
    for pdf_file in pdf_files:
        doc_data = extract_text_from_pdf(str(pdf_file))
        if doc_data["text"]:  # Only add if extraction was successful
            documents.append(doc_data)
            
    logger.info(f"Extraction complete. Successfully processed {len(documents)} document(s).")
    return documents