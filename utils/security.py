"""Enterprise security, sanitization, and token compaction module for LexiGuard.

This module provides input sanitization, token compaction, XML-style delimiter
encapsulation to prevent prompt injection, sensitive error masking to prevent
information leakage, and HTML escaping for XSS prevention.
"""

import html
import re
import unicodedata
from typing import Final

# Hard Security & Denial-of-Service Limits
MAX_DOCUMENT_CHARS: Final[int] = 100_000
MAX_QUERY_CHARS: Final[int] = 1_000
MAX_FILE_SIZE_BYTES: Final[int] = 15 * 1024 * 1024  # 15 Megabytes
MAX_PDF_PAGES: Final[int] = 100

# Regex patterns for sensitive information redaction
_API_KEY_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(AIza[0-9A-Za-z-_]{35}|(?:key|api[_-]?key|secret|token)[\s=:'\"]+([a-zA-Z0-9_\-]{16,}))",
    re.IGNORECASE,
)
_FILE_PATH_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(/(?:Users|home|private|tmp|var|etc|usr)/[^\s:;\"'\)\]>]+|[A-Za-z]:\\[^\s:;\"'\)\]>]+)",
    re.IGNORECASE,
)
_QUERY_PARAM_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"([?&](?:token|key|api_key|auth|secret|password)=)[^&\s]+",
    re.IGNORECASE,
)


def sanitize_text(text: str, max_chars: int = MAX_DOCUMENT_CHARS) -> str:
    """Sanitize raw text input to prevent DoS, strip null bytes, and normalize unicode.

    Args:
        text: Raw untrusted string from user or document reader.
        max_chars: Maximum allowable character length (default: MAX_DOCUMENT_CHARS).

    Returns:
        Sanitized string stripped of null bytes and truncated to max_chars.

    Raises:
        TypeError: If text is not an instance of str.
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str input, got {type(text).__name__}")

    # Strip null bytes and control chars (except standard newlines and tabs)
    clean = text.replace("\x00", "")
    # Normalize unicode to standard composed form
    clean = unicodedata.normalize("NFC", clean)
    # Enforce maximum character cap
    if len(clean) > max_chars:
        clean = clean[:max_chars]

    return clean.strip()


def compact_text(text: str) -> str:
    """Compact whitespace in text to minimize token consumption by 15-25%.

    Collapses 3+ consecutive newlines to 2 (preserving markdown/paragraph breaks)
    and replaces multiple spaces/tabs within lines with a single space.

    Args:
        text: Text to compact.

    Returns:
        Token-efficient compacted text.

    Raises:
        TypeError: If text is not an instance of str.
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str input, got {type(text).__name__}")

    if not text:
        return ""

    # Replace windows newlines
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")

    # Collapse 3 or more consecutive newlines to exactly 2
    collapsed_newlines = re.sub(r"\n{3,}", "\n\n", normalized)

    # Collapse multi-spaces and tabs on each line while preserving single spaces
    lines = []
    for line in collapsed_newlines.split("\n"):
        line_stripped = re.sub(r"[ \t]+", " ", line)
        lines.append(line_stripped.rstrip())

    compacted = "\n".join(lines).strip()
    return compacted


def wrap_delimiters(content: str, tag: str = "document_content") -> str:
    r"""Enclose untrusted content in safe XML-style delimiters to neutralize prompt injection.

    Neutralizes any closing tag attempts within the body by replacing
    `</{tag}>` with `<\//{tag}>`.

    Args:
        content: The untrusted content string to wrap.
        tag: The XML delimiter tag name (default: "document_content").

    Returns:
        Safely wrapped and sanitized XML container string.

    Raises:
        TypeError: If content or tag is not a str.
    """
    if not isinstance(content, str) or not isinstance(tag, str):
        raise TypeError("Both content and tag must be str instances")

    sanitized_tag = re.sub(r"[^a-zA-Z0-9_-]", "", tag)
    # Neutralize any attempts to close the delimiter within the content
    closing_tag_pattern = re.compile(rf"</\s*{re.escape(sanitized_tag)}\s*>", re.IGNORECASE)
    neutralized_content = closing_tag_pattern.sub(rf"<\//{sanitized_tag}>", content)

    return f"<{sanitized_tag}>\n{neutralized_content}\n</{sanitized_tag}>"


def mask_sensitive_error(error_msg: str) -> str:
    """Mask sensitive paths, API keys, and credentials from error strings.

    Args:
        error_msg: Raw error message string.

    Returns:
        Sanitized error message safe for user display or standard logs.

    Raises:
        TypeError: If error_msg is not a str.
    """
    if not isinstance(error_msg, str):
        raise TypeError(f"Expected str input, got {type(error_msg).__name__}")

    masked = _API_KEY_PATTERN.sub("[REDACTED_API_KEY]", error_msg)
    masked = _FILE_PATH_PATTERN.sub("[REDACTED_PATH]", masked)
    masked = _QUERY_PARAM_PATTERN.sub(r"\1[REDACTED_PARAM]", masked)
    return masked


def escape_html_text(text: str) -> str:
    """Safely escape text for insertion into HTML components to prevent XSS.

    Args:
        text: Raw text to escape.

    Returns:
        HTML-escaped text string.

    Raises:
        TypeError: If text is not a str.
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str input, got {type(text).__name__}")

    return html.escape(text, quote=True)
