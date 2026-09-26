"""Service for plain-language document summarization and legal jargon glossary."""

from typing import Any, Dict

from prompts.simplify import build_simplify_prompt, get_simplify_schema
from services.gemini_client import gemini_client


def simplify_document(
    document_text: str,
    reading_level: str = "standard",
    language: str = "english",
) -> Dict[str, Any]:
    """Generate executive summary, key takeaways, and jargon glossary for a document.

    Args:
        document_text: Plaintext content of the contract or document.
        reading_level: "standard" or "eli15" (Explain Like I'm 15).
        language: "english", "hindi", or "kannada".

    Returns:
        Dictionary containing 'summary', 'key_points', and 'glossary'.

    Raises:
        ValueError: If document_text is empty.
        RuntimeError: If analysis fails and no fallback could be resolved.
    """
    if not document_text or not document_text.strip():
        raise ValueError("Cannot simplify an empty document.")

    system_instruction, user_prompt = build_simplify_prompt(
        document_text=document_text,
        reading_level=reading_level,
        language=language,
    )
    schema = get_simplify_schema()

    result = gemini_client.generate_json(
        system_instruction=system_instruction,
        prompt=user_prompt,
        schema=schema,
        task="light",
        task_fallback_name="simplify",
    )

    return result
