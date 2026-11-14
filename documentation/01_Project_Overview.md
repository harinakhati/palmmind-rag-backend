# PalmMind AI — Project Documentation

**Project Name:** Document Processing and Retrieval-Augmented Generation System  
**Organization:** PalmMind AI  
**Project Type:** Backend Development — AI/ML  
**Documentation Version:** 1.0  
**Status:** Initial Planning

---

## 1. Introduction

Large Language Models (LLMs) can generate human-like responses and answer questions, but their knowledge is generally limited to the information available during their training or the external context provided to them.

When users need answers based on specific documents, relying solely on an LLM may produce inaccurate or irrelevant information. A system is therefore required to process external documents, retrieve relevant information, and provide that information as context to an LLM.

Retrieval-Augmented Generation (RAG) addresses this problem by combining document retrieval with language generation.

This project aims to develop a backend system that processes uploaded documents, converts their contents into vector embeddings, stores them in a vector database, and makes the information available for retrieval through an LLM-powered API.

The project also includes conversational capabilities and an interview booking workflow.

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

Two chunking strategies will be implemented:

**A. Fixed-Size Chunking**

Divides extracted text into chunks of a predefined size. An overlap between consecutive chunks preserves contextual information that might otherwise be lost at chunk boundaries.

**B. Recursive Character Chunking**

Divides text using a hierarchy of separators, attempting to preserve meaningful paragraphs and sentences before splitting text into smaller sections.

### 4.2 API 2: RAG Query and Interview Booking API

This component provides conversational interaction with the processed documents.

Its responsibilities include:

- Accepting natural-language questions from users.
- Generating query embeddings.
- Retrieving relevant document chunks from the vector database.
- Constructing prompts using retrieved context.
- Sending the constructed prompts to an LLM.
- Returning context-aware responses.
- Maintaining conversation history using Redis.
- Supporting multi-turn conversations.
- Collecting and validating interview booking information.
- Saving interview booking information in a database.

The RAG pipeline will be implemented using custom retrieval and prompt-generation logic rather than relying on a prebuilt RetrievalQAChain.

## 5. High-Level System Architecture

The system will consist of the following major components:

1. **API Layer:** Exposes REST endpoints and handles incoming requests.
2. **Document Processing Layer:** Extracts text and applies chunking strategies.
3. **Embedding Layer:** Converts document chunks and user queries into vector representations.
4. **Vector Storage Layer:** Stores embeddings and supports similarity-based retrieval.
5. **SQL Database Layer:** Stores document metadata and interview booking information.
6. **RAG Layer:** Retrieves relevant information and constructs prompts for the LLM.
7. **LLM Integration Layer:** Communicates with the selected language model.
8. **Conversation Memory Layer:** Uses Redis to maintain conversational context.

The architecture will follow a modular design so that individual components can be developed, tested, and maintained independently.

## 6. Technology Selection

The final technology stack will be documented after evaluating the project requirements and implementation constraints.

| Component | Proposed Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| API Validation | Pydantic |
| Document Processing | PyMuPDF / Python file processing |
| Chunking | Custom Fixed-Size and Recursive Character Chunking |
| Embedding Model | To be selected |
| Vector Database | Qdrant / Pinecone / Weaviate / Milvus |
| Relational Database | PostgreSQL / MySQL |
| Conversational Memory | Redis |
| LLM Integration | To be selected |
| Testing | Pytest |
| Version Control | Git and GitHub |

Technology selection will consider implementation complexity, documentation availability, compatibility, and resource requirements.

## 7. Expected Deliverables

The expected deliverables include:

1. Functional Document Ingestion REST API.
2. Functional RAG Query and Interview Booking REST API.
3. Two selectable document chunking strategies.
4. Vector database integration.
5. SQL database integration.
6. Redis-based conversational memory.
7. Custom RAG implementation.
8. API testing and validation.
9. Technical documentation.
10. GitHub repository containing the source code and setup instructions.

## 8. Development Approach

The project will follow an incremental development approach.

Each component will be documented, implemented, and tested before moving to the next major component.

The proposed development phases are:

- **Phase 1:** Requirement analysis and system architecture.
- **Phase 2:** Document ingestion and text extraction.
- **Phase 3:** Chunking strategies and embedding generation.
- **Phase 4:** Vector database and SQL database integration.
- **Phase 5:** Custom RAG pipeline implementation.
- **Phase 6:** Conversational memory and interview booking.
- **Phase 7:** Testing, integration, and documentation completion.

## 9. Conclusion

This project aims to develop a modular backend system that combines document processing, vector-based retrieval, and Large Language Models to provide context-aware conversational capabilities.

By implementing the document ingestion pipeline and custom RAG architecture, the project demonstrates practical understanding of document processing, embeddings, vector databases, API development, and LLM integration.