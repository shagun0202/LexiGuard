"""Unit tests for dual contract comparison service."""

import pytest

from services.compare_service import compare_documents


def test_compare_empty_doc_a_raises(sample_employment_text: str):
    """Verify empty Document A triggers ValueError."""
    with pytest.raises(ValueError):
        compare_documents("", sample_employment_text)


def test_compare_empty_doc_b_raises(sample_nda_text: str):
    """Verify empty Document B triggers ValueError."""
    with pytest.raises(ValueError):
        compare_documents(sample_nda_text, "")


def test_compare_documents_structure(sample_nda_text: str, sample_employment_text: str):
    """Verify compare_documents returns expected comparison schema."""
    res = compare_documents(sample_nda_text, sample_employment_text)
    assert "overall_comparison" in res
    assert "favorability" in res
    assert res["favorability"] in ("Document A", "Document B", "Neither / Balanced")
    assert "differences" in res
    assert isinstance(res["differences"], list)
    assert "missing_in_doc_a" in res
    assert "missing_in_doc_b" in res
    assert isinstance(res["missing_in_doc_a"], list)
    assert isinstance(res["missing_in_doc_b"], list)
