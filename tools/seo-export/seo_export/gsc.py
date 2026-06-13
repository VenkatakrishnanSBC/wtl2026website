"""Google Search Console adapter (Search Analytics API).

Provides:
  - queries(): query x page rows (with optional country/device dims).
  - pages(): page-level aggregate rows.
  - list_sites(): used by ``verify`` to confirm the site is accessible.

Handles the 25,000-row-per-request cap via startRow pagination. Retries on 429/5xx.
"""

from __future__ import annotations

from typing import Optional

from seo_export.auth import GSC_SCOPES, credentials_for, service_account_email
from seo_export.config import Config
from seo_export.normalize import normalize_path, to_float, to_int
from seo_export.retry import with_retry

GSC_ROW_LIMIT = 25_000  # API hard cap per request


class GSCError(Exception):
    """Raised on GSC API failures, with guidance for permission errors."""


def _service(config: Config):
    """Build a Search Console API service client."""
    try:
        from googleapiclient.discovery import build
    except ImportError as exc:  # pragma: no cover
        raise GSCError(
            "google-api-python-client is not installed. Run: pip install -r requirements.txt"
        ) from exc
    creds = credentials_for(config, GSC_SCOPES)
    # cache_discovery=False avoids noisy warnings and filesystem cache writes.
    return build("searchconsole", "v1", credentials=creds, cache_discovery=False)


def _wrap_permission_error(exc: Exception, config: Config) -> GSCError:
    """Turn a raw 403 into a clear remediation message."""
    sa_email = service_account_email(config.credentials_path) or "<your-service-account-email>"
    return GSCError(
        f"GSC request failed: {exc}\n\n"
        "If this is a permission error (403), the service account is not authorized "
        f"on GSC property '{config.gsc_site_url}'.\n"
        "Fix: Search Console -> Settings -> Users and permissions -> 'Add user' -> "
        f"add this email as Full or Restricted:\n    {sa_email}\n"
        "Also confirm GSC_SITE_URL matches the property exactly (URL-prefix needs the "
        "trailing slash; domain properties use the 'sc-domain:' prefix)."
    )


def list_sites(config: Config) -> list[dict]:
    """Return the list of sites the service account can access (for ``verify``)."""
    service = _service(config)
    try:
        resp = with_retry(lambda: service.sites().list().execute())
    except Exception as exc:  # noqa: BLE001
        raise _wrap_permission_error(exc, config) from exc
    return resp.get("siteEntry", [])


def _query_all(config: Config, body: dict) -> list[dict]:
    """Page through Search Analytics results until exhausted.

    The API returns at most GSC_ROW_LIMIT rows per call; we advance startRow until a
    short page (or empty page) is returned.
    """
    service = _service(config)
    site = config.gsc_site_url
    all_rows: list[dict] = []
    start_row = 0
    while True:
        page_body = dict(body)
        page_body["rowLimit"] = GSC_ROW_LIMIT
        page_body["startRow"] = start_row

        def _call(b=page_body):
            return service.searchanalytics().query(siteUrl=site, body=b).execute()

        try:
            resp = with_retry(_call)
        except Exception as exc:  # noqa: BLE001
            raise _wrap_permission_error(exc, config) from exc

        rows = resp.get("rows", [])
        all_rows.extend(rows)
        if len(rows) < GSC_ROW_LIMIT:
            break
        start_row += GSC_ROW_LIMIT
    return all_rows


def queries(
    config: Config,
    start: str,
    end: str,
    *,
    country: Optional[str] = None,
    device: Optional[str] = None,
    min_impressions: int = 0,
    low_ctr_below: Optional[float] = None,
) -> list[dict]:
    """Fetch query x page search analytics rows.

    Args:
        country: Optional ISO-3166-1-alpha-3 country code (e.g. 'sen'); adds the
            'country' dimension and filters server-side.
        device: Optional 'desktop' | 'mobile' | 'tablet'; adds the 'device' dimension.
        min_impressions: Keep only rows with impressions >= this value.
        low_ctr_below: When set, keep only rows with ctr < this value (anomaly hunt
            for high-impression, low-CTR queries). Combine with --min-impressions.

    Returns:
        Rows with keys: query, page (normalized path), [country], [device],
        clicks, impressions, ctr, position.
    """
    dimensions = ["query", "page"]
    if country:
        dimensions.append("country")
    if device:
        dimensions.append("device")

    body: dict = {
        "startDate": start,
        "endDate": end,
        "dimensions": dimensions,
        "dataState": "final",
    }
    filters = []
    if country:
        filters.append(
            {"dimension": "country", "operator": "equals", "expression": country.lower()}
        )
    if device:
        filters.append(
            {"dimension": "device", "operator": "equals", "expression": device.lower()}
        )
    if filters:
        body["dimensionFilterGroups"] = [{"filters": filters}]

    raw = _query_all(config, body)
    rows = _parse_query_rows(raw, dimensions)

    if min_impressions:
        rows = [r for r in rows if r["impressions"] >= min_impressions]
    if low_ctr_below is not None:
        rows = [r for r in rows if r["ctr"] < low_ctr_below]
    rows.sort(key=lambda r: r["impressions"], reverse=True)
    return rows


def _parse_query_rows(raw: list[dict], dimensions: list[str]) -> list[dict]:
    """Map GSC keys[] (positional per dimensions) into normalized dicts."""
    out: list[dict] = []
    for row in raw:
        keys = row.get("keys", [])
        record: dict = {}
        for i, dim in enumerate(dimensions):
            value = keys[i] if i < len(keys) else ""
            if dim == "page":
                record["page"] = normalize_path(value, strip_query=True)
            else:
                record[dim] = value
        record["clicks"] = to_int(row.get("clicks"))
        record["impressions"] = to_int(row.get("impressions"))
        record["ctr"] = to_float(row.get("ctr"))
        record["position"] = to_float(row.get("position"))
        out.append(record)
    return out


def bucket_for(verdict: str, coverage_state: str) -> str:
    """Roll a URL Inspection result into one coarse indexation bucket.

    The raw ``coverageState`` string is preserved on each row; this is only for
    the summary roll-up so the user sees indexed / crawled-not-indexed /
    discovered-not-indexed / unknown / excluded counts at a glance.
    """
    cs = (coverage_state or "").lower()
    if "unknown to google" in cs:
        return "unknown"
    if "indexed" in cs and "not indexed" not in cs:
        return "indexed"
    if "crawled" in cs and "not indexed" in cs:
        return "crawled_not_indexed"
    if "discovered" in cs and "not indexed" in cs:
        return "discovered_not_indexed"
    if any(
        k in cs
        for k in ("excluded", "noindex", "redirect", "alternate", "canonical",
                  "blocked", "not found", "soft 404")
    ):
        return "excluded"
    return "indexed" if (verdict or "").upper() == "PASS" else "other"


def inspect_url(config: Config, url: str) -> dict:
    """Inspect one URL via the URL Inspection API and normalize the result.

    A single failing URL records its error inline (bucket="error") rather than
    aborting the whole sample, except for 403s which mean a permission problem
    worth surfacing immediately.

    Returns a row with keys: url, verdict, coverage_state, bucket,
    indexing_state, robots_txt_state, page_fetch_state, last_crawl_time,
    google_canonical, user_canonical, canonical_match, in_sitemap,
    referring_urls, inspection_link, error.
    """
    service = _service(config)

    def _call():
        return (
            service.urlInspection()
            .index()
            .inspect(body={"inspectionUrl": url, "siteUrl": config.gsc_site_url})
            .execute()
        )

    try:
        resp = with_retry(_call)
    except Exception as exc:  # noqa: BLE001
        msg = str(exc)
        if "403" in msg or "PERMISSION_DENIED" in msg:
            raise _wrap_permission_error(exc, config) from exc
        return {
            "url": url, "verdict": "", "coverage_state": "", "bucket": "error",
            "indexing_state": "", "robots_txt_state": "", "page_fetch_state": "",
            "last_crawl_time": "", "google_canonical": "", "user_canonical": "",
            "canonical_match": "", "in_sitemap": "", "referring_urls": 0,
            "inspection_link": "", "error": msg[:200],
        }

    result = resp.get("inspectionResult", {})
    idx = result.get("indexStatusResult", {})
    google_canonical = idx.get("googleCanonical", "")
    user_canonical = idx.get("userCanonical", "")
    verdict = idx.get("verdict", "")
    coverage = idx.get("coverageState", "")
    return {
        "url": url,
        "verdict": verdict,
        "coverage_state": coverage,
        "bucket": bucket_for(verdict, coverage),
        "indexing_state": idx.get("indexingState", ""),
        "robots_txt_state": idx.get("robotsTxtState", ""),
        "page_fetch_state": idx.get("pageFetchState", ""),
        "last_crawl_time": idx.get("lastCrawlTime", ""),
        "google_canonical": google_canonical,
        "user_canonical": user_canonical,
        "canonical_match": bool(google_canonical) and google_canonical == user_canonical,
        "in_sitemap": bool(idx.get("sitemap")),
        "referring_urls": len(idx.get("referringUrls", []) or []),
        "inspection_link": result.get("inspectionResultLink", ""),
        "error": "",
    }


def inspect_urls(config: Config, urls: list[str], *, on_progress=None) -> list[dict]:
    """Inspect each URL sequentially (the Inspection API is per-URL, not batched).

    Args:
        on_progress: optional callback(index, total, row) for live feedback.
    """
    rows: list[dict] = []
    total = len(urls)
    for i, url in enumerate(urls, 1):
        row = inspect_url(config, url)
        rows.append(row)
        if on_progress is not None:
            on_progress(i, total, row)
    return rows


def pages(
    config: Config,
    start: str,
    end: str,
    *,
    min_impressions: int = 0,
) -> list[dict]:
    """Fetch page-level aggregate rows (dimension 'page' only).

    Returns rows with keys: page (normalized path), clicks, impressions, ctr, position.
    """
    body = {
        "startDate": start,
        "endDate": end,
        "dimensions": ["page"],
        "dataState": "final",
    }
    raw = _query_all(config, body)
    rows = _parse_query_rows(raw, ["page"])
    if min_impressions:
        rows = [r for r in rows if r["impressions"] >= min_impressions]
    rows.sort(key=lambda r: r["impressions"], reverse=True)
    return rows
