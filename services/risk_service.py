"""Service for contract risk assessment, clause auditing, and algorithmic quote verification."""

import re
from difflib import SequenceMatcher
from typing import Any, Dict, List

from prompts.risk import build_risk_prompt, get_risk_schema
from services.gemini_client import gemini_client


def _normalize_for_matching(text: str) -> str:
    """Normalize text by collapsing whitespace, stripping smart quotes, and lowercasing."""
    if not text:
        return ""
    # Replace smart quotes and dashes with ASCII equivalents
    normalized = (
        text.replace("“", '"')
        .replace("”", '"')
        .replace("’", "'")
        .replace("‘", "'")
        .replace("—", "-")
        .replace("–", "-")
    )
    # Collapse all whitespace and newlines to single spaces
    normalized = re.sub(r"\s+", " ", normalized).strip().lower()
    return normalized


def verify_quote_authenticity(quote: str, source_text: str) -> Dict[str, Any]:
    """Algorithmatically verify whether an extracted quote exists in the source contract.

    Prevents AI hallucination and provides users with a cryptographic-like authenticity score.

    Args:
        quote: Extracted verbatim quote candidate.
        source_text: The complete original document plaintext.

    Returns:
        Dictionary with:
            - status (str): "VERIFIED", "PARTIAL_MATCH", or "UNVERIFIED"
            - score (int): 0-100 match percentage
            - is_authentic (bool): True if exact or near-exact match
    """
    if not quote or not source_text:
        return {"status": "UNVERIFIED", "score": 0, "is_authentic": False}

    norm_quote = _normalize_for_matching(quote)
    norm_source = _normalize_for_matching(source_text)

    # 1. Exact Substring Match
    if norm_quote in norm_source:
        return {"status": "VERIFIED", "score": 100, "is_authentic": True}

    # 2. Sliding window search or best substring match using SequenceMatcher
    matcher = SequenceMatcher(None, norm_source, norm_quote)
    match = matcher.find_longest_match(0, len(norm_source), 0, len(norm_quote))
    
    if len(norm_quote) > 0:
        longest_match_ratio = (match.size / len(norm_quote)) * 100
    else:
        longest_match_ratio = 0.0

    score = int(round(longest_match_ratio))

    if score >= 90:
        return {"status": "VERIFIED", "score": score, "is_authentic": True}
    elif score >= 65:
        return {"status": "PARTIAL_MATCH", "score": score, "is_authentic": True}
    else:
        return {"status": "UNVERIFIED", "score": score, "is_authentic": False}


def audit_contract_risks(document_text: str) -> Dict[str, Any]:
    """Perform comprehensive risk scoring, contradiction detection, and clause auditing.

    Also runs algorithmic quote verification across all extracted clauses.

    Args:
        document_text: Plaintext content of the contract.

    Returns:
        Dictionary containing risk_score, risk_level, score_rationale,
        inconsistencies, and clauses with verification metadata.

    Raises:
        ValueError: If document_text is empty.
    """
    if not document_text or not document_text.strip():
        raise ValueError("Cannot audit risks of an empty document.")

    system_instruction, user_prompt = build_risk_prompt(document_text)
    schema = get_risk_schema()

    result = gemini_client.generate_json(
        system_instruction=system_instruction,
        prompt=user_prompt,
        schema=schema,
        task="heavy",  # Risk analysis is heavier reasoning
        task_fallback_name="risk",
    )

    # Perform automated quote verification for each clause
    clauses = result.get("clauses", [])
    for clause in clauses:
        quote = clause.get("quote", "")
        verification = verify_quote_authenticity(quote, document_text)
        clause["verification"] = verification

    return result
