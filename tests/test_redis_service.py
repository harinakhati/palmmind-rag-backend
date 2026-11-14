import uuid

import pytest

from app.services.redis_service import (
    get_redis_client,
    get_conversation_history,
    save_conversation_history,
    CONVERSATION_TTL,
)


@pytest.fixture
def redis_client():
    client = get_redis_client()
    client.ping()

    yield client

    client.close()


def test_save_and_retrieve_conversation(redis_client):
    conversation_id = str(uuid.uuid4())

    history = [
        {
            "role": "user",
            "content": "What is RAG?",
        },
        {
            "role": "assistant",
            "content": "RAG combines retrieval with generation.",
        },
    ]

    save_conversation_history(
        redis_client,
        conversation_id,
        history,
    )

    retrieved_history = get_conversation_history(
        redis_client,
        conversation_id,
    )

    assert retrieved_history == history

    redis_client.delete(f"conversation:{conversation_id}")


def test_get_nonexistent_conversation(redis_client):
    conversation_id = str(uuid.uuid4())

    history = get_conversation_history(
        redis_client,
        conversation_id,
    )

    assert history == []


def test_conversation_has_expiration(redis_client):
    conversation_id = str(uuid.uuid4())

    history = [
        {
            "role": "user",
            "content": "Explain embeddings.",
        }
    ]

    save_conversation_history(
        redis_client,
        conversation_id,
        history,
    )

    ttl = redis_client.ttl(
        f"conversation:{conversation_id}"
    )

    assert 0 < ttl <= CONVERSATION_TTL

    redis_client.delete(f"conversation:{conversation_id}")