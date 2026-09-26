"""Service for strictly grounded interactive Q&A interrogation."""

from typing import Any, Dict, List, Optional

from prompts.qa import build_qa_prompt, get_qa_schema
from services.gemini_client import gemini_client
from services.risk_service import verify_quote_authenticity


def answer_document_query(
    document_text: str,
    question: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """Execute grounded question answering against a specific document.

    Args:
        document_text: Plaintext content of the contract.
        question: User query string.
        chat_history: Optional chat history messages.

    Returns:
        Dictionary with:
            - answer (str): Grounded answer or 'Not specified in document.'
            - supporting_quotes (List[str]): List of verbatim quotes.
            - needs_lawyer (bool): Flag indicating if counsel is recommended.
            - lawyer_rationale (str): Reason why counsel consultation is advised.
            - verified_quotes (List[Dict[str, Any]]): Verification stats for quotes.

    Raises:
        ValueError: If document_text or question is empty.
    """
    if not document_text or not document_text.strip():
        raise ValueError("Cannot query an empty document.")
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    system_instruction, user_prompt = build_qa_prompt(
        document_text=document_text,
        question=question,
        chat_history=chat_history,
    )
    schema = get_qa_schema()

    result = gemini_client.generate_json(
        system_instruction=system_instruction,
        prompt=user_prompt,
        schema=schema,
        task="light",
        task_fallback_name="qa",
    )

    # Verify supporting quotes authenticity
    quotes = result.get("supporting_quotes", [])
    verified_quotes = []
    for q in quotes:
        ver = verify_quote_authenticity(q, document_text)
        verified_quotes.append({"quote": q, "verification": ver})

    result["verified_quotes"] = verified_quotes
    return result
