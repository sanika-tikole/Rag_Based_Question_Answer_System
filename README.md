# 📚 RAG-Based Document Q&A System

A clean, modular, and production-ready Retrieval-Augmented Generation (RAG) system built with Python. It extracts text from PDFs, chunks it intelligently, stores it in a local vector database, and answers user queries using the **Groq** API with accurate source citations.

## ✨ Features

- **PDF Extraction**: Fast and reliable text extraction using `PyMuPDF`.
- **Smart Chunking**: Overlapping text splitting via `langchain-text-splitters` to preserve semantic context.
- **Local Embeddings**: Privacy-friendly, on-device embedding generation using `Sentence Transformers` (`all-MiniLM-L6-v2`).
- **Persistent Vector Store**: Local semantic search using `ChromaDB`.
- **Lightning-Fast LLM**: Powered by **Groq** (`llama-3.3-70b-versatile`) for near-instantaneous, high-quality responses.
- **Interactive UI**: Clean, chat-based interface built with `Streamlit`.
- **Robust Error Handling**: Graceful fallbacks for empty databases, missing API keys, or extraction failures.
- **Source Citations**: Every answer includes references to the exact PDF files used to generate it.

## 🏗️ Architecture

<img width="1661" height="947" alt="ChatGPT Image Aug 24, 2026, 02_29_04 PM" src="https://github.com/user-attachments/assets/4d0e8f17-5122-4a7a-89fc-8702ae8dac96" />

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.9 - 3.13
- A free [Groq API Key](https://console.groq.com/keys)

### 2. Installation

```bash
# Navigate to the project directory
cd RAG-Document-QA

# Create and activate a virtual environment
python -m venv venv

# On Windows (CMD):
venv\Scripts\activate
# On Windows (PowerShell):
venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configuration

Copy the example environment file and add your Groq API key:

```bash
# On Windows:
copy .env.example .env
# On macOS/Linux:
cp .env.example .env
```

Open `.env` in a text editor and update:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Ingest Documents

Place your `.pdf` files into the `data/documents/` folder, then run the ingestion pipeline:

```bash
python ingest.py
```

*This will extract text, chunk it, generate embeddings, and store everything in the local ChromaDB.*

### 5. Run the Application

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501` to start chatting with your documents!

## 📂 Project Structure

```text
RAG-Document-QA/
├── data/
│   ├── documents/           # Place raw PDF files here
│   └── vector_store/        # ChromaDB persistent storage (gitignored)
├── src/
│   ├── config.py            # Centralized environment & path configuration
│   ├── ingestion.py         # PDF text extraction logic
│   ├── chunking.py          # Text splitting logic
│   ├── embeddings.py        # Sentence Transformer embedding logic
│   ├── vector_store.py      # ChromaDB insertion logic
│   ├── retrieval.py         # Semantic search logic
│   ├── llm.py               # Groq API interaction & prompt formatting
│   └── utils.py             # Logging utilities
├── tests/                   # Unit and integration tests
├── app.py                   # Streamlit frontend entry point
├── ingest.py                # CLI script for data ingestion
├── sample_qa.md             # Template for evaluating RAG accuracy
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## ⚙️ Customization

All major configuration options are controlled via the `.env` file:

| Setting | Description | Default |
| :--- | :--- | :--- |
| `LLM_MODEL_NAME` | The Groq model to use for generation | `llama-3.3-70b-versatile` |
| `LLM_TEMPERATURE` | Creativity vs. precision (0.0 = deterministic) | `0.1` |
| `EMBEDDING_MODEL_NAME` | The Sentence Transformer model for vectorization | `all-MiniLM-L6-v2` |
| `CHUNK_SIZE` | Maximum characters per text chunk | `1000` |
| `CHUNK_OVERLAP` | Overlapping characters between chunks for context | `200` |
| `CHROMA_COLLECTION_NAME` | Name of the ChromaDB collection | `atman_rag_docs` |

## 📝 Evaluation

Use the provided `sample_qa.md` file to systematically test the system's:
1. **Accuracy**: Does it answer using *only* the provided context?
2. **Citation**: Are the `[1]`, `[2]` markers present and correct?
3. **Refusal**: Does it correctly decline out-of-scope questions?
4. **Conciseness**: Is the answer free of unnecessary fluff?

## 🛠️ Tech Stack

- **Language**: Python 3.13
- **PDF Processing**: PyMuPDF
- **Text Splitting**: LangChain Text Splitters
- **Embeddings**: Sentence Transformers
- **Vector Database**: ChromaDB
- **LLM Provider**: Groq (Llama 3.3)
- **Frontend**: Streamlit
- **Configuration**: Pydantic Settings + python-dotenv

## 🎯 Design Trade-offs

During development, several architectural decisions were made based on the project's scope and requirements:

| Decision | Chosen Approach | Alternative Considered | Rationale |
|:---|:---|:---|:---|
| **Vector Database** | ChromaDB (local, persistent) | Pinecone, Weaviate, FAISS | ChromaDB is lightweight, requires no external service, and persists to disk. Ideal for a single-user demo. FAISS is faster but lacks built-in persistence; Pinecone requires cloud setup. |
| **Embedding Model** | `all-MiniLM-L6-v2` (384-dim) | `text-embedding-3-large` (OpenAI), `BAAI/bge-large` | Local model = zero API cost, works offline, fast (~10ms per chunk). Larger models offer better accuracy but require GPU or paid API calls. |
| **Chunking Strategy** | Recursive character split (1000 chars / 200 overlap) | Semantic chunking, fixed-page splits | Recursive splitting preserves paragraph/sentence boundaries without requiring an NLP model. 1000 chars balances context richness with retrieval precision. |
| **LLM Provider** | Groq (Llama 3.1 70B) | OpenAI GPT-4, Anthropic Claude | Groq offers near-instant inference on LPU hardware at a fraction of the cost. Llama 3.1 70B provides strong reasoning for RAG tasks. |
| **PDF Extraction** | PyMuPDF (fitz) | pdfplumber, Unstructured, LlamaParse | PyMuPDF is the fastest pure-Python PDF library with excellent text fidelity. Unstructured is more powerful for complex layouts but heavier. |
| **Configuration** | Pydantic Settings + `.env` | Hardcoded constants, YAML files | Pydantic provides type validation, environment variable loading, and IDE autocomplete — professional standard for production apps. |

## ⚠️ Known Limitations

The current implementation has the following limitations, which could be addressed in future iterations:

1. **Text-Only PDFs**: The system extracts plain text only. PDFs with scanned images, complex tables, charts, or embedded diagrams will lose that information. (Fix: integrate OCR via Tesseract or a vision model.)

2. **Single Language**: The embedding model (`all-MiniLM-L6-v2`) is optimized for English. Non-English documents may have reduced retrieval accuracy. (Fix: switch to `paraphrase-multilingual-MiniLM-L12-v2`.)

3. **No Conversational Context**: Each question is answered independently. The system does not remember previous questions in the session. (Fix: implement conversation history in Streamlit.)

4. **No Document Management**: Users cannot delete or list ingested documents from the UI. (Fix: add a document management panel.)

5. **No Streaming Responses**: The LLM response appears all at once after generation completes. (Fix: use Groq's streaming API for token-by-token display.)

6. **No Re-ranking**: Retrieved chunks are returned in raw similarity order. A cross-encoder re-ranker could improve precision for complex queries.

7. **No Evaluation Automation**: The `sample_qa.md` file exists for manual testing, but there is no automated evaluation pipeline to compute accuracy, citation precision, or hallucination rate.

## 📄 License

This project is created as part of the Atman Cloud Consultancy AI/ML Engineer assignment.
