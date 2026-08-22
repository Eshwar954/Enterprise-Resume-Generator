from pathlib import Path

from fastapi import UploadFile


TEXT_EXTENSIONS = {".txt", ".md", ".text"}
PDF_EXTENSIONS = {".pdf"}
DOCX_EXTENSIONS = {".docx"}


async def extract_text(file: UploadFile) -> str:
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()

    supported_extensions = (
        TEXT_EXTENSIONS
        | PDF_EXTENSIONS
        | DOCX_EXTENSIONS
    )

    if extension not in supported_extensions:
        raise ValueError(
            f"Unsupported file type '{extension or 'unknown'}'. "
            "Upload PDF, DOCX, or TXT."
        )

    content = await file.read()

    if not content:
        raise ValueError(
            f"Uploaded file '{filename}' is empty."
        )

    if extension in TEXT_EXTENSIONS:
        return content.decode(
            "utf-8-sig",
            errors="replace",
        ).strip()

    if extension in PDF_EXTENSIONS:
        return _extract_pdf(content, filename)

    if extension in DOCX_EXTENSIONS:
        return _extract_docx(content, filename)

    raise ValueError(
        "Unable to extract text from the uploaded file."
    )


def _extract_pdf(
    content: bytes,
    filename: str,
) -> str:
    from io import BytesIO

    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ValueError(
            "PDF support requires pypdf. "
            "Run: pip install pypdf"
        ) from exc

    try:
        reader = PdfReader(BytesIO(content))

        pages = []

        for page in reader.pages:
            text = page.extract_text() or ""

            if text.strip():
                pages.append(text)

        result = "\n\n".join(pages).strip()

    except Exception as exc:
        raise ValueError(
            f"Could not read PDF '{filename}'."
        ) from exc

    if not result:
        raise ValueError(
            f"Could not extract readable text from "
            f"PDF '{filename}'."
        )

    return result


def _extract_docx(
    content: bytes,
    filename: str,
) -> str:
    from io import BytesIO

    try:
        from docx import Document
    except ImportError as exc:
        raise ValueError(
            "DOCX support requires python-docx. "
            "Run: pip install python-docx"
        ) from exc

    try:
        document = Document(BytesIO(content))

        paragraphs = [
            paragraph.text.strip()
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        result = "\n".join(paragraphs).strip()

    except Exception as exc:
        raise ValueError(
            f"Could not read DOCX '{filename}'."
        ) from exc

    if not result:
        raise ValueError(
            f"Could not extract readable text from "
            f"DOCX '{filename}'."
        )

    return result