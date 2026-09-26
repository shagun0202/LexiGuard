"""Unit tests for risk assessment service and algorithmic quote verification."""

import pytest

from services.risk_service import audit_contract_risks, verify_quote_authenticity


def test_verify_quote_authenticity_exact_match():
    """Verify exact verbatim quote gets VERIFIED status and 100% score."""
    source = (
        "7. NO WARRANTY. ALL CONFIDENTIAL INFORMATION IS PROVIDED 'AS IS' WITHOUT WARRANTY OF ANY KIND."
    )
    quote = "ALL CONFIDENTIAL INFORMATION IS PROVIDED 'AS IS' WITHOUT WARRANTY OF ANY KIND."
    ver = verify_quote_authenticity(quote, source)
    assert ver["status"] == "VERIFIED"
    assert ver["score"] == 100
    assert ver["is_authentic"] is True


def test_verify_quote_authenticity_smart_quotes_normalization():
    """Verify smart quotes and slight punctuation differences normalize cleanly."""
    source = 'Disclosing Party shall be entitled to seek "equitable relief" without posting a bond.'
    quote = 'Disclosing Party shall be entitled to seek “equitable relief” without posting a bond.'
    ver = verify_quote_authenticity(quote, source)
    assert ver["status"] == "VERIFIED"
    assert ver["score"] == 100


def test_verify_quote_authenticity_partial_match():
    """Verify quote with minor omissions produces PARTIAL_MATCH."""
    source = (
        "Any dispute arising out of or related to this Agreement shall be submitted to binding arbitration in San Francisco, California."
    )
    quote = "dispute arising out of this Agreement shall be submitted to binding arbitration in San Francisco"
    ver = verify_quote_authenticity(quote, source)
    assert ver["status"] in ("VERIFIED", "PARTIAL_MATCH")
    assert ver["score"] >= 65


def test_verify_quote_authenticity_hallucinated_unverified():
    """Verify completely hallucinated or nonexistent quote is marked UNVERIFIED."""
    source = "This contract is governed by California law."
    hallucinated_quote = "The parties agree to pay liquidated damages of ten million dollars upon any breach."
    ver = verify_quote_authenticity(hallucinated_quote, source)
    assert ver["status"] == "UNVERIFIED"
    assert ver["score"] < 65
    assert ver["is_authentic"] is False


def test_verify_quote_authenticity_empty_strings():
    """Verify empty quote or source text returns unverified."""
    assert verify_quote_authenticity("", "some source")["status"] == "UNVERIFIED"
    assert verify_quote_authenticity("some quote", "")["status"] == "UNVERIFIED"


def test_audit_contract_risks_empty_raises():
    """Verify empty document triggers ValueError."""
    with pytest.raises(ValueError):
        audit_contract_risks("")


def test_audit_contract_risks_schema_validation(sample_nda_text: str):
    """Verify audit_contract_risks returns risk_score, risk_level, and verified clauses."""
    res = audit_contract_risks(sample_nda_text)
    assert "risk_score" in res
    assert 0 <= res["risk_score"] <= 100
    assert res["risk_level"] in ("Low", "Medium", "High")
    assert "score_rationale" in res
    assert "clauses" in res
    assert isinstance(res["clauses"], list)

    for clause in res["clauses"]:
        assert "verification" in clause
        assert clause["verification"]["status"] in ("VERIFIED", "PARTIAL_MATCH", "UNVERIFIED")
