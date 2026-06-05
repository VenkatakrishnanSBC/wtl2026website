"""Exponential-backoff retry helpers shared by the GA4 and GSC adapters.

Retries on transient API failures: HTTP 429 (rate limit / quota) and 5xx. Honors a
``Retry-After`` header when present. Non-transient errors (e.g. 403 permission denied)
are re-raised immediately so the user gets a clear, actionable message.
"""

from __future__ import annotations

import random
import time
from typing import Callable, TypeVar

T = TypeVar("T")

# Status codes we consider transient and worth retrying.
RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})

DEFAULT_MAX_ATTEMPTS = 4
BASE_DELAY_SECONDS = 1.0
MAX_DELAY_SECONDS = 32.0


def _status_of(exc: Exception) -> int | None:
    """Best-effort extraction of an HTTP status code from a Google client error."""
    # google-api-python-client raises googleapiclient.errors.HttpError with .resp.status
    resp = getattr(exc, "resp", None)
    if resp is not None:
        status = getattr(resp, "status", None)
        if status is not None:
            try:
                return int(status)
            except (TypeError, ValueError):
                return None
    # google-api-core (used by google-analytics-data) exposes .code on some errors,
    # and the gRPC status maps to HTTP-like semantics. We map the common ones.
    code = getattr(exc, "code", None)
    if callable(code):  # grpc.StatusCode-style
        try:
            name = code().name  # type: ignore[call-arg]
        except Exception:  # pragma: no cover - defensive
            name = None
        mapping = {
            "RESOURCE_EXHAUSTED": 429,
            "UNAVAILABLE": 503,
            "INTERNAL": 500,
            "DEADLINE_EXCEEDED": 504,
        }
        if name in mapping:
            return mapping[name]
    # google-api-core exceptions expose an integer .code attribute too.
    if isinstance(code, int):
        return code
    return None


def _retry_after_seconds(exc: Exception) -> float | None:
    """Extract a Retry-After hint (seconds) from response headers, if present."""
    resp = getattr(exc, "resp", None)
    if resp is not None:
        headers = getattr(resp, "headers", None) or {}
        value = headers.get("retry-after") or headers.get("Retry-After")
        if value:
            try:
                return float(value)
            except (TypeError, ValueError):
                return None
    return None


def with_retry(
    func: Callable[[], T],
    *,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    base_delay: float = BASE_DELAY_SECONDS,
    sleep: Callable[[float], None] = time.sleep,
    on_retry: Callable[[int, float, Exception], None] | None = None,
) -> T:
    """Call ``func`` with exponential backoff on transient API errors.

    Args:
        func: Zero-argument callable performing the API request.
        max_attempts: Total attempts including the first.
        base_delay: Initial delay; doubles each attempt (capped), plus jitter.
        sleep: Injectable sleep (for tests).
        on_retry: Optional callback (attempt, delay, exc) invoked before sleeping.

    Returns:
        Whatever ``func`` returns on success.

    Raises:
        The last exception if all attempts are exhausted, or immediately for
        non-transient errors.
    """
    attempt = 0
    while True:
        attempt += 1
        try:
            return func()
        except Exception as exc:  # noqa: BLE001 - we re-raise non-transient below
            status = _status_of(exc)
            transient = status in RETRYABLE_STATUS if status is not None else False
            if not transient or attempt >= max_attempts:
                raise
            retry_after = _retry_after_seconds(exc)
            if retry_after is not None:
                delay = retry_after
            else:
                delay = min(base_delay * (2 ** (attempt - 1)), MAX_DELAY_SECONDS)
                delay += random.uniform(0, delay * 0.25)  # jitter
            if on_retry is not None:
                on_retry(attempt, delay, exc)
            sleep(delay)
