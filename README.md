# PalmMind RAG Backend

A backend application for building a Retrieval-Augmented Generation (RAG) system using FastAPI. The project focuses on document ingestion, text extraction, document processing, and context-aware information retrieval.

## Overview

Retrieval-Augmented Generation (RAG) combines information retrieval with Large Language Models (LLMs). Instead of relying only on the knowledge learned during model training, a RAG system retrieves relevant information from external documents and uses it to generate context-aware responses.

This project aims to develop a backend system that processes uploaded documents, converts their content into searchable representations, and uses retrieved information to support accurate responses.

## Objectives

- Build REST APIs for document ingestion and RAG-based querying.
- Support PDF and TXT document uploads.
- Extract and process text from uploaded documents.
- Implement configurable document chunking strategies.
- Generate embeddings and store them in a vector database.
- Maintain document metadata using a relational database.
- Retrieve relevant document content to generate context-aware responses.
- Support multi-turn conversations and interview booking functionality.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| ASGI Server | Uvicorn |
| PDF Text Extraction | PyMuPDF |
| Relational Database | MySQL |
| Vector Database | Qdrant |
| Embedding Generation | To be finalized |
| Conversation State | Redis |
| API Testing | Swagger UI / Pytest |
| Version Control | Git and GitHub |

*Technologies will be integrated incrementally as development progresses.*

## Project Structure

```text
palmmind-rag-backend/
│
├── app/
│   ├── api/              # API route definitions
│   ├── schemas/          # Request and response schemas
│   ├── services/         # Business logic and processing
│   └── main.py           # FastAPI application entry point
│
├── documentation/        # Project and technical documentation
├── tests/                # Automated tests
├── uploads/              # Temporary document uploads (ignored by Git)
│
├── .gitignore
├── requirements.txt
└── README.md
```

## Current Implementation Status

| Feature | Status |
|---|---|
| FastAPI application setup | Completed |
| PDF document upload | Implemented |
| TXT document upload | Implemented |
| PDF text extraction | Implemented |
| TXT text extraction | Implemented |
| File validation | Initial implementation |
| Fixed-size chunking with overlap | Planned |
| Recursive character chunking | Planned |
| Embedding generation | Planned |
| Vector database integration | Planned |
| MySQL metadata storage | Planned |
| RAG query API | Planned |
| Conversation management | Planned |
| Interview booking API | Planned |

## Getting Started

### Prerequisites

- Python 3.14
- Git

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/harinakhati/palmmind-rag-backend
cd palmmind-rag-backend
```

**2. Create a virtual environment**

```bash
python3.14 -m venv .venv
```

**3. Activate the virtual environment**

Linux/macOS:

```bash
source .venv/bin/activate
```

**4. Install dependencies**

```bash
python -m pip install -r requirements.txt
```

**5. Run the application**

```bash
uvicorn app.main:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000
```

### API Documentation

FastAPI automatically generates interactive API documentation.

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Development Approach

The project is being developed incrementally, with documentation and testing maintained alongside implementation.

The development process follows these major stages:

1. Project setup and API initialization.
2. Document ingestion and text extraction.
3. Document chunking and preprocessing.
4. Embedding generation and vector storage.
5. RAG-based query processing.
6. Conversation management and interview booking.
7. Integration testing and documentation.

## Documentation

Detailed project documentation is maintained in the `documentation/` directory.

## Project Status

Currently under active development.