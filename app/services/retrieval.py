from qdrant_client import models

from app.services.embedding import generate_embeddings
from app.services.vector_store import client, COLLECTION_NAME


def retrieve_relevant_chunks(
    query: str,
    limit: int = 5,
    document_id: str | None = None,
) -> list[dict]:

    if not query.strip():
        raise ValueError("Query cannot be empty.")

    if limit <= 0:
        raise ValueError("Limit must be greater than zero.")

    # Convert the user's question into an embedding.
    query_embedding = generate_embeddings([query])[0]

    # Apply document-specific filtering when document_id is provided.
    query_filter = None

    if document_id:
        query_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="document_id",
                    match=models.MatchValue(value=document_id),
                )
            ]
        )

    # Search Qdrant.
    search_results = client.query_points(
    collection_name=COLLECTION_NAME,
    query=query_embedding,
    query_filter=query_filter,
    limit=limit,
    score_threshold=0.30,
    with_payload=True,
)

    retrieved_chunks = []

    for point in search_results.points:
        payload = point.payload or {}

        retrieved_chunks.append({
            "document_id": payload.get("document_id"),
            "filename": payload.get("filename"),
            "chunk_index": payload.get("chunk_index"),
            "chunk_text": payload.get("chunk_text"),
            "score": point.score,
        })

    return retrieved_chunks