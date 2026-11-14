from uuid import uuid4

import uuid

from app.services.redis_service import (
    get_conversation_history,
    save_conversation_history,
)
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException,
    Depends,
    Request,
)

from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Document
from app.schemas.query import QueryRequest, QueryResponse, RetrievedChunk

from app.services.retrieval import retrieve_relevant_chunks

from app.services.vector_store import (
    store_chunks,
    delete_document_chunks,
)

from app.services.embedding import generate_embeddings

from app.services.document_extractor import (
    extract_text_from_pdf,
    extract_text_from_txt,
)

from app.services.chunking import (
    fixed_size_chunking,
    recursive_character_chunking,
)


from app.services.llm import generate_answer

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

ALLOWED_EXTENSIONS = {".pdf", ".txt"}


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    chunking_method: str = Form("recursive"),
    chunk_size: int = Form(1000),
    overlap: int = Form(200),
    db: Session = Depends(get_db),
):
    """Upload a document, process it, and store its metadata and vectors."""

    # 1. Validate filename
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    filename = file.filename.strip()

    extension = (
        "." + filename.rsplit(".", 1)[-1].lower()
        if "." in filename
        else ""
    )

    # 2. Validate file extension
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported.",
        )

    # 3. Validate chunking method
    if chunking_method not in {"fixed", "recursive"}:
        raise HTTPException(
            status_code=400,
            detail="Chunking method must be 'fixed' or 'recursive'.",
        )

    # 4. Read uploaded file
    file_content = await file.read()

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    # 5. Extract document text
    try:
        if extension == ".pdf":
            extracted_text = extract_text_from_pdf(file_content)
        else:
            extracted_text = extract_text_from_txt(file_content)

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="TXT file must use UTF-8 encoding.",
        )

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not read the uploaded document. Please check the file.",
        )

    # 6. Check extracted text
    if not extracted_text:
        raise HTTPException(
            status_code=400,
            detail="No extractable text found in the document.",
        )

    # 7. Generate document chunks
    try:
        if chunking_method == "fixed":
            chunks = fixed_size_chunking(
                extracted_text,
                chunk_size=chunk_size,
                overlap=overlap,
            )
        else:
            chunks = recursive_character_chunking(
                extracted_text,
                chunk_size=chunk_size,
                overlap=overlap,
            )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    # 8. Generate embeddings
    try:
        embeddings = generate_embeddings(chunks)

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Embedding generation failed: {str(error)}",
        )

    # 9. Generate document ID
    document_id = str(uuid4())

    # 10. Store chunks and embeddings in Qdrant
    try:
        stored_count = store_chunks(
            chunks=chunks,
            embeddings=embeddings,
            document_id=document_id,
            filename=filename,
            file_type=extension,
            chunking_method=chunking_method,
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Vector storage failed: {str(error)}",
        )

    # 11. Save document metadata in MySQL
    try:
        document = Document(
            document_id=document_id,
            filename=filename,
            file_type=extension,
            chunking_method=chunking_method,
            chunk_size=chunk_size,
            overlap=overlap,
            character_count=len(extracted_text),
            chunk_count=len(chunks),
            embedding_dimensions=len(embeddings[0]) if embeddings else 0,
        )

        db.add(document)
        db.commit()

    except Exception as error:
        db.rollback()

        # Remove vectors if metadata storage fails
        try:
            delete_document_chunks(document_id)
        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail="Document metadata storage failed.",
        )

    # 12. Return response
    return {
        "document_id": document_id,
        "filename": filename,
        "file_type": extension,
        "message": "Document uploaded and stored successfully.",
        "chunking_method": chunking_method,
        "chunk_size": chunk_size,
        "overlap": overlap,
        "character_count": len(extracted_text),
        "chunk_count": len(chunks),
        "embedding_count": len(embeddings),
        "embedding_dimensions": len(embeddings[0]) if embeddings else 0,
        "stored_vectors": stored_count,
        "metadata_database": "MySQL",
        "vector_database": "Qdrant",
    }

@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    http_request: Request,
):
    try:
        if not request.query.strip():
            raise HTTPException(
                status_code=400,
                detail="Query cannot be empty."
            )

        # 1. Get or generate conversation ID
        conversation_id = request.conversation_id or str(uuid.uuid4())

        # 2. Access Redis client
        redis_client = http_request.app.state.redis

        # 3. Retrieve previous conversation history
        conversation_history = get_conversation_history(
            redis_client,
            conversation_id,
        )

        # 4. Retrieve relevant document chunks
        retrieved_chunks = retrieve_relevant_chunks(
            query=request.query,
            limit=request.limit,
            document_id=request.document_id,
        )

        # 5. Generate answer using conversation history
        answer = generate_answer(
            query=request.query,
            retrieved_chunks=retrieved_chunks,
            conversation_history=conversation_history,
        )

        # 6. Format retrieved chunks
        formatted_chunks = [
            RetrievedChunk(**chunk)
            for chunk in retrieved_chunks
        ]

        # 7. Update conversation history
        conversation_history.extend([
            {
                "role": "user",
                "content": request.query,
            },
            {
                "role": "assistant",
                "content": answer,
            },
        ])

        # Keep the latest 20 messages
        conversation_history = conversation_history[-20:]

        # 8. Save updated history in Redis
        save_conversation_history(
            redis_client,
            conversation_id,
            conversation_history,
        )

        return QueryResponse(
            query=request.query,
            answer=answer,
            conversation_id=conversation_id,
            retrieved_chunks=formatted_chunks,
            total_retrieved=len(formatted_chunks),
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Document retrieval failed: {str(error)}"
        )
