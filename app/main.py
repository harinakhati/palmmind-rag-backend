from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.document_routes import router as document_router
from app.services.vector_store import client as qdrant_client
from app.services.redis_service import get_redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Initialize Redis connection
    redis_client = get_redis_client()
    redis_client.ping()

    app.state.redis = redis_client

    print("Redis connected successfully.")

    yield

    # Close connections during application shutdown
    redis_client.close()
    qdrant_client.close()

    print("Redis and Qdrant connections closed.")


app = FastAPI(
    title="PalmMind RAG Backend",
    description="Backend API for document ingestion and retrieval-augmented generation.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(document_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to PalmMind RAG Backend",
        "status": "running",
    }