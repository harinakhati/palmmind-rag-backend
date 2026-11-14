from pathlib import Path
from uuid import uuid4

from qdrant_client import QdrantClient, models


# Project root directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Persistent storage directory
QDRANT_PATH = BASE_DIR / "qdrant_storage"

# Collection name
COLLECTION_NAME = "document_chunks"

# Embedding dimensions
VECTOR_SIZE = 384


# Initialize Qdrant client
client = QdrantClient(
    path=str(QDRANT_PATH)
)


def create_collection() -> None:
    """
    Create the Qdrant collection if it does not already exist.
    """

    if not client.collection_exists(COLLECTION_NAME):

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE,
            ),
        )


def store_chunks(
    chunks: list[str],
    embeddings: list[list[float]],
    document_id: str,
    filename: str,
    file_type: str,
    chunking_method: str,
) -> int:
    """
    Store document chunks and their embeddings in Qdrant.
    """

    if len(chunks) != len(embeddings):
        raise ValueError(
            "Number of chunks must match number of embeddings."
        )

    if not chunks:
        return 0

    create_collection()

    points = []

    for index, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):

        points.append(
            models.PointStruct(
                id=str(uuid4()),
                vector=embedding,
                payload={
                    "document_id": document_id,
                    "filename": filename,
                    "file_type": file_type,
                    "chunk_index": index,
                    "chunk_text": chunk,
                    "chunking_method": chunking_method,
                },
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

    return len(points)

def delete_document_chunks(document_id: str) -> None:
    """Delete all Qdrant chunks belonging to a document."""

    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(value=document_id),
                    )
                ]
            )
        ),
    )