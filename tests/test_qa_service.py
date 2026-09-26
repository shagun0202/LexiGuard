"""Unit tests for grounded interactive Q&A service."""

import pytest

from services.qa_service import answer_document_query


def test_qa_empty_doc_raises_value_error():
    """Verify empty document triggers ValueError."""
    with pytest.raises(ValueError):
        answer_document_query("", "What is the term?")


def test_qa_empty_question_raises_value_error(sample_nda_text: str):
    """Verify empty question triggers ValueError."""
    with pytest.raises(ValueError):
        answer_document_query(sample_nda_text, "   ")


def test_qa_grounded_response_structure(sample_nda_text: str):
    """Verify answer_document_query returns answer and verified quotes."""
    res = answer_document_query(sample_nda_text, "What is the duration of the agreement?")
    assert "answer" in res
    assert isinstance(res["answer"], str)
    assert len(res["answer"]) > 5
    assert "supporting_quotes" in res
    assert "needs_lawyer" in res
    assert "verified_quotes" in res
    assert isinstance(res["verified_quotes"], list)


def test_qa_with_chat_history(sample_nda_text: str):
    """Verify conversational Q&A handles chat history context."""
    history = [
        {"role": "user", "content": "Who are the parties?"},
        {"role": "assistant", "content": "Apex Innovations and Horizon Analytics."},
    ]
    res = answer_document_query(sample_nda_text, "Which party is located in San Francisco?", chat_history=history)
    assert "answer" in res
