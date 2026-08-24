import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

# Define base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"

# Ensure directories exist
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LLM (Groq)
    llm_provider: str = os.getenv("LLM_PROVIDER", "groq")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    llm_model_name: str = os.getenv("LLM_MODEL_NAME", "openai/gpt-oss-120b")
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    
    # Embeddings
    embedding_model_name: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    
    # Chunking
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # Vector Store
    chroma_collection_name: str = os.getenv("CHROMA_COLLECTION_NAME", "atman_rag_docs")
    chroma_persist_dir: str = str(VECTOR_STORE_DIR)

    class Config:
        env_file = ".env"
        extra = "ignore"

# Instantiate settings to be imported across the app
settings = Settings()