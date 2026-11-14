import pytest
from qdrant_client import QdrantClient

from app.services import vector_store


@pytest.fixture
def isolated_qdrant_client(tmp_path, monkeypatch):
    """Create an isolated Qdrant client for testing."""

    storage_path = tmp_path / "qdrant_test"

    test_client = QdrantClient(
        path=str(storage_path)
    )

    # Replace the project's Qdrant client temporarily.
    monkeypatch.setattr(
        vector_store,
        "client",
        test_client,
    )

    yield test_client

    test_client.close()


def test_store_and_delete_document_chunks(isolated_qdrant_client):
    document_id = "test-document-001"

    chunks = [
        "RAG combines retrieval with generation.",
        "Embeddings represent text as numerical vectors.",
    ]

    embeddings = [
        [0.1] * 384,
        [0.2] * 384,
    ]

    # Store actual vectors in temporary Qdrant storage.
    stored_count = vector_store.store_chunks(
        chunks=chunks,
        embeddings=embeddings,
        document_id=document_id,
        filename="sample.txt",
        file_type=".txt",
        chunking_method="recursive",
    )

    assert stored_count == 2

    # Verify that the vectors were actually persisted.
    count = isolated_qdrant_client.count(
        collection_name=vector_store.COLLECTION_NAME,
        exact=True,
    )

    assert count.count == 2

    # Retrieve stored points and inspect their metadata.
    records, next_page = isolated_qdrant_client.scroll(
        collection_name=vector_store.COLLECTION_NAME,
        limit=10,
        with_payload=True,
    )

    assert len(records) == 2
    assert next_page is None

    stored_payloads = [
        record.payload for record in records
    ]

    assert all(
        payload["document_id"] == document_id
        for payload in stored_payloads
    )

    assert {
        payload["chunk_text"] for payload in stored_payloads
    } == set(chunks)

    # Delete all vectors belonging to this document.
    vector_store.delete_document_chunks(document_id)

    remaining_count = isolated_qdrant_client.count(
        collection_name=vector_store.COLLECTION_NAME,
        exact=True,
    )

    assert remaining_count.count == 0