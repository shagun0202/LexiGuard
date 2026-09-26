"""Common pytest fixtures, mock helpers, and sample contracts for LexiGuard test suite."""

import os
from pathlib import Path
from typing import Any, Dict

import pytest

# Ensure .cache and logs exist
Path(".cache").mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)


@pytest.fixture
def sample_nda_text() -> str:
    """Return realistic sample Mutual NDA plaintext."""
    path = Path("demo_data/sample_nda.txt")
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return (
        "MUTUAL NON-DISCLOSURE AGREEMENT\n\n"
        "This Agreement is between Apex Innovations and Horizon Analytics.\n"
        "1. Confidential Information shall be protected for 5 years.\n"
        "2. Governing law is California. All disputes submitted to AAA arbitration."
    )


@pytest.fixture
def sample_employment_text() -> str:
    """Return realistic sample Employment Agreement plaintext."""
    path = Path("demo_data/sample_employment.txt")
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return (
        "EXECUTIVE EMPLOYMENT AGREEMENT\n\n"
        "Zenith Cloud Technologies employs David Vance.\n"
        "1. Compensation: Base salary $240,000.\n"
        "2. Non-Compete for 12 months following termination."
    )


@pytest.fixture
def non_legal_text() -> str:
    """Return grocery / non-contract text for legal density testing."""
    return "Grocery list: apples, bananas, milk, eggs, whole wheat bread, cheese, butter, and coffee beans."


@pytest.fixture
def mock_gemini_response():
    """Helper factory to produce a mock Gemini API GenerateContentResponse object."""
    def _create_mock(text_content: str):
        class MockResp:
            def __init__(self, text: str):
                self.text = text
        return MockResp(text_content)
    return _create_mock
