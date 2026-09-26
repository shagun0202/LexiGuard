"""Security and sanitization utilities for LexiGuard."""

from utils.security import (
    MAX_DOCUMENT_CHARS,
    MAX_FILE_SIZE_BYTES,
    MAX_PDF_PAGES,
    MAX_QUERY_CHARS,
    compact_text,
    escape_html_text,
    mask_sensitive_error,
    sanitize_text,
    wrap_delimiters,
)

__all__ = [
    "MAX_DOCUMENT_CHARS",
    "MAX_QUERY_CHARS",
    "MAX_FILE_SIZE_BYTES",
    "MAX_PDF_PAGES",
    "sanitize_text",
    "compact_text",
    "wrap_delimiters",
    "mask_sensitive_error",
    "escape_html_text",
]
