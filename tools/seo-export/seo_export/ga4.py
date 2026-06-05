"""GA4 Data API adapter (runReport).

Provides two reports used downstream:
  - landing_pages(): session/engagement metrics per landing page + channel group.
  - key_events(): key-event counts per landing page x event name.

All public functions return normalized list[dict] rows with explicit numeric types.
Retries on 429/5xx via :mod:`seo_export.retry`.
"""

from __future__ import annotations

from typing import Optional

from seo_export.auth import GA4_SCOPES, credentials_for, service_account_email
from seo_export.config import Config
from seo_export.normalize import normalize_path, to_float, to_int
from seo_export.retry import with_retry

# GA4 channel group value for organic search, used by the --channel organic filter.
ORGANIC_CHANNEL = "Organic Search"

LANDING_METRICS = [
    "sessions",
    "engagedSessions",
    "engagementRate",
    "userEngagementDuration",
    "averageSessionDuration",
    "keyEvents",
    "bounceRate",
]


class GA4Error(Exception):
    """Raised on GA4 API failures, with actionable guidance for permission errors."""


def _client(config: Config):
    """Build a BetaAnalyticsDataClient from config credentials."""
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
    except ImportError as exc:  # pragma: no cover
        raise GA4Error(
            "google-analytics-data is not installed. Run: pip install -r requirements.txt"
        ) from exc
    creds = credentials_for(config, GA4_SCOPES)
    return BetaAnalyticsDataClient(credentials=creds)


def _wrap_permission_error(exc: Exception, config: Config) -> GA4Error:
    """Turn a raw 403/permission error into a clear remediation message."""
    sa_email = service_account_email(config.credentials_path) or "<your-service-account-email>"
    return GA4Error(
        f"GA4 request failed: {exc}\n\n"
        "If this is a permission error (403 / PERMISSION_DENIED), the service "
        f"account is not authorized on GA4 property {config.ga4_property_id}.\n"
        "Fix: GA4 Admin -> Property Access Management -> '+' -> add this email as "
        f"a Viewer:\n    {sa_email}\n"
        "Also confirm GA4_PROPERTY_ID is the NUMERIC property id (not G-XXXX)."
    )


def _run_report(config: Config, request) -> object:
    """Execute a runReport request with retry, wrapping permission errors."""
    client = _client(config)
    try:
        return with_retry(lambda: client.run_report(request))
    except Exception as exc:  # noqa: BLE001
        raise _wrap_permission_error(exc, config) from exc


def get_property_metadata(config: Config) -> dict:
    """Fetch property metadata (used by ``verify``) to confirm access.

    Returns a small dict with property id, currency, and timezone.
    """
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import GetMetadataRequest
    except ImportError as exc:  # pragma: no cover
        raise GA4Error("google-analytics-data not installed.") from exc

    creds = credentials_for(config, GA4_SCOPES)
    client = BetaAnalyticsDataClient(credentials=creds)
    name = f"properties/{config.ga4_property_id}/metadata"
    try:
        meta = with_retry(lambda: client.get_metadata(GetMetadataRequest(name=name)))
    except Exception as exc:  # noqa: BLE001
        raise _wrap_permission_error(exc, config) from exc
    return {
        "property_id": config.ga4_property_id,
        "dimension_count": len(meta.dimensions),
        "metric_count": len(meta.metrics),
    }


def _build_organic_filter():
    """Return a FilterExpression restricting to Organic Search channel group."""
    from google.analytics.data_v1beta.types import Filter, FilterExpression

    return FilterExpression(
        filter=Filter(
            field_name="sessionDefaultChannelGroup",
            string_filter=Filter.StringFilter(value=ORGANIC_CHANNEL),
        )
    )


def landing_pages(
    config: Config,
    start: str,
    end: str,
    *,
    organic_only: bool = False,
    strip_query: bool = False,
    row_limit: int = 100_000,
) -> list[dict]:
    """Run the landing-pages report.

    Dimensions: landingPagePlusQueryString, sessionDefaultChannelGroup.
    Metrics: see :data:`LANDING_METRICS`.

    Args:
        organic_only: When True, filter to ``Organic Search`` channel group.
        strip_query: When True, normalize landing page paths without query strings.
            Rows that collapse to the same path are summed (sessions, durations) and
            engagement rates are recomputed as weighted averages.

    Returns:
        Normalized rows with keys: landing_page, channel_group, sessions,
        engaged_sessions, engagement_rate, user_engagement_duration_sec,
        avg_session_duration_sec, key_events, bounce_rate.
    """
    from google.analytics.data_v1beta.types import (
        DateRange,
        Dimension,
        Metric,
        RunReportRequest,
    )

    request = RunReportRequest(
        property=f"properties/{config.ga4_property_id}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[
            Dimension(name="landingPagePlusQueryString"),
            Dimension(name="sessionDefaultChannelGroup"),
        ],
        metrics=[Metric(name=m) for m in LANDING_METRICS],
        dimension_filter=_build_organic_filter() if organic_only else None,
        limit=row_limit,
    )
    response = _run_report(config, request)
    rows = _parse_landing_rows(response, strip_query=strip_query)
    return rows


def _parse_landing_rows(response, *, strip_query: bool) -> list[dict]:
    """Convert a GA4 runReport response into normalized landing-page rows."""
    raw_rows: list[dict] = []
    for row in response.rows:
        landing_raw = row.dimension_values[0].value
        channel = row.dimension_values[1].value
        m = [mv.value for mv in row.metric_values]
        raw_rows.append(
            {
                "landing_page": normalize_path(landing_raw, strip_query=strip_query),
                "channel_group": channel,
                "sessions": to_int(m[0]),
                "engaged_sessions": to_int(m[1]),
                "engagement_rate": to_float(m[2]),
                "user_engagement_duration_sec": to_float(m[3]),
                "avg_session_duration_sec": to_float(m[4]),
                "key_events": to_int(m[5]),
                "bounce_rate": to_float(m[6]),
            }
        )

    if not strip_query:
        return raw_rows

    # When stripping the query string, multiple GA4 rows can collapse to one path
    # (per channel). Re-aggregate so totals stay correct.
    return _aggregate_landing_rows(raw_rows)


def _aggregate_landing_rows(rows: list[dict]) -> list[dict]:
    """Sum collapsed landing-page rows and recompute weighted rate metrics."""
    grouped: dict[tuple[str, str], dict] = {}
    for r in rows:
        key = (r["landing_page"], r["channel_group"])
        acc = grouped.setdefault(
            key,
            {
                "landing_page": r["landing_page"],
                "channel_group": r["channel_group"],
                "sessions": 0,
                "engaged_sessions": 0,
                "user_engagement_duration_sec": 0.0,
                "_session_duration_weighted": 0.0,
                "key_events": 0,
            },
        )
        acc["sessions"] += r["sessions"]
        acc["engaged_sessions"] += r["engaged_sessions"]
        acc["user_engagement_duration_sec"] += r["user_engagement_duration_sec"]
        acc["_session_duration_weighted"] += r["avg_session_duration_sec"] * r["sessions"]
        acc["key_events"] += r["key_events"]

    out: list[dict] = []
    for acc in grouped.values():
        sessions = acc["sessions"]
        engaged = acc["engaged_sessions"]
        out.append(
            {
                "landing_page": acc["landing_page"],
                "channel_group": acc["channel_group"],
                "sessions": sessions,
                "engaged_sessions": engaged,
                "engagement_rate": (engaged / sessions) if sessions else 0.0,
                "user_engagement_duration_sec": acc["user_engagement_duration_sec"],
                "avg_session_duration_sec": (
                    acc["_session_duration_weighted"] / sessions if sessions else 0.0
                ),
                "key_events": acc["key_events"],
                "bounce_rate": (1.0 - (engaged / sessions)) if sessions else 0.0,
            }
        )
    out.sort(key=lambda r: r["sessions"], reverse=True)
    return out


def key_events(
    config: Config,
    start: str,
    end: str,
    *,
    organic_only: bool = False,
    strip_query: bool = False,
    row_limit: int = 100_000,
) -> list[dict]:
    """Run the key-events breakdown: keyEvents per landing page x event name.

    Returns rows with keys: landing_page, event_name, key_events.
    Rows with zero key events for an event are omitted by the API.
    """
    from google.analytics.data_v1beta.types import (
        DateRange,
        Dimension,
        Metric,
        RunReportRequest,
    )

    request = RunReportRequest(
        property=f"properties/{config.ga4_property_id}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[
            Dimension(name="landingPagePlusQueryString"),
            Dimension(name="eventName"),
        ],
        metrics=[Metric(name="keyEvents")],
        dimension_filter=_build_organic_filter() if organic_only else None,
        limit=row_limit,
    )
    response = _run_report(config, request)

    rows: list[dict] = []
    for row in response.rows:
        count = to_int(row.metric_values[0].value)
        if not count:
            continue  # only emit events that actually fired as key events
        rows.append(
            {
                "landing_page": normalize_path(
                    row.dimension_values[0].value, strip_query=strip_query
                ),
                "event_name": row.dimension_values[1].value,
                "key_events": count,
            }
        )

    if strip_query:
        merged: dict[tuple[str, str], int] = {}
        for r in rows:
            k = (r["landing_page"], r["event_name"])
            merged[k] = merged.get(k, 0) + r["key_events"]
        rows = [
            {"landing_page": lp, "event_name": ev, "key_events": c}
            for (lp, ev), c in merged.items()
        ]
    rows.sort(key=lambda r: r["key_events"], reverse=True)
    return rows
