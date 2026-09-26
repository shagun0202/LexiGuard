"""Unit tests for simplify_service."""

import pytest

from services.simplify_service import simplify_document


def test_simplify_empty_document_raises_value_error():
    """Verify empty document triggers ValueError."""
    with pytest.raises(ValueError):
        simplify_document("")


def test_simplify_whitespace_only_raises_value_error():
    """Verify whitespace-only document triggers ValueError."""
    with pytest.raises(ValueError):
        simplify_document("    \n\n  ")


def test_simplify_sample_nda(sample_nda_text: str):
    """Verify simplify_document returns required schema fields."""
    res = simplify_document(sample_nda_text, reading_level="standard", language="english")
    assert isinstance(res, dict)
    assert "summary" in res
    assert "key_points" in res
    assert "glossary" in res
    assert len(res["summary"]) > 20
    assert isinstance(res["key_points"], list)
    assert isinstance(res["glossary"], list)


def test_simplify_eli15_reading_level(sample_nda_text: str):
    """Verify ELI15 reading level produces valid response."""
    res = simplify_document(sample_nda_text, reading_level="eli15", language="english")
    assert "summary" in res
    assert isinstance(res["key_points"], list)


def test_simplify_multilingual_hindi(sample_nda_text: str):
    """Verify hindi language parameter execution."""
    res = simplify_document(sample_nda_text, reading_level="standard", language="hindi")
    assert "summary" in res
