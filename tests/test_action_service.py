"""Unit tests for action plan and counsel preparation service."""

import pytest

from services.action_service import generate_action_plan


def test_action_empty_doc_raises():
    """Verify empty document triggers ValueError."""
    with pytest.raises(ValueError):
        generate_action_plan("")


def test_action_plan_structure(sample_nda_text: str):
    """Verify action plan returns checklist, deadlines, and attorney questions."""
    res = generate_action_plan(sample_nda_text)
    assert "checklist" in res
    assert "deadlines" in res
    assert "lawyer_questions" in res

    assert isinstance(res["checklist"], list)
    assert len(res["checklist"]) >= 3

    assert isinstance(res["deadlines"], list)
    assert len(res["deadlines"]) >= 2

    assert isinstance(res["lawyer_questions"], list)
    assert len(res["lawyer_questions"]) >= 5
