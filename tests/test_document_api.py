from fastapi.testclient import TestClient

import pymupdf
import pytest
from app.main import app
from app.api import document_routes


class FakeDB:
    """A simple mock database session."""

    def add(self, document):
        self.document = document

    def commit(self):
        pass

    def rollback(self):
        pass


def override_get_db():
    return FakeDB()

@pytest.fixture
def client():
    app.dependency_overrides[document_routes.get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

def setup_test_dependencies(monkeypatch):
    monkeypatch.setitem(
        app.dependency_overrides,
        document_routes.get_db,
        override_get_db,
    )


def test_upload_valid_txt_file(monkeypatch):
    setup_test_dependencies(monkeypatch)

    # Mock embedding generation.
    def mock_embeddings(chunks):
        return [[0.1] * 384 for _ in chunks]

    # Mock Qdrant storage.
    def mock_store_chunks(**kwargs):
        return len(kwargs["chunks"])

    monkeypatch.setattr(
        document_routes,
        "generate_embeddings",
        mock_embeddings,
    )

    monkeypatch.setattr(
        document_routes,
        "store_chunks",
        mock_store_chunks,
    )

    client = TestClient(app)

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "sample.txt",
                b"RAG combines retrieval with language generation.",
                "text/plain",
            )
        },
        data={
            "chunking_method": "fixed",
            "chunk_size": 1000,
            "overlap": 200,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "sample.txt"
    assert data["file_type"] == ".txt"
    assert data["chunking_method"] == "fixed"
    assert data["chunk_count"] == 1
    assert data["embedding_count"] == 1
    assert data["embedding_dimensions"] == 384
    assert data["stored_vectors"] == 1
    assert data["metadata_database"] == "MySQL"
    assert data["vector_database"] == "Qdrant"

    app.dependency_overrides.clear()

def test_upload_valid_pdf_file(monkeypatch):
    setup_test_dependencies(monkeypatch)

    # Generate a real PDF in memory.
    pdf_document = pymupdf.open()

    page = pdf_document.new_page()

    page.insert_text(
        (72, 72),
        "PalmMind uses Retrieval-Augmented Generation to answer questions."
    )

    pdf_bytes = pdf_document.tobytes()
    pdf_document.close()

    # Mock embedding generation.
    def mock_embeddings(chunks):
        return [[0.1] * 384 for _ in chunks]

    # Mock Qdrant storage.
    def mock_store_chunks(**kwargs):
        return len(kwargs["chunks"])

    monkeypatch.setattr(
        document_routes,
        "generate_embeddings",
        mock_embeddings,
    )

    monkeypatch.setattr(
        document_routes,
        "store_chunks",
        mock_store_chunks,
    )

    client = TestClient(app)

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "sample.pdf",
                pdf_bytes,
                "application/pdf",
            )
        },
        data={
            "chunking_method": "recursive",
            "chunk_size": 1000,
            "overlap": 200,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "sample.pdf"
    assert data["file_type"] == ".pdf"
    assert data["chunking_method"] == "recursive"
    assert data["chunk_count"] >= 1
    assert data["embedding_count"] == data["chunk_count"]
    assert data["embedding_dimensions"] == 384
    assert data["stored_vectors"] == data["chunk_count"]
    assert data["metadata_database"] == "MySQL"
    assert data["vector_database"] == "Qdrant"

    app.dependency_overrides.clear()

def test_upload_unsupported_file_type(monkeypatch):
    setup_test_dependencies(monkeypatch)

    client = TestClient(app)

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "sample.docx",
                b"Unsupported document",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Only PDF and TXT files are supported."
    )

    app.dependency_overrides.clear()


def test_upload_empty_file(monkeypatch):
    setup_test_dependencies(monkeypatch)

    client = TestClient(app)

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "empty.txt",
                b"",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Uploaded file is empty."
    )

    app.dependency_overrides.clear()
    
@pytest.mark.parametrize(
    "chunking_method, chunk_size, overlap",
    [
        ("invalid", 1000, 200),
        ("fixed", 0, 0),
        ("fixed", -100, 0),
        ("fixed", 100, 100),
        ("fixed", 100, 150),
        ("recursive", 100, -1),
    ],
)
def test_upload_invalid_chunking_settings(
    monkeypatch,
    chunking_method,
    chunk_size,
    overlap,
):
    setup_test_dependencies(monkeypatch)

    client = TestClient(app)

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "sample.txt",
                b"This is a sample document for testing.",
                "text/plain",
            )
        },
        data={
            "chunking_method": chunking_method,
            "chunk_size": chunk_size,
            "overlap": overlap,
        },
    )

    assert response.status_code == 400

    app.dependency_overrides.clear()
    
def test_upload_invalid_pdf_file(client, monkeypatch):
    def mock_pdf_extraction(file_content):
        raise Exception("Invalid PDF")

    monkeypatch.setattr(
        document_routes,
        "extract_text_from_pdf",
        mock_pdf_extraction,
    )

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "invalid.pdf",
                b"This is not a valid PDF.",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Could not read the uploaded document. Please check the file."
    )


def test_upload_txt_with_invalid_encoding(client):
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "invalid.txt",
                b"\xff\xfe\xfa",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "TXT file must use UTF-8 encoding."
    )


def test_upload_document_without_extractable_text(client, monkeypatch):
    def mock_pdf_extraction(file_content):
        return ""

    monkeypatch.setattr(
        document_routes,
        "extract_text_from_pdf",
        mock_pdf_extraction,
    )

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "empty-content.pdf",
                b"%PDF-1.4 fake content",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "No extractable text found in the document."
    )
    
def test_upload_embedding_failure(client, monkeypatch):
    def mock_embeddings(chunks):
        raise RuntimeError("Embedding model unavailable")

    monkeypatch.setattr(
        document_routes,
        "generate_embeddings",
        mock_embeddings,
    )

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "sample.txt",
                b"RAG combines retrieval with language generation.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 500
    assert "Embedding generation failed" in response.json()["detail"]


def test_upload_vector_storage_failure(client, monkeypatch):
    def mock_embeddings(chunks):
        return [[0.1] * 384 for _ in chunks]

    def mock_store_chunks(**kwargs):
        raise RuntimeError("Qdrant unavailable")

    monkeypatch.setattr(
        document_routes,
        "generate_embeddings",
        mock_embeddings,
    )

    monkeypatch.setattr(
        document_routes,
        "store_chunks",
        mock_store_chunks,
    )

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "sample.txt",
                b"RAG combines retrieval with language generation.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 500
    assert "Vector storage failed" in response.json()["detail"]


def test_upload_metadata_failure_cleans_up_vectors(client, monkeypatch):
    deleted_documents = []

    class FailingDB:
        def add(self, document):
            self.document = document

        def commit(self):
            raise RuntimeError("MySQL unavailable")

        def rollback(self):
            pass

    def override_failing_db():
        return FailingDB()

    # Replace the normal fake database with one that fails on commit.
    from app.database import get_db

    app.dependency_overrides[get_db] = override_failing_db

    def mock_embeddings(chunks):
        return [[0.1] * 384 for _ in chunks]

    def mock_store_chunks(**kwargs):
        return len(kwargs["chunks"])

    def mock_delete_document_chunks(document_id):
        deleted_documents.append(document_id)

    monkeypatch.setattr(
        document_routes,
        "generate_embeddings",
        mock_embeddings,
    )

    monkeypatch.setattr(
        document_routes,
        "store_chunks",
        mock_store_chunks,
    )

    monkeypatch.setattr(
        document_routes,
        "delete_document_chunks",
        mock_delete_document_chunks,
    )

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "sample.txt",
                b"RAG combines retrieval with language generation.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 500

    assert response.json()["detail"] == (
        "Document metadata storage failed."
    )

    # Confirm that the Qdrant cleanup function was called.
    assert len(deleted_documents) == 1
    assert len(deleted_documents[0]) == 36