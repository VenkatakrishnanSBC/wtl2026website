"""URL normalization and numeric coercion helpers.

The reconcile step joins GSC (page = full URL) against GA4 (landing page = path +
query). To join reliably we collapse both to a canonical path that:
  - strips protocol and domain,
  - strips query string and fragment,
  - normalizes trailing slashes (everything but root has no trailing slash),
  - PRESERVES /fr/ and /de/ language prefixes so languages stay separable.
"""

from __future__ import annotations

from typing import Optional
from urllib.parse import urlsplit


def normalize_path(url_or_path: str, *, strip_query: bool = True) -> str:
    """Reduce a URL or GA4 landing path to a canonical join key.

    Args:
        url_or_path: A full URL ("https://host/fr/about?x=1"), a path ("/fr/about"),
            or GA4's landingPagePlusQueryString ("/fr/about?x=1").
        strip_query: When True (default) remove the query string. When False the
            query is preserved (used by ga4-landing-pages without --strip-query).

    Returns:
        A canonical path beginning with "/". Root collapses to "/". Language
        prefixes /fr and /de are preserved.
    """
    if url_or_path is None:
        return "/"
    raw = url_or_path.strip()
    if not raw:
        return "/"

    # GA4 sometimes returns "(not set)" or full URLs; handle both.
    if raw.lower() in {"(not set)", "(other)"}:
        return raw

    parts = urlsplit(raw if "://" in raw else "//" + raw if raw.startswith("//") else raw)
    # urlsplit on a bare path keeps it in .path; on a URL it populates .netloc.
    path = parts.path if (parts.scheme or parts.netloc) else raw

    # If we kept the raw path, it may still contain a query/fragment.
    query = ""
    if "?" in path:
        path, _, query_frag = path.partition("?")
        query = query_frag.split("#", 1)[0]
    elif parts.query:
        query = parts.query

    if "#" in path:
        path = path.split("#", 1)[0]

    if not path:
        path = "/"
    if not path.startswith("/"):
        path = "/" + path

    # Normalize trailing slash: root stays "/", everything else loses trailing "/".
    if len(path) > 1:
        path = path.rstrip("/")
        if not path:
            path = "/"

    if not strip_query and query:
        return f"{path}?{query}"
    return path


def language_of(path: str) -> str:
    """Return the language segment for a normalized path: 'fr', 'de', or 'en'."""
    if path.startswith("/fr/") or path == "/fr":
        return "fr"
    if path.startswith("/de/") or path == "/de":
        return "de"
    return "en"


def to_int(value: object, default: Optional[int] = 0) -> Optional[int]:
    """Coerce an API value to int, returning ``default`` on failure/empty."""
    if value is None or value == "":
        return default
    try:
        return int(round(float(value)))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def to_float(value: object, default: Optional[float] = 0.0) -> Optional[float]:
    """Coerce an API value to float, returning ``default`` on failure/empty."""
    if value is None or value == "":
        return default
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def median(values: list[float]) -> float:
    """Return the median of a numeric list; 0.0 for an empty list."""
    if not values:
        return 0.0
    ordered = sorted(values)
    n = len(ordered)
    mid = n // 2
    if n % 2 == 1:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0
