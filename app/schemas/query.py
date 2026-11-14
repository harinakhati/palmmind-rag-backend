from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        description="Natural-language question from the user."
    )

    limit: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of relevant chunks to retrieve."
    )

    document_id: str | None = Field(
        default=None,
        description="Optional document ID to restrict the search."
    )
    
    conversation_id: str | None = Field(
    default=None,
    max_length=100,
    description="ID used to continue an existing conversation."
)

class RetrievedChunk(BaseModel):
    document_id: str | None = None
    filename: str | None = None
    chunk_index: int | None = None
    chunk_text: str | None = None
    score: float


class QueryResponse(BaseModel):
    query: str
    answer: str
    conversation_id: str
    retrieved_chunks: list[RetrievedChunk]
    total_retrieved: int