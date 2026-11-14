import json
import redis

REDIS_URL = "redis://localhost:6379/0"

CONVERSATION_TTL = 1800  # 30 minutes


def get_redis_client():
    return redis.Redis.from_url(
        REDIS_URL,
        decode_responses=True,
    )


def get_conversation_history(
    client: redis.Redis,
    conversation_id: str,
) -> list[dict]:

    key = f"conversation:{conversation_id}"

    history = client.get(key)

    if history is None:
        return []

    return json.loads(history)


def save_conversation_history(
    client: redis.Redis,
    conversation_id: str,
    history: list[dict],
) -> None:

    key = f"conversation:{conversation_id}"

    client.set(
        key,
        json.dumps(history),
        ex=CONVERSATION_TTL,
    )