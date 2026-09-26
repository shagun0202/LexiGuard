"""Enterprise Gemini API Integration Client for LexiGuard.

Implements the 6 Architectural Pillars:
1. Core Rules & Security:
   - Zero key or prompt leakage.
   - Lazy client initialization; raises friendly ValueError on missing key.
   - Disables internal SDK retries (HttpRetryOptions(attempts=1)).
   - Enforces strict timeout via HttpOptions(timeout=...).
2. Multi-Model Fallback Chains (Tiered Routing):
   - task="light" | "heavy" routing with configurable model chains from .env.
   - Automatic fall-forward to next model on recoverable failures.
3. Intelligent HTTP Error Classification:
   - 401/403: Stop immediately with zero retries.
   - 404: Skip to next model immediately (0ms sleep).
   - 400 with 'thinking': Retry once without thinking_config.
   - Other 400: Stop immediately.
   - 429/5xx/Timeouts: Exponential backoff with jitter up to 2 retries, then fall forward.
   - If all models fail: Friendly RuntimeError detailing all attempt outcomes.
4. Output Validation & Self-Healing JSON:
   - Rejects empty or blocked responses.
   - Strips markdown code fences.
   - Single self-healing retry on parse failure or MAX_TOKENS with temp=0 and schema prompt append.
   - Schema validation for required fields.
5. Speed & Load Protection:
   - Thread-safe rate limiter with GEMINI_MIN_INTERVAL_SECONDS.
   - Circuit breaker: 2 consecutive failures -> 60s cooldown; bypass if all cooled down.
6. Content-Addressable Caching & Offline Fallback:
   - SHA-256(system_instruction + prompt + schema + task) cache check < 5ms.
   - Falls back to .cache/ then demo_data/ if all models fail.
7. Observability & Logging:
   - RotatingFileHandler to logs/calls.log with format:
     <timestamp_iso> | <model> | <task> | <outcome_or_error_code> | <seconds_taken>s
   - get_last_call_info() helper for UI metadata display.
"""

import json
import logging
import os
import random
import re
import threading
import time
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from dotenv import load_dotenv
from google import genai
from google.genai import types

from services.cache import cache_manager, compute_cache_key
from utils.security import mask_sensitive_error

# Load environment configuration
load_dotenv()

# Configuration Knobs & Defaults
GEMINI_TIMEOUT_SECONDS: float = float(os.getenv("GEMINI_TIMEOUT_SECONDS", "35"))
GEMINI_MIN_INTERVAL_SECONDS: float = float(os.getenv("GEMINI_MIN_INTERVAL_SECONDS", "1.0"))

DEFAULT_LIGHT_CHAIN: List[str] = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.6-flash",
    "gemini-flash-lite-latest",
]
DEFAULT_HEAVY_CHAIN: List[str] = [
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-flash-lite-latest",
]


def _parse_model_chain(env_var: str, default_chain: List[str]) -> List[str]:
    """Parse comma-separated model chain from environment variable.

    Args:
        env_var: Environment variable name.
        default_chain: Default list of models.

    Returns:
        List of trimmed model identifier strings.
    """
    raw = os.getenv(env_var, "")
    if not raw.strip():
        return list(default_chain)
    models = [m.strip() for m in raw.split(",") if m.strip()]
    return models if models else list(default_chain)


# Observability Logger Setup
_LOG_DIR = Path("logs")
_LOG_DIR.mkdir(parents=True, exist_ok=True)
_LOG_FILE = _LOG_DIR / "calls.log"

logger = logging.getLogger("lexiguard.client")

_calls_logger = logging.getLogger("lexiguard.calls")
_calls_logger.setLevel(logging.INFO)
if not _calls_logger.handlers:
    _handler = RotatingFileHandler(_LOG_FILE, maxBytes=1024 * 1024, backupCount=3, encoding="utf-8")
    _formatter = logging.Formatter("%(message)s")
    _handler.setFormatter(_formatter)
    _calls_logger.addHandler(_handler)

# Thread-Safe State & Knobs
_RATE_LIMIT_LOCK = threading.Lock()
_LAST_CALL_TIMESTAMP: float = 0.0

_CIRCUIT_LOCK = threading.Lock()
_MODEL_FAILURES: Dict[str, int] = {}
_MODEL_COOLDOWNS: Dict[str, float] = {}  # model -> cooldown expiration epoch

_LAST_CALL_INFO: Dict[str, Any] = {
    "model_used": "none",
    "source": "none",
    "attempts": 0,
    "fell_back": False,
    "seconds": 0.0,
}


def get_last_call_info() -> Dict[str, Any]:
    """Return observability metadata from the most recent API or cache call.

    Returns:
        Dictionary with model_used, source ('live', 'cache', 'demo'), attempts, fell_back, seconds.
    """
    with _RATE_LIMIT_LOCK:
        return dict(_LAST_CALL_INFO)


def _record_call_log(model: str, task: str, outcome: str, duration_sec: float) -> None:
    """Write structured record to logs/calls.log without leaking keys or user content.

    Format: <timestamp_iso> | <model> | <task> | <outcome_or_error_code> | <seconds_taken>s
    """
    iso_ts = datetime.now(timezone.utc).isoformat()
    record = f"{iso_ts} | {model} | {task} | {outcome} | {duration_sec:.2f}s"
    _calls_logger.info(record)


def _enforce_rate_limit() -> None:
    """Enforce minimum interval between API calls to avoid burst QPM throttling."""
    global _LAST_CALL_TIMESTAMP
    with _RATE_LIMIT_LOCK:
        now = time.time()
        elapsed = now - _LAST_CALL_TIMESTAMP
        if elapsed < GEMINI_MIN_INTERVAL_SECONDS:
            sleep_needed = GEMINI_MIN_INTERVAL_SECONDS - elapsed
            time.sleep(sleep_needed)
        _LAST_CALL_TIMESTAMP = time.time()


def _is_model_cooling_down(model: str) -> bool:
    """Check if model is currently placed in cooldown by circuit breaker."""
    with _CIRCUIT_LOCK:
        expiry = _MODEL_COOLDOWNS.get(model, 0.0)
        return time.time() < expiry


def _record_model_failure(model: str) -> None:
    """Increment consecutive model failure count and trip circuit breaker if threshold hit."""
    with _CIRCUIT_LOCK:
        fails = _MODEL_FAILURES.get(model, 0) + 1
        _MODEL_FAILURES[model] = fails
        if fails >= 2:
            _MODEL_COOLDOWNS[model] = time.time() + 60.0  # 60s cooldown


def _record_model_success(model: str) -> None:
    """Reset failure counter and remove cooldown on model success."""
    with _CIRCUIT_LOCK:
        _MODEL_FAILURES[model] = 0
        _MODEL_COOLDOWNS.pop(model, None)


def _classify_error(exc: Exception) -> Tuple[str, Optional[int]]:
    """Inspect exception attributes and string message to classify HTTP status code.

    Returns:
        Tuple of (classification_category, optional_status_code).
        Categories: 'auth', 'not_found', 'thinking_issue', 'bad_request', 'transient', 'unknown'
    """
    status_code: Optional[int] = None

    # Check common status code attributes on SDK/HTTP exceptions
    for attr in ("status_code", "code", "http_status"):
        val = getattr(exc, attr, None)
        if isinstance(val, int):
            status_code = val
            break

    msg = str(exc)

    if status_code is None:
        # Regex search for 3-digit HTTP status code in message
        match = re.search(r"\b(400|401|403|404|429|500|502|503|504)\b", msg)
        if match:
            status_code = int(match.group(1))

    if status_code in (401, 403):
        return "auth", status_code

    if status_code == 404:
        return "not_found", status_code

    if status_code == 400:
        if "thinking" in msg.lower():
            return "thinking_issue", 400
        return "bad_request", 400

    if status_code in (429, 500, 502, 503, 504) or "timeout" in msg.lower() or "connection" in msg.lower():
        return "transient", status_code

    return "unknown", status_code


class GeminiClient:
    """Centralized, resilient client for Google GenAI SDK with multi-model fallback."""

    def __init__(self) -> None:
        """Initialize lazy client placeholder without connecting on import."""
        self._client: Optional[genai.Client] = None
        self._api_key: Optional[str] = None

    def _get_client(self) -> genai.Client:
        """Lazily initialize and return the Google GenAI SDK client.

        Raises:
            ValueError: If GEMINI_API_KEY is not configured in the environment.
        """
        if not os.getenv("GEMINI_API_KEY"):
            load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key or api_key == "your_gemini_api_key_here":
            raise ValueError(
                "GEMINI_API_KEY is not configured. Please provide a valid Gemini API key in your .env file."
            )

        if self._client is None or self._api_key != api_key:
            # Disable internal SDK retries: 1 attempt only, our application handles retries
            retry_opts = types.HttpRetryOptions(attempts=1)
            # Enforce strict request timeout in milliseconds
            http_opts = types.HttpOptions(
                timeout=int(GEMINI_TIMEOUT_SECONDS * 1000),
                retry_options=retry_opts,
            )
            self._client = genai.Client(api_key=api_key, http_options=http_opts)
            self._api_key = api_key

        return self._client

    def _get_model_chain(self, task: str) -> List[str]:
        """Retrieve model priority chain based on task type.

        Args:
            task: "light" or "heavy".

        Returns:
            List of model names to attempt sequentially.
        """
        if task == "heavy":
            return _parse_model_chain("GEMINI_MODEL_CHAIN_HEAVY", DEFAULT_HEAVY_CHAIN)
        return _parse_model_chain("GEMINI_MODEL_CHAIN_LIGHT", DEFAULT_LIGHT_CHAIN)

    def generate_json(
        self,
        system_instruction: str,
        prompt: str,
        schema: Optional[Dict[str, Any]] = None,
        task: str = "light",
        task_fallback_name: str = "simplify",
        allow_demo_fallback: bool = True,
    ) -> Dict[str, Any]:
        """Execute a structured JSON generation request with complete 6-pillar resilience.

        Args:
            system_instruction: System prompt.
            prompt: User prompt content.
            schema: Expected JSON schema dictionary.
            task: "light" or "heavy".
            task_fallback_name: Name of demo data file to use for offline fallback.
            allow_demo_fallback: Whether to serve demo data if all models fail.

        Returns:
            Validated Python dictionary matching the required schema.

        Raises:
            RuntimeError: If all models fail and demo fallback is disabled.
            ValueError: If API key is missing and demo fallback is disabled.
        """
        start_time = time.time()
        global _LAST_CALL_INFO

        # 1. Content-Addressable Cache Check (< 5ms)
        cache_key = compute_cache_key(system_instruction, prompt, schema, task)
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            duration = time.time() - start_time
            _LAST_CALL_INFO = {
                "model_used": "cache",
                "source": "cache",
                "attempts": 0,
                "fell_back": False,
                "seconds": duration,
            }
            _record_call_log("cache", task, "200_CACHE_HIT", duration)
            return cached_result

        # Check API key presence before live network attempts
        try:
            client = self._get_client()
        except ValueError as val_err:
            if allow_demo_fallback:
                logger.info("API key unconfigured; serving offline demo fallback for %s", task_fallback_name)
                duration = time.time() - start_time
                demo_data = cache_manager.get_demo_fallback(task_fallback_name)
                _LAST_CALL_INFO = {
                    "model_used": "demo_data",
                    "source": "demo",
                    "attempts": 0,
                    "fell_back": True,
                    "seconds": duration,
                }
                _record_call_log("demo_fallback", task, "DEMO_FALLBACK_KEY_MISSING", duration)
                return demo_data
            raise val_err

        model_chain = self._get_model_chain(task)
        total_attempts = 0
        model_outcomes: List[str] = []

        # Check if all models in chain are in circuit breaker cooldown
        all_cooled = all(_is_model_cooling_down(m) for m in model_chain)

        for model_idx, model in enumerate(model_chain):
            if not all_cooled and _is_model_cooling_down(model):
                model_outcomes.append(f"{model}: skipped (circuit breaker cooldown)")
                continue

            fell_forward = model_idx > 0

            # Up to 2 retries per model for transient errors
            max_model_retries = 2
            attempt_in_model = 0
            disable_thinking = False

            while attempt_in_model <= max_model_retries:
                attempt_in_model += 1
                total_attempts += 1
                call_start = time.time()

                _enforce_rate_limit()

                try:
                    config_kwargs: Dict[str, Any] = {
                        "system_instruction": system_instruction,
                        "response_mime_type": "application/json",
                    }
                    if schema:
                        config_kwargs["response_schema"] = schema
                    if disable_thinking:
                        # Disable thinking config if model produced 400 thinking error
                        config_kwargs["thinking_config"] = types.ThinkingConfig(thinking_budget=0)

                    config = types.GenerateContentConfig(**config_kwargs)

                    response = client.models.generate_content(
                        model=model,
                        contents=prompt,
                        config=config,
                    )

                    call_duration = time.time() - call_start

                    # Validate response presence
                    if not response or not response.text:
                        _record_model_failure(model)
                        _record_call_log(model, task, "EMPTY_RESPONSE", call_duration)
                        model_outcomes.append(f"{model}: empty response")
                        break  # Fall forward to next model

                    # Output Parsing & Self-Healing JSON
                    raw_text = response.text.strip()
                    # Strip markdown code fences if present
                    clean_json_str = _strip_code_fences(raw_text)

                    parsed_dict = None
                    try:
                        parsed_dict = json.loads(clean_json_str)
                    except json.JSONDecodeError:
                        parsed_dict = None

                    # If parsing failed, trigger single self-healing retry on same model
                    if parsed_dict is None or not isinstance(parsed_dict, dict):
                        heal_prompt = f"{prompt}\n\nIMPORTANT: Return only valid JSON matching the schema."
                        heal_kwargs: Dict[str, Any] = {
                            "system_instruction": system_instruction,
                            "response_mime_type": "application/json",
                            "temperature": 0.0,
                        }
                        if schema:
                            heal_kwargs["response_schema"] = schema
                        heal_config = types.GenerateContentConfig(**heal_kwargs)
                        heal_resp = client.models.generate_content(
                            model=model,
                            contents=heal_prompt,
                            config=heal_config,
                        )
                        if heal_resp and heal_resp.text:
                            healed_clean = _strip_code_fences(heal_resp.text.strip())
                            try:
                                parsed_dict = json.loads(healed_clean)
                            except json.JSONDecodeError:
                                parsed_dict = None

                    if parsed_dict is None or not isinstance(parsed_dict, dict):
                        _record_model_failure(model)
                        _record_call_log(model, task, "JSON_PARSE_FAILURE", call_duration)
                        model_outcomes.append(f"{model}: invalid JSON payload")
                        break  # Fall forward

                    # Validate required schema keys
                    if schema and "required" in schema:
                        missing = [key for key in schema["required"] if key not in parsed_dict]
                        if missing:
                            _record_model_failure(model)
                            _record_call_log(model, task, f"SCHEMA_MISSING_{missing}", call_duration)
                            model_outcomes.append(f"{model}: missing required keys {missing}")
                            break  # Fall forward

                    # Success!
                    _record_model_success(model)
                    cache_manager.set(cache_key, parsed_dict)
                    total_duration = time.time() - start_time
                    _record_call_log(model, task, "200_SUCCESS", total_duration)

                    _LAST_CALL_INFO = {
                        "model_used": model,
                        "source": "live",
                        "attempts": total_attempts,
                        "fell_back": fell_forward,
                        "seconds": total_duration,
                    }
                    return parsed_dict

                except Exception as exc:
                    call_duration = time.time() - call_start
                    err_cat, status_code = _classify_error(exc)
                    masked_err = mask_sensitive_error(str(exc))

                    if err_cat == "auth":
                        # 401 / 403 Stop immediately, zero retries
                        _record_call_log(model, task, f"AUTH_ERROR_{status_code}", call_duration)
                        if allow_demo_fallback:
                            logger.warning("Auth failure; falling back to demo data.")
                            break  # Will break to demo fallback below
                        raise PermissionError(
                            "Gemini API key is invalid or unauthorized. Please verify your credentials."
                        ) from exc

                    elif err_cat == "not_found":
                        # 404 Model retired or not found: 0ms fall forward immediately
                        _record_call_log(model, task, "404_NOT_FOUND", call_duration)
                        model_outcomes.append(f"{model}: 404 Not Found")
                        break

                    elif err_cat == "thinking_issue":
                        # 400 with 'thinking': retry once without thinking_config
                        _record_call_log(model, task, "400_THINKING_RETRY", call_duration)
                        disable_thinking = True
                        continue

                    elif err_cat == "bad_request":
                        # Other 400: Stop immediately
                        _record_call_log(model, task, f"400_BAD_REQUEST: {masked_err}", call_duration)
                        model_outcomes.append(f"{model}: 400 Bad Request")
                        break

                    elif err_cat == "transient":
                        # 429 / 5xx / Timeout: Exponential backoff with jitter
                        _record_model_failure(model)
                        _record_call_log(model, task, f"TRANSIENT_{status_code or 'ERR'}", call_duration)
                        if attempt_in_model <= max_model_retries:
                            backoff = (2 ** (attempt_in_model - 1)) + random.uniform(0.0, 0.5)
                            time.sleep(backoff)
                            continue
                        else:
                            model_outcomes.append(f"{model}: exceeded {max_model_retries} transient retries")
                            break
                    else:
                        # Unknown error: record failure and fall forward
                        _record_model_failure(model)
                        _record_call_log(model, task, f"UNKNOWN_ERROR: {masked_err}", call_duration)
                        model_outcomes.append(f"{model}: error ({masked_err[:60]})")
                        break

        # If all models in the chain failed
        duration = time.time() - start_time
        if allow_demo_fallback:
            logger.warning("All Gemini models failed. Serving offline fallback for %s", task_fallback_name)
            demo_data = cache_manager.get_demo_fallback(task_fallback_name)
            _LAST_CALL_INFO = {
                "model_used": "demo_data",
                "source": "demo",
                "attempts": total_attempts,
                "fell_back": True,
                "seconds": duration,
            }
            _record_call_log("fallback", task, "ALL_MODELS_FAILED_SERVED_DEMO", duration)
            return demo_data

        raise RuntimeError(
            f"All Gemini models in fallback chain failed. Outcomes: {'; '.join(model_outcomes)}"
        )


def _strip_code_fences(text: str) -> str:
    """Remove markdown code fences (```json ... ```) from model output.

    Args:
        text: Raw model string.

    Returns:
        Clean JSON string ready for json.loads.
    """
    clean = text.strip()
    if clean.startswith("```"):
        # Remove opening fence
        clean = re.sub(r"^```[a-zA-Z]*\n?", "", clean)
        # Remove closing fence
        clean = re.sub(r"\n?```$", "", clean)
    return clean.strip()


# Global client instance
gemini_client = GeminiClient()
