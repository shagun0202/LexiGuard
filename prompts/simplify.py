"""Prompt builder and schema definition for document simplification."""

from typing import Any, Dict, List, Tuple

from utils.security import compact_text, wrap_delimiters


def get_simplify_schema() -> Dict[str, Any]:
    """Return JSON schema defining expected structure for document simplification.

    Returns:
        JSON Schema dictionary.
    """
    return {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "A single comprehensive paragraph executive summary in plain, everyday language."
            },
            "key_points": {
                "type": "array",
                "items": {"type": "string"},
                "description": "5-8 bullet points highlighting crucial rights, commercial terms, and key obligations."
            },
            "glossary": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "term": {"type": "string", "description": "Legal or Latin term found in the text."},
                        "definition": {"type": "string", "description": "Clear plain English explanation."},
                        "context": {"type": "string", "description": "How the term is used in this agreement."}
                    },
                    "required": ["term", "definition", "context"]
                },
                "description": "List of difficult legal terms, Latin jargon, or formal definitions translated to plain language."
            }
        },
        "required": ["summary", "key_points", "glossary"]
    }


def build_simplify_prompt(
    document_text: str,
    reading_level: str = "standard",
    language: str = "english"
) -> Tuple[str, str]:
    """Construct system instruction and prompt for legal simplification.

    Args:
        document_text: Sanitized plaintext of the legal document.
        reading_level: "standard" (plain professional) or "eli15" (simplified for a 15-year-old).
        language: "english", "hindi", or "kannada".

    Returns:
        Tuple of (system_instruction, user_prompt).
    """
    level_instruction = (
        "Use simple, conversational language suitable for a high-school student (Explain Like I'm 15). "
        "Avoid any formal legalistic jargon."
        if reading_level.lower() == "eli15"
        else "Use clear, concise, professional plain-English accessible to any business executive or individual without legal training."
    )

    lang_instruction = "Respond entirely in English."
    if language.lower() in ("hindi", "hi"):
        lang_instruction = "Respond entirely in Hindi (हिंदी script) with accurate translation of concepts."
    elif language.lower() in ("kannada", "kn"):
        lang_instruction = "Respond entirely in Kannada (ಕನ್ನಡ script) with accurate translation of concepts."

    system_instruction = (
        "You are LexiGuard's expert legal document simplification assistant. "
        "Your role is educational: transform dense, impenetrable contract language into crystal-clear, "
        "transparent explanations without offering formal legal advice.\n"
        f"Reading Level Directive: {level_instruction}\n"
        f"Language Directive: {lang_instruction}\n"
        "Return strictly valid JSON matching the schema provided."
    )

    compacted = compact_text(document_text)
    wrapped_doc = wrap_delimiters(compacted, tag="document_content")

    user_prompt = (
        f"Analyze the following legal document enclosed in <document_content>.\n\n"
        f"{wrapped_doc}\n\n"
        f"Generate:\n"
        f"1. A clear one-paragraph executive summary.\n"
        f"2. 5 to 8 bullet points capturing critical business and legal takeaways.\n"
        f"3. A jargon glossary defining all key Latin, archaic, or complex legal terms used in this document.\n\n"
        f"Output MUST be valid JSON adhering strictly to the schema."
    )

    return system_instruction, user_prompt
