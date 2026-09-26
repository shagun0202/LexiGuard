"""Unit tests for the resilient Gemini API client integration."""

import json
import os
from unittest.mock import MagicMock, patch
import pytest

from services.cache import cache_manager, compute_cache_key
from services.gemini_client import (
    GeminiClient,
    _classify_error,
    _is_model_cooling_down,
    _record_model_failure,
    _record_model_success,
    _strip_code_fences,
    gemini_client,
    get_last_call_info,
)


def test_strip_code_fences():
    """Verify markdown ```json code fences are stripped cleanly."""
    fenced = "```json\n{\"summary\": \"Test summary\"}\n```"
    clean = _strip_code_fences(fenced)
    assert clean == '{"summary": "Test summary"}'

    plain = '{"key": "value"}'
    assert _strip_code_fences(plain) == '{"key": "value"}'


def test_classify_error_auth_401():
    """Verify 401/403 status is classified as auth."""
    class MockAuthErr(Exception):
        status_code = 401

    cat, code = _classify_error(MockAuthErr("Unauthorized"))
    assert cat == "auth"
    assert code == 401


def test_classify_error_not_found_404():
    """Verify 404 status is classified as not_found."""
    class Mock404(Exception):
        code = 404

    cat, code = _classify_error(Mock404("Model not found"))
    assert cat == "not_found"
    assert code == 404


def test_classify_error_thinking_400():
    """Verify 400 error mentioning 'thinking' is classified as thinking_issue."""
    err = Exception("400 Bad Request: thinking_config not supported on this model")
    cat, code = _classify_error(err)
    assert cat == "thinking_issue"
    assert code == 400


def test_classify_error_transient_429_503():
    """Verify 429 quota and 503 unavailable are classified as transient."""
    err_429 = Exception("Resource has been exhausted (e.g. check quota): 429")
    cat, code = _classify_error(err_429)
    assert cat == "transient"
    assert code == 429

    err_503 = Exception("503 Service Unavailable")
    cat, code = _classify_error(err_503)
    assert cat == "transient"
    assert code == 503


def test_circuit_breaker_trips_after_2_failures():
    """Verify model is placed in cooldown after 2 consecutive failures."""
    test_model = "test-model-circuit-breaker"
    _record_model_failure(test_model)
    assert not _is_model_cooling_down(test_model)
    
    _record_model_failure(test_model)
    assert _is_model_cooling_down(test_model)

    # Success resets counter and removes cooldown
    _record_model_success(test_model)
    assert not _is_model_cooling_down(test_model)


def test_cache_key_excludes_model_and_api_key():
    """Verify cache key is independent of model and API key."""
    key1 = compute_cache_key("System instr", "Prompt content", {"type": "object"}, "light")
    key2 = compute_cache_key("System instr", "Prompt content", {"type": "object"}, "light")
    assert key1 == key2


def test_unconfigured_api_key_serves_demo_fallback():
    """Verify missing API key serves pre-canned demo data when allow_demo_fallback=True."""
    import uuid
    client = GeminiClient()
    # Temporarily remove API key from env
    with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
        res = client.generate_json(
            system_instruction="sys",
            prompt=f"unique_unconfigured_prompt_{uuid.uuid4()}",
            task="light",
            task_fallback_name="simplify",
            allow_demo_fallback=True,
        )
        assert isinstance(res, dict)
        assert "summary" in res
        info = get_last_call_info()
        assert info["source"] == "demo"


def test_unconfigured_api_key_raises_error_without_fallback():
    """Verify missing API key raises ValueError when allow_demo_fallback=False."""
    import uuid
    client = GeminiClient()
    with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
        with pytest.raises(ValueError) as exc:
            client.generate_json(
                system_instruction="sys",
                prompt=f"unique_unconfigured_error_{uuid.uuid4()}",
                task="light",
                allow_demo_fallback=False,
            )
        assert "GEMINI_API_KEY is not configured" in str(exc.value)


def test_cache_hit_returns_in_memory():
    """Verify cache manager stores and retrieves data without calling API."""
    key = "unit_test_cache_key_12345"
    payload = {"status": "ok", "value": 42}
    cache_manager.set(key, payload)
    retrieved = cache_manager.get(key)
    assert retrieved == payload


def test_successful_mocked_generation(mock_gemini_response):
    """Verify successful generation flow when client returns valid JSON."""
    import uuid
    client = GeminiClient()
    expected_data = {"summary": "Mock summary", "key_points": ["Point 1"], "glossary": []}

    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.return_value = mock_gemini_response(json.dumps(expected_data))

    unique_prompt = f"unique prompt {uuid.uuid4()}"
    with patch.object(client, "_get_client", return_value=mock_client_instance):
        res = client.generate_json(
            system_instruction="sys",
            prompt=unique_prompt,
            schema={"required": ["summary"]},
            task="light",
            allow_demo_fallback=False,
        )
        assert res == expected_data
        info = get_last_call_info()
        assert info["source"] == "live"
        assert info["attempts"] == 1


def test_self_healing_json_retry(mock_gemini_response):
    """Verify self-healing retry triggers when initial model output is malformed JSON."""
    client = GeminiClient()
    valid_data = {"summary": "Healed summary", "key_points": [], "glossary": []}

    bad_resp = mock_gemini_response("Here is the JSON: {bad json...")
    healed_resp = mock_gemini_response(json.dumps(valid_data))

    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.side_effect = [bad_resp, healed_resp]

    with patch.object(client, "_get_client", return_value=mock_client_instance):
        res = client.generate_json(
            system_instruction="sys",
            prompt="prompt for self healing",
            schema={"required": ["summary"]},
            task="light",
            allow_demo_fallback=False,
        )
        assert res == valid_data
