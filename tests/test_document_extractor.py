import pymupdf

from app.services.document_extractor import extract_text_from_pdf


def test_extract_text_from_pdf():
    # Create a real PDF in memory.
    document = pymupdf.open()

    page = document.new_page()
    page.insert_text(
        (72, 72),
        "PalmMind RAG PDF extraction test."
    )

    pdf_bytes = document.tobytes()
    document.close()

    # Extract text using our actual extraction function.
    extracted_text = extract_text_from_pdf(pdf_bytes)

    assert "PalmMind RAG PDF extraction test." in extracted_text