import pymupdf


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from a PDF document."""

    text = []

    with pymupdf.open(stream=file_content, filetype="pdf") as document:
        for page in document:
            text.append(page.get_text())

    return "\n".join(text).strip()


def extract_text_from_txt(file_content: bytes) -> str:
    """Extract text from a TXT document."""

    return file_content.decode("utf-8-sig").strip()
