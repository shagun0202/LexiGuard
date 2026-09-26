"""Service for pre-signing action plan, deadline extraction, and legal counsel preparation."""

from typing import Any, Dict

from prompts.action import build_action_prompt, get_action_schema
from services.gemini_client import gemini_client


def generate_action_plan(document_text: str) -> Dict[str, Any]:
    """Generate pre-signing checklist, obligations milestones, and lawyer questions.

    Args:
        document_text: Plaintext content of the contract.

    Returns:
        Dictionary with checklist, deadlines, and lawyer_questions.

    Raises:
        ValueError: If document_text is empty.
    """
    if not document_text or not document_text.strip():
        raise ValueError("Cannot generate action plan for an empty document.")

    system_instruction, user_prompt = build_action_prompt(document_text)
    schema = get_action_schema()

    result = gemini_client.generate_json(
        system_instruction=system_instruction,
        prompt=user_prompt,
        schema=schema,
        task="light",
        task_fallback_name="action",
    )

    return result
