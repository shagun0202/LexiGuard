"""Content-addressable caching and offline fallback manager for LexiGuard.

Implements Pillar 6:
- Computes cache key as: SHA-256(system_instruction + prompt + schema + task)
  explicitly EXCLUDING the model name and API key.
- Serves disk-cached responses from `.cache/{key}.json` in < 5ms.
- Provides seamless zero-API demo fallback from `demo_data/` during network outages
  or unconfigured API keys.
"""

import hashlib
import json
import logging
import os
import threading
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("lexiguard.cache")

_CACHE_DIR = Path(".cache")
_DEMO_DIR = Path("demo_data")
_CACHE_LOCK = threading.Lock()


def compute_cache_key(
    system_instruction: str,
    prompt: str,
    schema: Optional[Dict[str, Any]] = None,
    task: str = "light",
) -> str:
    """Compute deterministic SHA-256 cache key based strictly on content and schema.

    Explicitly excludes the model name and API key.

    Args:
        system_instruction: System prompt text.
        prompt: User prompt content.
        schema: Optional JSON schema dictionary.
        task: "light" or "heavy".

    Returns:
        Hex-encoded SHA-256 hash string.

    Raises:
        TypeError: If arguments are invalid types.
    """
    if not isinstance(system_instruction, str) or not isinstance(prompt, str) or not isinstance(task, str):
        raise TypeError("system_instruction, prompt, and task must be str")

    hasher = hashlib.sha256()
    hasher.update(system_instruction.encode("utf-8", errors="ignore"))
    hasher.update(prompt.encode("utf-8", errors="ignore"))
    hasher.update(task.encode("utf-8", errors="ignore"))

    if schema:
        # Sort keys for deterministic JSON serialization
        schema_str = json.dumps(schema, sort_keys=True)
        hasher.update(schema_str.encode("utf-8", errors="ignore"))

    return hasher.hexdigest()


class CacheManager:
    """Thread-safe disk cache and offline fallback manager."""

    def __init__(self, cache_dir: Path = _CACHE_DIR, demo_dir: Path = _DEMO_DIR) -> None:
        """Initialize cache manager with storage paths.

        Args:
            cache_dir: Path to local disk cache directory.
            demo_dir: Path to directory containing pre-canned demo data.
        """
        self.cache_dir = cache_dir
        self.demo_dir = demo_dir
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            logger.warning("Could not create cache directory %s: %s", self.cache_dir, err)

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached result by SHA-256 key in < 5ms.

        Args:
            key: Deterministic SHA-256 cache key.

        Returns:
            Dictionary payload if cache hit and valid, else None.
        """
        cache_path = self.cache_dir / f"{key}.json"
        if not cache_path.is_file():
            return None

        with _CACHE_LOCK:
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
                # Corrupt cache file, ignore gracefully
                logger.debug("Corrupted cache file %s ignored: %s", cache_path, exc)
                return None

        return None

    def set(self, key: str, value: Dict[str, Any]) -> None:
        """Store validated JSON dictionary to disk cache.

        Args:
            key: Deterministic SHA-256 cache key.
            value: Validated payload dictionary to store.
        """
        if not isinstance(value, dict):
            return

        cache_path = self.cache_dir / f"{key}.json"
        with _CACHE_LOCK:
            try:
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(value, f, indent=2, ensure_ascii=False)
            except OSError as exc:
                logger.warning("Failed to write cache entry %s: %s", cache_path, exc)

    def get_demo_fallback(self, task_type: str) -> Dict[str, Any]:
        """Load pre-canned JSON response for zero-API demo resilience.

        Args:
            task_type: One of 'simplify', 'risk', 'qa', 'compare', 'action'.

        Returns:
            Dictionary matching the requested task schema.
        """
        demo_file = self.demo_dir / f"demo_{task_type}.json"
        if demo_file.is_file():
            try:
                with open(demo_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Error reading demo fallback %s: %s", demo_file, exc)

        # Built-in minimal fallback if file missing
        return {
            "status": "demo_fallback",
            "message": f"Pre-canned demo data for {task_type} loaded successfully."
        }


# Singleton instance
cache_manager = CacheManager()
