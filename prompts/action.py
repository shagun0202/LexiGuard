"""Prompt builder and schema definition for pre-signing action plan and legal consultation guide."""

from typing import Any, Dict, Tuple

from utils.security import compact_text, wrap_delimiters


def get_action_schema() -> Dict[str, Any]:
    """Return JSON schema defining expected structure for action plan generation.

    Returns:
        JSON Schema dictionary.
    """
    return {
        "type": "object",
        "properties": {
            "checklist": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "task": {"type": "string", "description": "Specific action item before signing."},
                        "category": {"type": "string", "description": "e.g. Due Diligence, Financial, Legal, Operational."},
                        "completed": {"type": "boolean", "description": "Initial state, always false."}
                    },
                    "required": ["task", "category", "completed"]
                },
                "description": "Interactive pre-execution checklist."
            },
            "deadlines": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "task": {"type": "string", "description": "Contractual obligation or milestone."},
                        "responsible_party": {"type": "string", "description": "Who must perform this action."},
                        "deadline": {"type": "string", "description": "Timeline, window, or date (e.g. 30 days prior to renewal)."}
                    },
                    "required": ["task", "responsible_party", "deadline"]
                },
                "description": "Crucial deadlines, notice windows, and milestone obligations."
            },
            "lawyer_questions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "8 to 10 specific, targeted questions to ask qualified legal counsel regarding this agreement."
            }
        },
        "required": ["checklist", "deadlines", "lawyer_questions"]
    }


def build_action_prompt(document_text: str) -> Tuple[str, str]:
    """Construct system instruction and prompt for creating the action plan.

    Args:
        document_text: Sanitized plaintext of the legal document.

    Returns:
        Tuple of (system_instruction, user_prompt).
    """
    system_instruction = (
        "You are LexiGuard's tactical contract execution and counsel prep assistant. "
        "Your role is to formulate practical next steps for a party considering signing this agreement:\n"
        "1. Create a 6-10 item pre-signing checklist of critical verifications.\n"
        "2. Extract all calendar milestones, notice periods, payment deadlines, and renewal timelines.\n"
        "3. Provide exactly 8 to 10 targeted, sophisticated questions for the user to ask an attorney.\n"
        "Return strictly valid JSON adhering to the schema."
    )

    compacted = compact_text(document_text)
    wrapped_doc = wrap_delimiters(compacted, tag="document_content")

    user_prompt = (
        f"Generate a comprehensive pre-signing action plan for the contract in <document_content>.\n\n"
        f"{wrapped_doc}\n\n"
        f"Provide the checklist, obligations and deadlines table, and 8 to 10 sharp attorney questions. "
        f"Return only valid JSON matching the schema."
    )

    return system_instruction, user_prompt
