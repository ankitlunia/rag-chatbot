# RAG Chatbot

A web-based chatbot application that uses RAG (Retrieval-Augmented Generation) to provide accurate answers based on your documents.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

## Quick Setup

1. Clone the repository and navigate to the project directory:
```bash
git clone <repository-url>
cd rag-chatbot
```

2. Set up Python virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
.
├── main.py           # FastAPI server and main application logic
├── indexer.py        # Document indexing functionality
├── requirements.txt  # Python dependencies
├── static/          # Frontend static files
├── pdfs/            # Directory for PDF documents
├── faiss_index/     # Vector store index
└── model/           # Language model directory
```

## Running the Application

1. Make sure your virtual environment is activated

2. Start the FastAPI server:
```bash
uvicorn main:app --reload --port 8000
```

3. Access the application at: `http://localhost:8000`

## Environment Setup Notes

- The language model will be automatically downloaded if it is not present in the `model/` directory.
- Ensure all your documents are placed in the `pdfs/` directory before running the indexer
- The FAISS index will be automatically created when you first run the indexer 