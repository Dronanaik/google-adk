import os
from typing import Dict


def _read_text_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _read_pdf(file_path: str) -> str:
    try:
        from pdfminer.high_level import extract_text  # type: ignore
    except Exception:
        raise RuntimeError(
            "pdfminer.six is required to read PDF resumes. Install it: pip install pdfminer.six"
        )
    return extract_text(file_path) or ""


def _read_docx(file_path: str) -> str:
    try:
        import docx  # type: ignore
    except Exception:
        raise RuntimeError(
            "python-docx is required to read DOCX resumes. Install it: pip install python-docx"
        )
    doc = docx.Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs)


def ingest_resume(file_path: str) -> Dict:
    """Load a resume from PDF, DOCX, or text and return plain text with metadata.

    Args:
        file_path: Absolute path to a PDF, DOCX, or text file containing the resume.

    Returns:
        dict: { status, meta:{path, ext, size_bytes}, text }
    """
    if not file_path or not os.path.exists(file_path):
        return {
            "status": "error",
            "error_message": "Resume file path missing or does not exist",
        }

    ext = os.path.splitext(file_path)[1].lower()
    size = os.path.getsize(file_path)

    if ext in (".txt", ".md", ".log"):
        text = _read_text_file(file_path)
    elif ext == ".pdf":
        text = _read_pdf(file_path)
    elif ext in (".docx",):
        text = _read_docx(file_path)
    else:
        return {
            "status": "error",
            "error_message": f"Unsupported resume format: {ext}",
        }

    return {
        "status": "success",
        "meta": {"path": os.path.abspath(file_path), "ext": ext, "size_bytes": size},
        "text": text.strip(),
    }


