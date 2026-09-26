"""Secure file parsing module for PDF, DOCX, and TXT documents.

Enforces file size and page count limits, handles encoding and format errors
gracefully, and provides file signature hashing for efficient UI caching.
"""

import hashlib
import io
import zipfile
from typing import Optional, Tuple

import docx
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from utils.security import (
    MAX_DOCUMENT_CHARS,
    MAX_FILE_SIZE_BYTES,
    MAX_PDF_PAGES,
    sanitize_text,
)


def compute_file_signature(file_bytes: bytes, filename: str) -> str:
    """Compute a deterministic hash signature of an uploaded file.

    Used by the presentation layer to detect file changes and avoid redundant
    re-parsing or re-running analyses.

    Args:
        file_bytes: The raw byte content of the file.
        filename: The original name of the uploaded file.

    Returns:
        Hex-encoded SHA-256 digest string.

    Raises:
        TypeError: If file_bytes is not bytes or filename is not str.
    """
    if not isinstance(file_bytes, bytes) or not isinstance(filename, str):
        raise TypeError("file_bytes must be bytes and filename must be str")

    hasher = hashlib.sha256()
    hasher.update(filename.encode("utf-8", errors="ignore"))
    hasher.update(str(len(file_bytes)).encode("ascii"))
    hasher.update(file_bytes[:4096])  # Hash first 4KB for fast uniqueness
    return hasher.hexdigest()


def extract_text_from_file(file_bytes: bytes, filename: str) -> Tuple[str, Optional[str]]:
    """Extract and sanitize plain text from a supported file format (PDF, DOCX, TXT/MD).

    Enforces MAX_FILE_SIZE_BYTES (15 MB) and MAX_PDF_PAGES (100 pages).

    Args:
        file_bytes: The raw byte content of the document.
        filename: The filename with extension (e.g. 'contract.pdf').

    Returns:
        A tuple of (extracted_text, error_message).
        If successful, extracted_text is populated and error_message is None.
        If an error occurred, extracted_text is empty and error_message describes the issue.

    Raises:
        TypeError: If file_bytes is not bytes or filename is not str.
    """
    if not isinstance(file_bytes, bytes) or not isinstance(filename, str):
        raise TypeError("file_bytes must be bytes and filename must be str")

    if not file_bytes:
        return "", "The uploaded file is empty (0 bytes)."

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        mb_size = len(file_bytes) / (1024 * 1024)
        return "", f"File size ({mb_size:.1f} MB) exceeds the maximum allowed limit of 15 MB."

    lower_name = filename.lower()

    try:
        if lower_name.endswith(".pdf"):
            return _extract_from_pdf(file_bytes)
        elif lower_name.endswith(".docx"):
            return _extract_from_docx(file_bytes)
        elif lower_name.endswith((".txt", ".md", ".rtf")):
            return _extract_from_txt(file_bytes)
        else:
            return "", f"Unsupported file extension in '{filename}'. Please upload a PDF, DOCX, or TXT file."
    except Exception as exc:  # Guard against unexpected parsing library defects
        return "", f"Failed to parse document: {str(exc)}"


def _extract_from_pdf(file_bytes: bytes) -> Tuple[str, Optional[str]]:
    """Internal helper to extract text from PDF bytes.

    Args:
        file_bytes: Raw PDF bytes.

    Returns:
        Tuple of (extracted_text, error_message).
    """
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        num_pages = len(reader.pages)

        if num_pages == 0:
            return "", "PDF file contains no readable pages."

        if num_pages > MAX_PDF_PAGES:
            return "", f"PDF has {num_pages} pages, which exceeds the limit of {MAX_PDF_PAGES} pages."

        text_parts = []
        for idx, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        full_text = "\n\n".join(text_parts).strip()
        if not full_text:
            return "", "Could not extract readable text from PDF (it may be scanned or image-only)."

        sanitized = sanitize_text(full_text, max_chars=MAX_DOCUMENT_CHARS)
        return sanitized, None

    except PdfReadError as err:
        return "", f"Corrupted or invalid PDF file: {str(err)}"
    except (ValueError, KeyError) as err:
        return "", f"Error reading PDF structure: {str(err)}"


def _extract_from_docx(file_bytes: bytes) -> Tuple[str, Optional[str]]:
    """Internal helper to extract text from DOCX bytes.

    Args:
        file_bytes: Raw DOCX bytes.

    Returns:
        Tuple of (extracted_text, error_message).
    """
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        
        # Also extract table text
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    paragraphs.append(row_text)

        full_text = "\n\n".join(paragraphs).strip()
        if not full_text:
            return "", "DOCX file contains no readable text."

        sanitized = sanitize_text(full_text, max_chars=MAX_DOCUMENT_CHARS)
        return sanitized, None

    except zipfile.BadZipFile:
        return "", "Invalid or corrupted DOCX file (archive structure is invalid)."
    except (ValueError, KeyError, AttributeError) as err:
        return "", f"Error reading DOCX document: {str(err)}"


def _extract_from_txt(file_bytes: bytes) -> Tuple[str, Optional[str]]:
    """Internal helper to extract text from plaintext bytes.

    Args:
        file_bytes: Raw plaintext bytes.

    Returns:
        Tuple of (extracted_text, error_message).
    """
    for encoding in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            raw_text = file_bytes.decode(encoding)
            sanitized = sanitize_text(raw_text, max_chars=MAX_DOCUMENT_CHARS)
            return sanitized, None
        except UnicodeDecodeError:
            continue

    return "", "Could not decode text file using standard character encodings (UTF-8, Latin-1)."
