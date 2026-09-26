"""Prompt builder and schema definition for dual document comparison."""

from typing import Any, Dict, Tuple

from utils.security import compact_text, wrap_delimiters


def get_compare_schema() -> Dict[str, Any]:
    """Return JSON schema defining expected structure for contract comparison.

    Returns:
        JSON Schema dictionary.
    """
    return {
        "type": "object",
        "properties": {
            "overall_comparison": {
                "type": "string",
                "description": "Executive summary explaining the primary strategic differences between Document A and Document B."
            },
            "favorability": {
                "type": "string",
                "enum": ["Document A", "Document B", "Neither / Balanced"],
                "description": "Which document is overall more favorable from the user's perspective."
            },
            "differences": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "clause_topic": {"type": "string", "description": "Subject matter (e.g. Liability Cap, Termination Notice)."},
                        "doc_a_provision": {"type": "string", "description": "How Document A handles this topic."},
                        "doc_b_provision": {"type": "string", "description": "How Document B handles this topic."},
                        "more_favorable_to": {
                            "type": "string",
                            "enum": ["Document A", "Document B", "Equal"],
                            "description": "Which document has the more advantageous position."
                        },
                        "analysis": {"type": "string", "description": "Legal rationale explaining the difference in exposure."}
                    },
                    "required": ["clause_topic", "doc_a_provision", "doc_b_provision", "more_favorable_to", "analysis"]
                },
                "description": "Direct side-by-side comparison of specific provisions."
            },
            "missing_in_doc_a": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Protections, covenants, or clauses present in Document B but completely absent from Document A."
            },
            "missing_in_doc_b": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Protections, covenants, or clauses present in Document A but completely absent from Document B."
            }
        },
        "required": ["overall_comparison", "favorability", "differences", "missing_in_doc_a", "missing_in_doc_b"]
    }


def build_compare_prompt(doc_a_text: str, doc_b_text: str) -> Tuple[str, str]:
    """Construct system instruction and prompt for comparing two legal agreements.

    Args:
        doc_a_text: Sanitized plaintext of Document A (e.g. Baseline or Version 1).
        doc_b_text: Sanitized plaintext of Document B (e.g. Counterparty or Version 2).

    Returns:
        Tuple of (system_instruction, user_prompt).
    """
    system_instruction = (
        "You are LexiGuard's senior contract redlining and comparative analysis engine. "
        "Your role is to compare two contracts, identify key structural and substantive differences, "
        "detect clauses present in one but omitted in the other, and determine favorability.\n"
        "Return strictly valid JSON adhering to the schema."
    )

    doc_a_compact = compact_text(doc_a_text)
    doc_b_compact = compact_text(doc_b_text)

    wrapped_a = wrap_delimiters(doc_a_compact, tag="document_a")
    wrapped_b = wrap_delimiters(doc_b_compact, tag="document_b")

    user_prompt = (
        f"Compare the two agreements provided below:\n\n"
        f"--- DOCUMENT A ---\n{wrapped_a}\n\n"
        f"--- DOCUMENT B ---\n{wrapped_b}\n\n"
        f"Provide a structured comparative analysis, favorability evaluation, and identify all missing clauses. "
        f"Return only valid JSON matching the schema."
    )

    return system_instruction, user_prompt
