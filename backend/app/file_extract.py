"""Résumé file → plain text extraction.

Handles the three formats the upload UI accepts (PDF, DOCX, TXT) plus text in
arbitrary encodings, so a real-world résumé upload doesn't fail on decoding.
"""
import io


def extract_resume_text(filename: str, content: bytes) -> str:
    """Extract plain text from an uploaded résumé file.

    Detection is by extension first, then by magic bytes, so a mislabeled file
    still works. Raises ValueError if the format can't be read.
    """
    name = (filename or "").lower()

    if name.endswith(".pdf") or content[:5] == b"%PDF-":
        return _extract_pdf(content)

    if name.endswith(".docx") or content[:4] == b"PK\x03\x04":
        return _extract_docx(content)

    # Plain text — try the common encodings before giving up.
    for encoding in ("utf-8-sig", "utf-8", "utf-16", "latin-1"):
        try:
            return content.decode(encoding)
        except (UnicodeDecodeError, UnicodeError):
            continue
    # Last resort: never raise on a text file — drop undecodable bytes.
    return content.decode("utf-8", errors="ignore")


def _extract_pdf(content: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover
        raise ValueError("PDF support is not installed (pip install pypdf).") from exc

    try:
        reader = PdfReader(io.BytesIO(content))
        pages = [(page.extract_text() or "") for page in reader.pages]
    except Exception as exc:
        raise ValueError("Could not read this PDF — it may be corrupted.") from exc

    return "\n".join(p for p in pages if p.strip())


def _extract_docx(content: bytes) -> str:
    try:
        import docx  # python-docx
    except ImportError as exc:  # pragma: no cover
        raise ValueError("DOCX support is not installed (pip install python-docx).") from exc

    try:
        document = docx.Document(io.BytesIO(content))
    except Exception as exc:
        raise ValueError("Could not read this DOCX file — it may be corrupted.") from exc

    return "\n".join(p.text for p in document.paragraphs)
