"""Heuristic analyzer for detecting legal document terminology and domain density.

Evaluates whether uploaded text constitutes a formal legal contract or agreement,
providing early feedback to users if an uploaded file is not legal in nature.
"""

import re
from typing import Dict, Final, List, Tuple

# Weighted legal terminology terms and phrases
_LEGAL_PATTERNS: Final[Dict[str, int]] = {
    r"\bindemnif(?:y|ication|ied)\b": 4,
    r"\bhold\s+harmless\b": 3,
    r"\bgoverning\s+law\b": 4,
    r"\bjurisdiction\b": 3,
    r"\bseverability\b": 4,
    r"\bforce\s+majeure\b": 5,
    r"\bconfidential(?:ity)?\b": 3,
    r"\bnon-disclosure\b": 4,
    r"\bproprietary\s+information\b": 3,
    r"\btermination\b": 2,
    r"\bbreach(?:\s+of\s+contract)?\b": 3,
    r"\blimitation\s+of\s+liability\b": 4,
    r"\bconsequential\s+damages\b": 4,
    r"\bintellectual\s+property\b": 3,
    r"\bwarrant(?:y|ies|ed)?\b": 2,
    r"\brepresentations?\b": 2,
    r"\bwhereas\b": 3,
    r"\bherein(?:after|before|to|of)?\b": 2,
    r"\bin\s+witness\s+whereof\b": 4,
    r"\bentire\s+agreement\b": 3,
    r"\barbitration\b": 3,
    r"\bcovenant\b": 3,
    r"\bparties?\s+hereto\b": 3,
    r"\bliquidated\s+damages\b": 4,
}

_COMPILED_PATTERNS: Final[List[Tuple[re.Pattern[str], str, int]]] = [
    (re.compile(pattern, re.IGNORECASE), pattern.replace(r"\b", "").replace(r"\s+", " "), weight)
    for pattern, weight in _LEGAL_PATTERNS.items()
]


def check_legal_density(text: str) -> Dict[str, object]:
    """Analyze text for presence and density of legal concepts and terminology.

    Args:
        text: Plaintext content of the document.

    Returns:
        Dictionary containing:
            - score (int): 0-100 legal confidence score.
            - is_legal_document (bool): True if confidence >= 25.
            - term_count (int): Total unique legal terms found.
            - matched_terms (List[str]): List of friendly names of matched terms.
            - message (str): Human-friendly assessment of the document.

    Raises:
        TypeError: If text is not an instance of str.
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str input, got {type(text).__name__}")

    if not text.strip():
        return {
            "score": 0,
            "is_legal_document": False,
            "term_count": 0,
            "matched_terms": [],
            "message": "Empty document. Please upload a document with text content.",
        }

    matched_terms: List[str] = []
    total_weight = 0

    for regex, display_name, weight in _COMPILED_PATTERNS:
        match = regex.search(text)
        if match:
            matched_terms.append(display_name)
            total_weight += weight

    # Normalize score out of 100 based on expected threshold for standard contracts
    # A standard contract typically hits 6-12 terms with weights summing to 25-45.
    raw_score = int(min(100, (total_weight / 35.0) * 100))

    if raw_score >= 60:
        message = "High legal density: Strong contractual and legal terminology detected."
        is_legal = True
    elif raw_score >= 25:
        message = "Moderate legal density: Standard legal and contractual terms detected."
        is_legal = True
    else:
        message = (
            "Low legal density: Few or no standard legal clauses detected. "
            "Please ensure this is a contract, agreement, policy, or legal document."
        )
        is_legal = False

    return {
        "score": raw_score,
        "is_legal_document": is_legal,
        "term_count": len(matched_terms),
        "matched_terms": matched_terms,
        "message": message,
    }
