"""Command-line interface for seo_export.

Usage:
    python -m seo_export <command> [options]

Commands:
    verify             Authenticate and confirm access to the GA4 property and GSC site.
    ga4-landing-pages  GA4 landing-page sessions/engagement/key-event metrics.
    ga4-key-events     GA4 key-event counts per landing page x event name.
    gsc-queries        GSC query x page clicks/impressions/CTR/position.
    gsc-pages          GSC page-level aggregates.
    reconcile          Join GSC pages + queries with GA4 landing behavior; flag anomalies.
    export-all         Run every report and write a combined dated output set.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from seo_export.auth import AuthError, service_account_email
from seo_export.config import Config, ConfigError, default_date_range, load_config
from seo_export.output import dated_output_dir, write_rows


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--credentials",
        metavar="PATH",
        help="Service-account JSON key (overrides GOOGLE_APPLICATION_CREDENTIALS).",
    )
    parser.add_argument(
        "--env-file",
        metavar="PATH",
        help="Explicit .env file (default: tools/seo-export/.env).",
    )
    parser.add_argument(
        "--access-token",
        metavar="TOKEN",
        help="OAuth2 bearer access token (e.g. from the OAuth Playground). "
        "Overrides OAUTH_ACCESS_TOKEN and takes precedence over key-file auth.",
    )


def _add_dates(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--start", metavar="YYYY-MM-DD", help="Start date (default: 90 days ago).")
    parser.add_argument("--end", metavar="YYYY-MM-DD", help="End date (default: yesterday).")


def _add_output(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--format", choices=("csv", "json"), default="csv", help="Output format (default: csv)."
    )
    parser.add_argument(
        "--out", metavar="DIR", help="Output directory (default: exports/YYYY-MM-DD/)."
    )


def _add_channel(parser: argparse.ArgumentParser, default: str = "all") -> None:
    parser.add_argument(
        "--channel",
        choices=("all", "organic"),
        default=default,
        help=f"GA4 session channel-group filter (default: {default}).",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="seo_export",
        description=(
            "Export GA4 landing-page behavior and GSC search analytics for "
            "worldtransgroup.com, and reconcile them to surface "
            "'High-Visibility, Low-Connection' anomalies."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("verify", help="Confirm credentials and access to both properties.")
    _add_common(p)

    p = sub.add_parser("ga4-landing-pages", help="GA4 landing-page engagement report.")
    _add_common(p)
    _add_dates(p)
    _add_output(p)
    _add_channel(p)
    p.add_argument(
        "--strip-query",
        action="store_true",
        help="Collapse landing pages to bare paths (recommended for joins).",
    )

    p = sub.add_parser("ga4-key-events", help="GA4 key events per landing page x event name.")
    _add_common(p)
    _add_dates(p)
    _add_output(p)
    _add_channel(p)
    p.add_argument("--strip-query", action="store_true", help="Collapse landing pages to bare paths.")

    p = sub.add_parser("gsc-queries", help="GSC query x page search analytics.")
    _add_common(p)
    _add_dates(p)
    _add_output(p)
    p.add_argument(
        "--min-impressions", type=int, default=0, metavar="N",
        help="Keep only rows with impressions >= N.",
    )
    p.add_argument(
        "--low-ctr-below", type=float, default=None, metavar="RATE",
        help="Keep only rows with CTR < RATE (e.g. 0.02). Combine with --min-impressions "
        "to hunt high-impression, low-CTR anomalies.",
    )
    p.add_argument("--country", metavar="ISO3", help="Filter by ISO-3166-1-alpha-3 country (e.g. sen).")
    p.add_argument("--device", choices=("desktop", "mobile", "tablet"), help="Filter by device.")

    p = sub.add_parser("gsc-pages", help="GSC page-level aggregates.")
    _add_common(p)
    _add_dates(p)
    _add_output(p)
    p.add_argument("--min-impressions", type=int, default=0, metavar="N",
                   help="Keep only pages with impressions >= N.")

    p = sub.add_parser(
        "gsc-inspect",
        help="URL Inspection API: bucket sitemap URLs by indexation coverage state.",
    )
    _add_common(p)
    _add_output(p)
    p.add_argument(
        "--sitemap", metavar="URL",
        help="Sitemap URL to sample from (default: https://worldtransgroup.com/sitemap.xml).",
    )
    p.add_argument(
        "--sample", type=int, default=40, metavar="N",
        help="Number of URLs to inspect, spread evenly across the sitemap (default 40). "
        "Mind the ~2000/day Inspection quota.",
    )
    p.add_argument(
        "--url", action="append", metavar="URL",
        help="Inspect a specific URL (repeatable). Bypasses sitemap sampling; "
        "combine with --sample 0 to inspect only these.",
    )

    p = sub.add_parser(
        "gsc-sitemap",
        help="List submitted sitemaps, or resubmit one to force a re-download.",
    )
    _add_common(p)
    p.add_argument(
        "--resubmit", nargs="?", const=DEFAULT_SITEMAP, metavar="URL",
        help="Resubmit a sitemap (default: the site's sitemap.xml). Needs a "
        "read-write 'webmasters'-scope token.",
    )

    p = sub.add_parser(
        "reconcile",
        help="Join GSC pages/queries with GA4 landing behavior; flag anomalies.",
    )
    _add_common(p)
    _add_dates(p)
    _add_output(p)
    _add_channel(p, default="organic")

    p = sub.add_parser("export-all", help="Run every report into one dated output set.")
    _add_common(p)
    _add_dates(p)
    _add_output(p)
    _add_channel(p, default="organic")

    return parser


def _resolve(args: argparse.Namespace) -> tuple[Config, str, str]:
    """Load config and resolve the date range from args."""
    config = load_config(
        credentials_override=getattr(args, "credentials", None),
        env_file=getattr(args, "env_file", None),
        token_override=getattr(args, "access_token", None),
    )
    default_start, default_end = default_date_range()
    start = getattr(args, "start", None) or default_start
    end = getattr(args, "end", None) or default_end
    return config, start, end


def _out_dir(args: argparse.Namespace) -> Optional[Path]:
    out = getattr(args, "out", None)
    return Path(out) if out else None


def _emit(rows: list[dict], name: str, args: argparse.Namespace, columns=None) -> None:
    path = write_rows(
        rows, name, fmt=args.format, out_dir=_out_dir(args) or dated_output_dir(), columns=columns
    )
    print(f"{name}: {len(rows)} rows -> {path}")


def cmd_verify(args: argparse.Namespace) -> int:
    from seo_export import ga4, gsc

    config = load_config(
        credentials_override=args.credentials,
        env_file=args.env_file,
        token_override=args.access_token,
    )
    print("Configuration OK:")
    print(f"  GA4_PROPERTY_ID = {config.ga4_property_id}")
    print(f"  GSC_SITE_URL    = {config.gsc_site_url}")
    if config.oauth_client_id and config.oauth_client_secret and config.oauth_refresh_token:
        print("  Auth            = OAuth refresh token (all-time; auto-refreshes)")
    elif config.oauth_access_token:
        print("  Auth            = OAuth access token (expires ~1h after issue)")
    else:
        sa_email = service_account_email(config.credentials_path)
        if sa_email:
            print(f"  Service account = {sa_email}")

    print("\nChecking GA4 access...")
    meta = ga4.get_property_metadata(config)
    print(
        f"  OK: property {meta['property_id']} reachable "
        f"({meta['dimension_count']} dimensions, {meta['metric_count']} metrics)."
    )

    print("\nChecking GSC access...")
    sites = gsc.list_sites(config)
    urls = {s.get("siteUrl") for s in sites}
    for s in sites:
        print(f"  - {s.get('siteUrl')} ({s.get('permissionLevel')})")
    if config.gsc_site_url in urls:
        print(f"  OK: '{config.gsc_site_url}' is accessible.")
    else:
        print(
            f"  WARNING: '{config.gsc_site_url}' not in the service account's site list. "
            "Add the service account in Search Console -> Settings -> Users and permissions."
        )
        return 1
    print("\nverify: all checks passed.")
    return 0


def cmd_ga4_landing_pages(args: argparse.Namespace) -> int:
    from seo_export import ga4

    config, start, end = _resolve(args)
    rows = ga4.landing_pages(
        config, start, end,
        organic_only=(args.channel == "organic"),
        strip_query=args.strip_query,
    )
    _emit(rows, "ga4-landing-pages", args)
    return 0


def cmd_ga4_key_events(args: argparse.Namespace) -> int:
    from seo_export import ga4

    config, start, end = _resolve(args)
    rows = ga4.key_events(
        config, start, end,
        organic_only=(args.channel == "organic"),
        strip_query=args.strip_query,
    )
    _emit(rows, "ga4-key-events", args)
    return 0


def cmd_gsc_queries(args: argparse.Namespace) -> int:
    from seo_export import gsc

    config, start, end = _resolve(args)
    rows = gsc.queries(
        config, start, end,
        country=args.country,
        device=args.device,
        min_impressions=args.min_impressions,
        low_ctr_below=args.low_ctr_below,
    )
    _emit(rows, "gsc-queries", args)
    return 0


def cmd_gsc_pages(args: argparse.Namespace) -> int:
    from seo_export import gsc

    config, start, end = _resolve(args)
    rows = gsc.pages(config, start, end, min_impressions=args.min_impressions)
    _emit(rows, "gsc-pages", args)
    return 0


DEFAULT_SITEMAP = "https://worldtransgroup.com/sitemap.xml"

# Stable column order for the inspection CSV.
INSPECT_COLUMNS = [
    "url", "bucket", "coverage_state", "verdict", "indexing_state",
    "robots_txt_state", "page_fetch_state", "last_crawl_time",
    "google_canonical", "user_canonical", "canonical_match",
    "in_sitemap", "referring_urls", "inspection_link", "error",
]


def cmd_gsc_inspect(args: argparse.Namespace) -> int:
    from seo_export import gsc
    from seo_export.sitemap import even_sample, fetch_sitemap_urls

    config = load_config(
        credentials_override=args.credentials,
        env_file=args.env_file,
        token_override=args.access_token,
    )

    urls: list[str] = list(args.url or [])
    if args.sample > 0:
        sitemap_url = args.sitemap or DEFAULT_SITEMAP
        print(f"Fetching sitemap {sitemap_url} ...")
        all_urls = fetch_sitemap_urls(sitemap_url)
        print(f"  {len(all_urls)} URLs in sitemap; sampling {args.sample} evenly.")
        sampled = even_sample(all_urls, args.sample)
        # Keep any explicit --url first, then the sample (de-duped).
        for u in sampled:
            if u not in urls:
                urls.append(u)
    if not urls:
        print("error: nothing to inspect (use --url or a positive --sample).", file=sys.stderr)
        return 2

    print(f"Inspecting {len(urls)} URLs (sequential; ~2000/day quota)...")

    def _progress(i, total, row):
        print(f"  [{i}/{total}] {row['bucket']:<22} {row['url']}")

    rows = gsc.inspect_urls(config, urls, on_progress=_progress)

    # Roll-up summary by bucket.
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["bucket"]] = counts.get(r["bucket"], 0) + 1
    indexed = counts.get("indexed", 0)
    print("\n=== Indexation buckets ===")
    for bucket in ("indexed", "crawled_not_indexed", "discovered_not_indexed",
                   "unknown", "excluded", "other", "error"):
        if counts.get(bucket):
            print(f"  {bucket:<24} {counts[bucket]}")
    print(f"  {'TOTAL inspected':<24} {len(rows)}")
    if rows:
        print(f"  indexed share: {indexed}/{len(rows)} = {indexed/len(rows)*100:.0f}%")

    _emit(rows, "gsc-inspect", args, columns=INSPECT_COLUMNS)
    return 0


def cmd_gsc_sitemap(args: argparse.Namespace) -> int:
    from seo_export import gsc

    config = load_config(
        credentials_override=args.credentials,
        env_file=args.env_file,
        token_override=args.access_token,
    )

    if args.resubmit:
        print(f"Resubmitting sitemap: {args.resubmit}")
        gsc.submit_sitemap(config, args.resubmit)
        print("  submit accepted (HTTP 204). Google will re-download shortly.")

    # Always show current state (after a resubmit, confirms the new timestamp).
    sitemaps = gsc.list_sitemaps(config)
    if not sitemaps:
        print("No sitemaps submitted to this property.")
        return 0
    print(f"\nSitemaps for {config.gsc_site_url}:")
    for s in sitemaps:
        contents = s.get("contents", [{}])[0]
        print(f"  {s.get('path')}")
        print(f"    lastSubmitted:  {s.get('lastSubmitted')}")
        print(f"    lastDownloaded: {s.get('lastDownloaded')}  (stale if months old)")
        print(f"    isPending: {s.get('isPending')}  errors: {s.get('errors')}  warnings: {s.get('warnings')}")
        print(f"    submitted: {contents.get('submitted')}  indexed: {contents.get('indexed')}")
    return 0


def cmd_reconcile(args: argparse.Namespace) -> int:
    from seo_export import ga4, gsc
    from seo_export.reconcile import RECONCILE_COLUMNS, reconcile

    config, start, end = _resolve(args)
    organic = args.channel == "organic"

    print(f"Fetching GSC pages ({start}..{end})...")
    gsc_pages = gsc.pages(config, start, end)
    print(f"  {len(gsc_pages)} pages")
    print("Fetching GSC queries...")
    gsc_queries = gsc.queries(config, start, end)
    print(f"  {len(gsc_queries)} query x page rows")
    print(f"Fetching GA4 landing pages (channel={args.channel})...")
    ga4_rows = ga4.landing_pages(config, start, end, organic_only=organic, strip_query=True)
    print(f"  {len(ga4_rows)} landing-page rows")

    rows = reconcile(gsc_pages, gsc_queries, ga4_rows)
    anomalies = sum(1 for r in rows if r["anomaly"])
    _emit(rows, "reconcile", args, columns=RECONCILE_COLUMNS)
    print(f"High-Visibility, Low-Connection anomalies flagged: {anomalies}")
    return 0


def cmd_export_all(args: argparse.Namespace) -> int:
    from seo_export import ga4, gsc
    from seo_export.reconcile import RECONCILE_COLUMNS, reconcile

    config, start, end = _resolve(args)
    organic = args.channel == "organic"
    print(f"Export window: {start}..{end} (channel={args.channel})")

    rows = ga4.landing_pages(config, start, end, organic_only=organic, strip_query=True)
    _emit(rows, "ga4-landing-pages", args)
    ga4_landing = rows

    rows = ga4.key_events(config, start, end, organic_only=organic, strip_query=True)
    _emit(rows, "ga4-key-events", args)

    gsc_query_rows = gsc.queries(config, start, end)
    _emit(gsc_query_rows, "gsc-queries", args)

    gsc_page_rows = gsc.pages(config, start, end)
    _emit(gsc_page_rows, "gsc-pages", args)

    rows = reconcile(gsc_page_rows, gsc_query_rows, ga4_landing)
    anomalies = sum(1 for r in rows if r["anomaly"])
    _emit(rows, "reconcile", args, columns=RECONCILE_COLUMNS)
    print(f"High-Visibility, Low-Connection anomalies flagged: {anomalies}")
    return 0


COMMANDS = {
    "verify": cmd_verify,
    "ga4-landing-pages": cmd_ga4_landing_pages,
    "ga4-key-events": cmd_ga4_key_events,
    "gsc-queries": cmd_gsc_queries,
    "gsc-pages": cmd_gsc_pages,
    "gsc-inspect": cmd_gsc_inspect,
    "gsc-sitemap": cmd_gsc_sitemap,
    "reconcile": cmd_reconcile,
    "export-all": cmd_export_all,
}


def main(argv: Optional[list[str]] = None) -> None:
    args = build_parser().parse_args(argv)
    handler = COMMANDS[args.command]
    try:
        exit_code = handler(args)
    except (ConfigError, AuthError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    except Exception as exc:  # GA4Error / GSCError carry remediation text already
        from seo_export.ga4 import GA4Error
        from seo_export.gsc import GSCError

        if isinstance(exc, (GA4Error, GSCError)):
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(2)
        raise
    sys.exit(exit_code)
