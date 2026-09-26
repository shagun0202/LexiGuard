"""Prompt builder and schema definition for strictly grounded document Q&A."""

from typing import Any, Dict, List, Optional, Tuple

from utils.security import compact_text, sanitize_text, wrap_delimiters


def get_qa_schema() -> Dict[str, Any]:
    """Return JSON schema defining expected structure for grounded Q&A responses.

    Returns:
        JSON Schema dictionary.
    """
    return {
        "type": "object",
        "properties": {
            "answer": {
                "type": "string",
                "description": "Grounded answer strictly based on the text. If the topic is absent, state: 'Not specified in document.'"
            },
            "supporting_quotes": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Verbatim quote(s) from the document substantiating this answer. Empty if topic is absent."
            },
            "needs_lawyer": {
                "type": "boolean",
                "description": "True if the question touches on complex litigation, uncapped liability, non-compete enforceability, or high-risk legal decisions requiring licensed legal counsel."
            },
            "lawyer_rationale": {
                "type": "string",
                "description": "Explanation of why consulting a licensed attorney is recommended for this specific question (if needs_lawyer is true)."
            }
        },
        "required": ["answer", "supporting_quotes", "needs_lawyer"]
    }


def build_qa_prompt(
    document_text: str,
    question: str,
    chat_history: Optional[List[Dict[str, str]]] = None
) -> Tuple[str, str]:
    """Construct system instruction and prompt for grounded Q&A.

    Args:
        document_text: Sanitized plaintext of the legal document.
        question: User's question string.
        chat_history: Optional list of past chat messages [{"role": "user"|"assistant", "content": "..."}].

    Returns:
        Tuple of (system_instruction, user_prompt).
    """
    system_instruction = (
        "You are LexiGuard's interactive legal document interrogation assistant. "
        "Your responses must be STRICTLY GROUNDED in the provided document.\n"
        "Guidelines:\n"
        "1. Never fabricate, assume, or hallucinate terms not present in the document.\n"
        "2. If the user's question cannot be answered from the document, your answer MUST explicitly state: "
        "'Not specified in document.' and supporting_quotes must be empty.\n"
        "3. Provide verbatim supporting quotes whenever an answer is found in the text.\n"
        "4. Set 'needs_lawyer': true if the question requires statutory interpretation, litigation strategy, "
        "assessing non-compete enforceability, or advice on whether to sign.\n"
        "5. Return strictly valid JSON adhering to the schema."
    )

    compacted = compact_text(document_text)
    sanitized_q = sanitize_text(question, max_chars=1_000)

    history_str = ""
    if chat_history:
        recent = chat_history[-4:]  # Last 2 turns for context
        formatted_history = []
        for msg in recent:
            role = msg.get("role", "user")
            content = sanitize_text(msg.get("content", ""), max_chars=500)
            formatted_history.append(f"{role.upper()}: {content}")
        history_str = "Recent Conversation History:\n" + "\n".join(formatted_history) + "\n\n"

    wrapped_doc = wrap_delimiters(compacted, tag="document_content")
    wrapped_query = wrap_delimiters(sanitized_q, tag="user_query")

    user_prompt = (
        f"{history_str}"
        f"Document Content:\n{wrapped_doc}\n\n"
        f"User Inquiry:\n{wrapped_query}\n\n"
        f"Answer the user inquiry based strictly on the document content. Return only valid JSON matching the schema."
    )

    return system_instruction, user_prompt
