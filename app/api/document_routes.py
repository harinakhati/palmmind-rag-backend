from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.document_extractor import (
    extract_text_from_pdf,
    extract_text_from_txt,
)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

ALLOWED_EXTENSIONS = {".pdf", ".txt"}


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF or TXT document and extract its text."""

    # 1. Validate filename
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    filename = file.filename.strip()
    extension = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    # 2. Validate file extension
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported.",
        )

    # 3. Read uploaded file
    file_content = await file.read()

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    # 4. Extract document text
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

    # 5. Check extracted text
    if not extracted_text:
        raise HTTPException(
            status_code=400,
            detail="No extractable text found in the document.",
        )

    # 6. Return response
    return {
        "filename": filename,
        "file_type": extension,
        "message": "Document uploaded and text extracted successfully.",
        "character_count": len(extracted_text),
        "extracted_text": extracted_text,
    }


git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/harinakhati/palmmind-rag-backend.git
git push -u origin main