from fastapi.testclient import TestClient

import uuid

from app.main import app
from app.api import document_routes


def test_query_with_no_relevant_chunks(monkeypatch):
    # Mock retrieval so the test does not depend on Qdrant.
    def mock_retrieval(**kwargs):
        return []

    monkeypatch.setattr(
        document_routes,
        "retrieve_relevant_chunks",
        mock_retrieval,
    )

    # Send a request to the query endpoint.
    with TestClient(app) as client:
        response = client.post(
            "/documents/query",
            json={
                "query": "Explain quantum computing in detail.",
                "limit": 3,
                "document_id": "nonexistent-document-123",
            },
        )

    print("Response:", response.status_code, response.text)
    # Check the HTTP response.
    assert response.status_code == 200

    data = response.json()

    # Check the response content.
    assert data["query"] == "Explain quantum computing in detail."

    assert data["answer"] == (
    "I couldn't find relevant information in the uploaded "
    "documents to answer your question."
)

    assert data["retrieved_chunks"] == []
    assert data["total_retrieved"] == 0
    
def test_query_with_relevant_chunks(monkeypatch):
    # Mock retrieval results.
    mock_chunks = [
        {
            "document_id": "test-document-001",
            "filename": "sample.txt",
            "chunk_index": 0,
            "chunk_text": "RAG combines retrieval with language generation.",
            "score": 0.6685,
        }
    ]

    def mock_retrieval(**kwargs):
        return mock_chunks

    # Mock Gemini answer generation.
    def mock_generation(
        query,
        retrieved_chunks,
        conversation_history=None,
    ):
        assert query == "What is RAG?"
        assert len(retrieved_chunks) == 1

        return "RAG combines retrieval with language generation."

    monkeypatch.setattr(
        document_routes,
        "retrieve_relevant_chunks",
        mock_retrieval,
    )

    monkeypatch.setattr(
        document_routes,
        "generate_answer",
        mock_generation,
    )

    with TestClient(app) as client:
        response = client.post(
            "/documents/query",
            json={
                "query": "What is RAG?",
                "limit": 3,
            },
        )

    print("Response:", response.status_code, response.text)
    assert response.status_code == 200

    data = response.json()

    assert data["query"] == "What is RAG?"
    assert data["answer"] == (
        "RAG combines retrieval with language generation."
    )
    assert data["total_retrieved"] == 1
    assert len(data["retrieved_chunks"]) == 1
    assert data["retrieved_chunks"][0]["filename"] == "sample.txt"
    
def test_query_with_empty_string():
    client = TestClient(app)

    response = client.post(
        "/documents/query",
        json={
            "query": "",
            "limit": 3,
        },
    )

    assert response.status_code == 422


def test_query_with_invalid_limit():
    
    with TestClient(app) as client:
        response = client.post(
            "/documents/query",
            json={
                "query": "What is RAG?",
                "limit": 0,
            },
        )

    assert response.status_code == 422
    
def test_multi_turn_conversation(monkeypatch):

    mock_chunks = [
        {
            "document_id": "test-document-001",
            "filename": "sample.txt",
            "chunk_index": 0,
            "chunk_text": "RAG combines retrieval with language generation.",
            "score": 0.85,
        }
    ]

    def mock_retrieval(**kwargs):
        return mock_chunks

    received_history = []

    def mock_generation(
        query,
        retrieved_chunks,
        conversation_history=None,
    ):
        received_history.append(
            [message.copy() for message in (conversation_history or [])]
)

        if query == "What is RAG?":
            return "RAG combines retrieval with language generation."

        return "Its advantages include more grounded and relevant answers."

    monkeypatch.setattr(
        document_routes,
        "retrieve_relevant_chunks",
        mock_retrieval,
    )

    monkeypatch.setattr(
        document_routes,
        "generate_answer",
        mock_generation,
    )

    with TestClient(app) as client:

        # First question: Start a new conversation
        first_response = client.post(
            "/documents/query",
            json={
                "query": "What is RAG?",
                "limit": 3,
            },
        )

        assert first_response.status_code == 200

        first_data = first_response.json()
        conversation_id = first_data["conversation_id"]

        # Second question: Continue the same conversation
        second_response = client.post(
            "/documents/query",
            json={
                "query": "What are its advantages?",
                "limit": 3,
                "conversation_id": conversation_id,
            },
        )

        assert second_response.status_code == 200

        second_data = second_response.json()

        # Both requests must belong to the same conversation
        assert second_data["conversation_id"] == conversation_id

        # First request should have no previous history
        assert received_history[0] == []

        # Second request should contain the first exchange
        assert len(received_history[1]) == 2

        assert received_history[1][0]["role"] == "user"
        assert received_history[1][0]["content"] == "What is RAG?"

        assert received_history[1][1]["role"] == "assistant"
        assert received_history[1][1]["content"] == (
            "RAG combines retrieval with language generation."
        )

        # Verify the second answer
        assert second_data["answer"] == (
            "Its advantages include more grounded and relevant answers."
        )

        # Clean up Redis test data
        app.state.redis.delete(f"conversation:{conversation_id}")