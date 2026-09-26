"""Unit tests for heuristic legal terminology density checker."""

import pytest

from utils.legal_checker import check_legal_density


def test_high_legal_density_contract(sample_nda_text: str):
    """Verify high legal density score on realistic NDA."""
    res = check_legal_density(sample_nda_text)
    assert res["score"] >= 50
    assert res["is_legal_document"] is True
    assert res["term_count"] >= 5
    assert any("confidential" in term for term in res["matched_terms"])
    assert "High legal density" in res["message"] or "Moderate" in res["message"]


def test_moderate_legal_density_agreement(sample_employment_text: str):
    """Verify legal terms detected in employment contract."""
    res = check_legal_density(sample_employment_text)
    assert res["score"] >= 25
    assert res["is_legal_document"] is True
    assert res["term_count"] >= 3


def test_low_legal_density_grocery_list(non_legal_text: str):
    """Verify non-legal text gets low score and false flag."""
    res = check_legal_density(non_legal_text)
    assert res["score"] < 25
    assert res["is_legal_document"] is False
    assert "Low legal density" in res["message"]


def test_empty_document_legal_check():
    """Verify empty text handling."""
    res = check_legal_density("   ")
    assert res["score"] == 0
    assert res["is_legal_document"] is False
    assert res["term_count"] == 0


def test_legal_checker_type_error():
    """Verify TypeError on non-str input."""
    with pytest.raises(TypeError):
        check_legal_density(None)  # type: ignore
