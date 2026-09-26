"""Prompt builder and schema definition for risk and clause analysis."""

from typing import Any, Dict, Tuple

from utils.security import compact_text, wrap_delimiters


def get_risk_schema() -> Dict[str, Any]:
    """Return JSON schema defining expected structure for contract risk analysis.

    Returns:
        JSON Schema dictionary.
    """
    return {
        "type": "object",
        "properties": {
            "risk_score": {
                "type": "integer",
                "description": "Overall contract risk score from 0 (very safe) to 100 (extremely risky/onerous)."
            },
            "risk_level": {
                "type": "string",
                "enum": ["Low", "Medium", "High"],
                "description": "Risk classification based on the score (0-35 Low, 36-70 Medium, 71-100 High)."
            },
            "score_rationale": {
                "type": "string",
                "description": "Concise summary explaining why this score was assigned."
            },
            "inconsistencies": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string", "description": "Nature of contradiction or conflicting terms."},
                        "conflicting_sections": {"type": "string", "description": "Sections or clauses in conflict."},
                        "severity": {"type": "string", "enum": ["Low", "Medium", "High"]}
                    },
                    "required": ["description", "conflicting_sections", "severity"]
                },
                "description": "List of internal contradictions, conflicting notice windows, mismatched caps, or ambiguous definitions."
            },
            "clauses": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Descriptive title of the clause."},
                        "category": {
                            "type": "string",
                            "enum": ["Payment", "Termination", "Liability", "Privacy", "Penalty", "Renewal", "Other"],
                            "description": "Clause category."
                        },
                        "risk_level": {
                            "type": "string",
                            "enum": ["Low", "Medium", "High"],
                            "description": "Risk level of this specific clause."
                        },
                        "risk_explanation": {
                            "type": "string",
                            "description": "Explanation of the risk or asymmetry in plain English."
                        },
                        "quote": {
                            "type": "string",
                            "description": "VERBATIM quote extracted word-for-word directly from the source document."
                        },
                        "counter_proposal": {
                            "type": "string",
                            "description": "Suggested balanced counter-clause or negotiation wording."
                        }
                    },
                    "required": ["title", "category", "risk_level", "risk_explanation", "quote", "counter_proposal"]
                },
                "description": "Key clauses audited from the document."
            }
        },
        "required": ["risk_score", "risk_level", "score_rationale", "inconsistencies", "clauses"]
    }


def build_risk_prompt(document_text: str) -> Tuple[str, str]:
    """Construct system instruction and prompt for contract risk and inconsistency audit.

    Args:
        document_text: Sanitized plaintext of the legal document.

    Returns:
        Tuple of (system_instruction, user_prompt).
    """
    system_instruction = (
        "You are LexiGuard's senior commercial contract risk auditor. "
        "Your mission is to perform an objective, rigorous risk assessment of the provided legal document.\n"
        "Crucial Rules:\n"
        "1. Identify any internal contradictions, contradictory terms, or conflicting timelines within the document.\n"
        "2. Break down clauses into: Payment, Termination, Liability, Privacy, Penalty, Renewal, or Other.\n"
        "3. For every clause extracted, the 'quote' field MUST BE VERBATIM — copied word-for-word exactly from the document "
        "without paraphrasing or ellipsis, as it will undergo automated cryptographic quote verification.\n"
        "4. Assign an overall risk score from 0 (very benign) to 100 (predatory / highly one-sided).\n"
        "5. Return strictly valid JSON conforming to the schema."
    )

    compacted = compact_text(document_text)
    wrapped_doc = wrap_delimiters(compacted, tag="document_content")

    user_prompt = (
        f"Perform an exhaustive risk and clause breakdown on the legal agreement in <document_content>.\n\n"
        f"{wrapped_doc}\n\n"
        f"Ensure all quotes are exact verbatim matches from the text. Return only valid JSON matching the schema."
    )

    return system_instruction, user_prompt
