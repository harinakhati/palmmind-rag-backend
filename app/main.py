from fastapi import FastAPI

from app.api.document_routes import router as document_router
# from app.services.document_extractor import 

app = FastAPI(
    title="PalmMind RAG Backend",
    description="Backend API for document ingestion and retrieval-augmented generation.",
    version="1.0.0",
)

app.include_router(document_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to PalmMind RAG Backend",
        "status": "running",
    }