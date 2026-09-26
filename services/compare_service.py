"""Service for dual contract comparison and favorability analysis."""

from typing import Any, Dict

from prompts.compare import build_compare_prompt, get_compare_schema
from services.gemini_client import gemini_client


def compare_documents(doc_a_text: str, doc_b_text: str) -> Dict[str, Any]:
    """Execute side-by-side comparison between two contracts.

    Identifies substantive differences, favorability, and missing clauses.

    Args:
        doc_a_text: Plaintext of Document A (e.g. Baseline).
        doc_b_text: Plaintext of Document B (e.g. Counterparty version).

    Returns:
        Dictionary with overall_comparison, favorability, differences,
        missing_in_doc_a, and missing_in_doc_b.

    Raises:
        ValueError: If either document text is empty.
    """
    if not doc_a_text or not doc_a_text.strip():
        raise ValueError("Document A cannot be empty for comparison.")
    if not doc_b_text or not doc_b_text.strip():
        raise ValueError("Document B cannot be empty for comparison.")

    system_instruction, user_prompt = build_compare_prompt(doc_a_text, doc_b_text)
    schema = get_compare_schema()

    result = gemini_client.generate_json(
        system_instruction=system_instruction,
        prompt=user_prompt,
        schema=schema,
        task="heavy",
        task_fallback_name="compare",
    )

    return result
