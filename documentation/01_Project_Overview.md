# PalmMind AI — Project Documentation

**Project Name:** Document Processing and Retrieval-Augmented Generation System
**Organization:** PalmMind AI
**Project Type:** Backend Development — AI/ML
**Documentation Version:** 2.0
**Status:** Core RAG Components Implemented and Tested

---

## 1. Introduction

Large Language Models (LLMs) can generate human-like responses and answer questions, but their knowledge is generally limited to information available during training or external context provided to them.

When users need answers based on specific documents, relying solely on an LLM may produce inaccurate or irrelevant information. A system is therefore required to process external documents, retrieve relevant information, and provide that information as context to an LLM.

Retrieval-Augmented Generation (RAG) addresses this problem by combining document retrieval with language generation.

This project implements a backend system that processes uploaded documents, converts their contents into vector embeddings, stores them in a vector database, and makes the information available for retrieval through an LLM-powered API.

The system also includes multi-turn conversational capabilities using Redis. An interview booking workflow is part of the project scope and remains to be completed and verified.

## 2. Problem Statement

Organizations and individuals frequently work with documents containing important information. However, extracting relevant information from large collections of documents manually can be time-consuming.

Traditional keyword-based searches may also fail to identify relevant information when users express their questions differently from the wording used in the original documents.

A system is needed that can:

- Accept and process different document formats.
- Convert document contents into searchable representations.
- Retrieve relevant information based on semantic similarity.
- Generate context-aware responses using an LLM.
- Maintain conversational context across multiple interactions.
- Support structured interview booking through an LLM-powered interaction.

## 3. Project Objectives

The primary objectives are:

1. Develop REST APIs for document ingestion and LLM-powered information retrieval.
2. Implement document text extraction for PDF and TXT formats.
3. Implement multiple document chunking strategies.
4. Generate vector embeddings from extracted document chunks.
5. Store embeddings in a dedicated vector database.
6. Maintain document information and metadata in a relational database.
7. Implement a custom RAG pipeline for retrieving relevant document context and generating responses.
8. Support multi-turn conversations using Redis-based conversational memory.
9. Implement an interview booking workflow with appropriate information validation and database storage.
10. Develop a modular, maintainable, and testable backend architecture.

## 4. Project Scope

The project consists of two major REST API components.

### 4.1 API 1: Document Ingestion API

This component handles document uploading, processing, and storage.

Its responsibilities include:

- Accepting PDF and TXT files.
- Extracting text from uploaded documents.
- Applying a selectable chunking strategy.
- Generating embeddings for document chunks.
- Storing embeddings in a vector database.
- Saving document metadata in an SQL database.
- Validating uploaded files and processing parameters.
- Handling failures during document processing and storage.

Two chunking strategies are implemented.

**A. Fixed-Size Chunking**

Divides extracted text into chunks based on a predefined character limit. An overlap between consecutive chunks preserves contextual information that might otherwise be lost at chunk boundaries.

**B. Recursive Character Chunking**

Divides text using a hierarchy of separators, attempting to preserve meaningful paragraphs and word boundaries before splitting text into smaller sections.

The ingestion pipeline follows this sequence:

1. Receive and validate the uploaded document.
2. Extract its textual content.
3. Divide the extracted text into chunks.
4. Generate embeddings for each chunk.
5. Store embeddings and associated payloads in Qdrant.
6. Save document metadata in MySQL.

### 4.2 API 2: RAG Query and Interview Booking API

This component provides conversational interaction with the processed documents.

Its implemented responsibilities include:

- Accepting natural-language questions from users.
- Generating query embeddings.
- Retrieving relevant document chunks from the vector database.
- Constructing prompts using retrieved context.
- Sending constructed prompts to an LLM.
- Returning context-aware responses.
- Maintaining conversation history using Redis.
- Supporting multi-turn conversations.

The planned interview booking functionality includes:

- Collecting interview booking information.
- Validating the collected information.
- Saving interview booking details in a database.

Interview booking implementation and verification are still pending.

The RAG pipeline uses custom retrieval and prompt-generation logic rather than relying on a prebuilt RetrievalQAChain.

## 5. High-Level System Architecture

The system consists of the following major components:

1. **API Layer:** Exposes REST endpoints and handles incoming requests using FastAPI.
2. **Document Processing Layer:** Extracts text and applies the selected chunking strategy.
3. **Embedding Layer:** Converts document chunks and user queries into vector representations using FastEmbed.
4. **Vector Storage Layer:** Stores embeddings and supports similarity-based retrieval using Qdrant.
5. **SQL Database Layer:** Stores document metadata using MySQL.
6. **RAG Layer:** Retrieves relevant information and constructs prompts for the LLM.
7. **LLM Integration Layer:** Communicates with Google's Gemini API to generate responses.
8. **Conversation Memory Layer:** Uses Redis to maintain conversational history.

The application follows a modular architecture. Each component is implemented as a separate service or module to support independent development, testing, and maintenance.

### 5.1 Document Ingestion Architecture

```text
             Client
               |
               v
       FastAPI Upload API
               |
               v
        File Validation
               |
               v
         Text Extraction
          (PDF / TXT)
               |
               v
          Text Chunking
          /           \
         v             v
    Fixed-Size      Recursive
      Chunking       Chunking
          \           /
               |
               v
       Embedding Generation
            (FastEmbed)
               |
               v
         Vector Storage
             (Qdrant)
               |
               v
       Metadata Storage
             (MySQL)
```

### 5.2 RAG Query Architecture

```text
             Client
               |
               v
         Query API
               |
               v
       Conversation History
             (Redis)
               |
               v
       Query Embedding
           (FastEmbed)
               |
               v
        Vector Retrieval
            (Qdrant)
               |
               v
       Context Construction
               |
               v
          Gemini LLM
               |
               v
        Generated Answer
               |
               v
       Update Conversation
             (Redis)
               |
               v
           Response
```

## 6. Technology Selection

The following technologies have been selected and integrated into the application.

| Component | Selected Technology | Purpose |
|---|---|---|
| Programming Language | Python | Backend development |
| Backend Framework | FastAPI | REST API development |
| API Validation | Pydantic | Request and response validation |
| ASGI Server | Uvicorn | Running the FastAPI application |
| PDF Processing | PyMuPDF | PDF text extraction |
| TXT Processing | Python UTF-8 decoding | Plain-text extraction |
| Chunking | Custom implementation | Fixed-size and recursive chunking |
| Embedding Generation | FastEmbed | Generating text embeddings |
| Embedding Model | paraphrase-multilingual-MiniLM-L12-v2 | Text vectorization |
| Vector Database | Qdrant | Vector storage and similarity search |
| Relational Database | MySQL | Document metadata storage |
| ORM | SQLAlchemy | Relational database operations |
| Conversation Memory | Redis | Multi-turn conversation history |
| LLM Integration | Google Gemini API | Context-aware answer generation |
| Testing | Pytest and HTTPX | Automated API and service testing |
| Version Control | Git and GitHub | Source code management |

The selected embedding model generates vectors with 384 dimensions.

The current implementation uses Qdrant's local persistent storage configuration.

## 7. Expected Deliverables

The project deliverables include:

1. Functional Document Ingestion REST API.
2. RAG Query API.
3. Two selectable document chunking strategies.
4. Embedding generation and vector database integration.
5. SQL database integration for document metadata.
6. Redis-based conversational memory.
7. Custom RAG implementation.
8. API testing and validation.
9. Interview booking workflow.
10. Technical documentation.
11. GitHub repository containing source code and setup instructions.

## 8. Development Approach and Implementation Status

The project follows an incremental development approach. Each component is implemented and tested before proceeding to the next major component.

The development phases and their current status are:

| Phase | Description | Status |
|---|---|---|
| Phase 1 | Requirement analysis and system architecture | Completed |
| Phase 2 | Document ingestion and text extraction | Completed |
| Phase 3 | Chunking strategies and embedding generation | Completed |
| Phase 4 | Vector database and SQL database integration | Completed |
| Phase 5 | Custom RAG pipeline implementation | Implemented and tested |
| Phase 6 | Conversational memory using Redis | Implemented and tested |
| Phase 7 | Interview booking workflow | Pending |
| Phase 8 | Integration testing and documentation | In progress |

### 8.1 Testing Summary

The application currently contains 43 automated tests.

The complete test suite was executed successfully:

```text
43 passed in 5.04s
```

The tests cover:

- Document chunking strategies.
- PDF and TXT extraction.
- Document upload validation.
- Invalid chunking configurations.
- Embedding generation failure handling.
- Vector storage failure handling.
- Database failure handling and vector cleanup.
- RAG query endpoints.
- Multi-turn conversation behavior.
- Redis conversation storage and expiration.
- Vector storage and deletion.

Manual API testing through Swagger UI has also verified successful PDF and TXT ingestion using both recursive and fixed-size chunking.

### 8.2 Known Limitations

- PDF extraction currently uses text extraction and does not perform OCR on scanned documents.
- Retrieval quality depends on document content, embedding similarity, and the configured similarity threshold.
- The current retrieval implementation does not yet resolve every context-dependent follow-up question before searching.
- Qdrant local persistent storage should not be accessed concurrently by multiple application processes.
- Interview booking functionality remains pending verification.

## 9. Conclusion

This project implements a modular backend system that combines document processing, vector-based retrieval, and Large Language Models to provide context-aware conversational capabilities.

The document ingestion pipeline supports PDF and TXT files, multiple chunking strategies, embedding generation, vector storage, and relational metadata management.

The RAG query component extends this functionality through semantic retrieval, Gemini-based response generation, and Redis-powered multi-turn conversation management.

The implementation demonstrates practical understanding of backend API development, document processing, embedding models, vector databases, relational databases, conversational state management, and LLM integration.

Further development will focus on completing the interview booking workflow, improving conversational retrieval, and finalizing technical documentation.