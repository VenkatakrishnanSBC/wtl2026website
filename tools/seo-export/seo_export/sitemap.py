"""Fetch and parse a sitemap (or sitemap index) into a flat list of page URLs.

Used by the ``gsc-inspect`` command to choose which URLs to send to the URL
Inspection API. Only <loc> values inside <url> entries are returned — the
hreflang <xhtml:link> alternates are ignored (they're already separate <url>
entries in a well-formed multilingual sitemap).
"""

from __future__ import annotations

import urllib.request
import xml.etree.ElementTree as ET

_SM_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
_USER_AGENT = "wtl-seo-export/0.1 (+sitemap fetch)"


def fetch_sitemap_urls(sitemap_url: str, *, _depth: int = 0) -> list[str]:
    """Return the page URLs listed in a sitemap, recursing into sitemap indexes.

    Args:
        sitemap_url: Absolute URL of a sitemap.xml or sitemap index.
        _depth: Internal recursion guard for nested sitemap indexes.

    Returns:
        De-duplicated list of <loc> page URLs, in document order.

    Raises:
        ValueError: If the document can't be fetched or parsed as a sitemap.
    """
    if _depth > 5:
        return []  # defensive: avoid pathological nesting
    req = urllib.request.Request(sitemap_url, headers={"User-Agent": _USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 - trusted own sitemap
            raw = resp.read()
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Could not fetch sitemap {sitemap_url}: {exc}") from exc

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError(f"Sitemap {sitemap_url} is not valid XML: {exc}") from exc

    tag = root.tag.lower()
    urls: list[str] = []

    if tag.endswith("sitemapindex"):
        for sm in root.findall(f"{_SM_NS}sitemap"):
            loc = sm.find(f"{_SM_NS}loc")
            if loc is not None and loc.text:
                urls.extend(fetch_sitemap_urls(loc.text.strip(), _depth=_depth + 1))
    else:
        for url in root.findall(f"{_SM_NS}url"):
            loc = url.find(f"{_SM_NS}loc")
            if loc is not None and loc.text:
                urls.append(loc.text.strip())

    # De-dup while preserving order.
    seen: set[str] = set()
    out: list[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def even_sample(urls: list[str], n: int) -> list[str]:
    """Pick ``n`` URLs spread evenly across the list (not just the first n).

    Even sampling avoids over-representing whichever section of the sitemap
    happens to come first, so the indexation buckets reflect the whole site.
    """
    if n <= 0 or not urls:
        return []
    if n >= len(urls):
        return list(urls)
    step = len(urls) / n
    picked = [urls[min(len(urls) - 1, int(i * step))] for i in range(n)]
    # int(i*step) can collide near the end; de-dup and top up if needed.
    seen: set[str] = set()
    out: list[str] = []
    for u in picked:
        if u not in seen:
            seen.add(u)
            out.append(u)
    i = 0
    while len(out) < n and i < len(urls):
        if urls[i] not in seen:
            seen.add(urls[i])
            out.append(urls[i])
        i += 1
    return out
