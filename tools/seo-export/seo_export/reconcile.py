"""Reconcile GSC page-level data with GA4 landing-page data.

Joins on normalized URL path. Surfaces "High-Visibility, Low-Connection" anomalies:
pages with above-median GSC impressions but weak GA4 engagement
(engagement_rate < 0.5 OR avg engagement time < 20s).
"""

from __future__ import annotations

from seo_export.normalize import median

# Anomaly thresholds (see README "Reconcile output & anomaly logic").
ENGAGEMENT_RATE_FLOOR = 0.5
ENGAGEMENT_TIME_FLOOR_SEC = 20.0
TOP_QUERIES_PER_PAGE = 5

# Output column order — stable schema for downstream consumers.
RECONCILE_COLUMNS = [
    "page",
    "language",
    "top_queries",
    "gsc_impressions",
    "gsc_clicks",
    "gsc_ctr",
    "gsc_avg_position",
    "ga4_sessions",
    "ga4_engagement_rate",
    "ga4_avg_engagement_time_sec",
    "ga4_key_events",
    "ga4_key_event_rate",
    "anomaly",
]


def _top_queries_by_page(query_rows: list[dict]) -> dict[str, str]:
    """Build {page: "q1|q2|...|q5"} ranked by impressions per page."""
    by_page: dict[str, list[tuple[str, int]]] = {}
    for r in query_rows:
        page = r.get("page", "")
        query = r.get("query", "")
        if not page or not query:
            continue
        by_page.setdefault(page, []).append((query, r.get("impressions", 0)))
    out: dict[str, str] = {}
    for page, items in by_page.items():
        items.sort(key=lambda t: t[1], reverse=True)
        top = [q for q, _ in items[:TOP_QUERIES_PER_PAGE]]
        out[page] = "|".join(top)
    return out


def _ga4_by_page(landing_rows: list[dict]) -> dict[str, dict]:
    """Aggregate GA4 landing rows to one record per page (across channel groups).

    The landing report is keyed by (landing_page, channel_group); for reconciliation
    we want page-level totals, so we sum sessions/durations/key-events and recompute
    engagement_rate and avg engagement time as weighted averages.
    """
    agg: dict[str, dict] = {}
    for r in landing_rows:
        page = r["landing_page"]
        a = agg.setdefault(
            page,
            {
                "sessions": 0,
                "engaged_sessions": 0,
                "user_engagement_duration_sec": 0.0,
                "key_events": 0,
            },
        )
        a["sessions"] += r.get("sessions", 0)
        a["engaged_sessions"] += r.get("engaged_sessions", 0)
        a["user_engagement_duration_sec"] += r.get("user_engagement_duration_sec", 0.0)
        a["key_events"] += r.get("key_events", 0)

    out: dict[str, dict] = {}
    for page, a in agg.items():
        sessions = a["sessions"]
        engaged = a["engaged_sessions"]
        out[page] = {
            "ga4_sessions": sessions,
            "ga4_engagement_rate": (engaged / sessions) if sessions else 0.0,
            # GA4 avg engagement time per session = total user engagement / sessions.
            "ga4_avg_engagement_time_sec": (
                a["user_engagement_duration_sec"] / sessions if sessions else 0.0
            ),
            "ga4_key_events": a["key_events"],
            "ga4_key_event_rate": (a["key_events"] / sessions) if sessions else 0.0,
        }
    return out


def reconcile(
    gsc_page_rows: list[dict],
    gsc_query_rows: list[dict],
    ga4_landing_rows: list[dict],
) -> list[dict]:
    """Join GSC page aggregates + top queries with GA4 page-level behavior.

    Args:
        gsc_page_rows: Output of :func:`seo_export.gsc.pages`.
        gsc_query_rows: Output of :func:`seo_export.gsc.queries` (for top_queries).
        ga4_landing_rows: Output of :func:`seo_export.ga4.landing_pages`
            (strip_query recommended so paths join cleanly).

    Returns:
        Rows ordered by gsc_impressions desc, conforming to RECONCILE_COLUMNS, each
        with an ``anomaly`` boolean flag.
    """
    from seo_export.normalize import language_of

    top_queries = _top_queries_by_page(gsc_query_rows)
    ga4_by_page = _ga4_by_page(ga4_landing_rows)

    # Full outer join on page: a page may have GSC data, GA4 data, or both.
    all_pages = set(r["page"] for r in gsc_page_rows) | set(ga4_by_page.keys())

    gsc_by_page = {r["page"]: r for r in gsc_page_rows}

    # Median impressions across pages that have GSC impressions, for the anomaly test.
    impressions_values = [
        r["impressions"] for r in gsc_page_rows if r.get("impressions", 0) > 0
    ]
    impressions_median = median([float(v) for v in impressions_values])

    rows: list[dict] = []
    for page in all_pages:
        g = gsc_by_page.get(page, {})
        a = ga4_by_page.get(page, {})

        gsc_impr = g.get("impressions", 0)
        eng_rate = a.get("ga4_engagement_rate", 0.0)
        eng_time = a.get("ga4_avg_engagement_time_sec", 0.0)

        # Anomaly: strong visibility (above-median impressions) but weak connection.
        has_ga4 = page in ga4_by_page
        above_median = gsc_impr > impressions_median and gsc_impr > 0
        weak_engagement = (eng_rate < ENGAGEMENT_RATE_FLOOR) or (
            eng_time < ENGAGEMENT_TIME_FLOOR_SEC
        )
        anomaly = bool(above_median and has_ga4 and weak_engagement)

        rows.append(
            {
                "page": page,
                "language": language_of(page),
                "top_queries": top_queries.get(page, ""),
                "gsc_impressions": gsc_impr,
                "gsc_clicks": g.get("clicks", 0),
                "gsc_ctr": g.get("ctr", 0.0),
                "gsc_avg_position": g.get("position", 0.0),
                "ga4_sessions": a.get("ga4_sessions", 0),
                "ga4_engagement_rate": eng_rate,
                "ga4_avg_engagement_time_sec": eng_time,
                "ga4_key_events": a.get("ga4_key_events", 0),
                "ga4_key_event_rate": a.get("ga4_key_event_rate", 0.0),
                "anomaly": anomaly,
            }
        )

    rows.sort(key=lambda r: r["gsc_impressions"], reverse=True)
    return rows
