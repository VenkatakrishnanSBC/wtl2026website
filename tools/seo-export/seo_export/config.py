"""Configuration loading and validation.

Reads GA4_PROPERTY_ID and GSC_SITE_URL from a ``.env`` file (via python-dotenv) or
the process environment. Fails fast with actionable messages when values are missing.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency guard
    load_dotenv = None  # type: ignore[assignment]


# Default lookback window when --start/--end are omitted.
DEFAULT_LOOKBACK_DAYS = 90


class ConfigError(Exception):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class Config:
    """Resolved runtime configuration.

    Attributes:
        ga4_property_id: Numeric GA4 property ID (NOT the G-XXXX measurement ID).
        gsc_site_url: GSC property, either a URL-prefix (``https://example.com/``)
            or a domain property (``sc-domain:example.com``).
        credentials_path: Optional explicit path to a service-account JSON key.
            When None, Application Default Credentials (ADC) are used, typically
            via the GOOGLE_APPLICATION_CREDENTIALS env var.
    """

    ga4_property_id: str
    gsc_site_url: str
    credentials_path: Optional[str] = None
    oauth_access_token: Optional[str] = None
    quota_project: Optional[str] = None


def load_config(
    credentials_override: Optional[str] = None,
    env_file: Optional[str] = None,
    token_override: Optional[str] = None,
) -> Config:
    """Load and validate configuration from .env / environment.

    Args:
        credentials_override: Path passed via ``--credentials`` to override ADC.
        env_file: Optional explicit path to a .env file. Defaults to a ``.env``
            next to this tool's root.

    Returns:
        A validated :class:`Config`.

    Raises:
        ConfigError: If GA4_PROPERTY_ID or GSC_SITE_URL is missing/invalid, or a
            supplied credentials path does not exist.
    """
    if load_dotenv is not None:
        if env_file:
            load_dotenv(env_file)
        else:
            # Default: tools/seo-export/.env
            default_env = Path(__file__).resolve().parent.parent / ".env"
            if default_env.exists():
                load_dotenv(default_env)

    ga4_property_id = (os.getenv("GA4_PROPERTY_ID") or "").strip()
    gsc_site_url = (os.getenv("GSC_SITE_URL") or "").strip()

    missing = []
    if not ga4_property_id:
        missing.append("GA4_PROPERTY_ID")
    if not gsc_site_url:
        missing.append("GSC_SITE_URL")
    if missing:
        raise ConfigError(
            "Missing required configuration: "
            + ", ".join(missing)
            + ".\n\nFix: create a .env file (copy .env.example) in tools/seo-export/ "
            "and set these values. See README.md 'Configuration'.\n"
            "  - GA4_PROPERTY_ID is the NUMERIC property id (e.g. 123456789), found in\n"
            "    GA4 Admin -> Property Settings -> Property ID (NOT the G-XXXX id).\n"
            "  - GSC_SITE_URL is either 'https://worldtransgroup.com/' (URL-prefix) or\n"
            "    'sc-domain:worldtransgroup.com' (domain property)."
        )

    # GA4 property id must be numeric; reject the common mistake of pasting G-XXXX.
    if not ga4_property_id.isdigit():
        raise ConfigError(
            f"GA4_PROPERTY_ID='{ga4_property_id}' is not numeric. The GA4 Data API "
            "requires the numeric Property ID (e.g. 123456789), not the measurement "
            "id 'G-QVG2LR3XV1'. Find it in GA4 Admin -> Property Settings -> Property ID."
        )

    # Token-based auth (OAuth Playground model) takes precedence over key files.
    oauth_access_token = (token_override or os.getenv("OAUTH_ACCESS_TOKEN") or "").strip() or None
    quota_project = (os.getenv("QUOTA_PROJECT") or "").strip() or None

    credentials_path = credentials_override or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if credentials_path and not oauth_access_token:
        if not Path(credentials_path).exists():
            raise ConfigError(
                f"Service-account credentials file not found: {credentials_path}\n"
                "Fix: pass a valid path with --credentials, set "
                "GOOGLE_APPLICATION_CREDENTIALS to your service-account JSON key, "
                "or use token auth via OAUTH_ACCESS_TOKEN / --access-token."
            )

    return Config(
        ga4_property_id=ga4_property_id,
        gsc_site_url=gsc_site_url,
        credentials_path=credentials_path,
        oauth_access_token=oauth_access_token,
        quota_project=quota_project,
    )


def default_date_range() -> tuple[str, str]:
    """Return (start, end) ISO dates for the default lookback window.

    End is yesterday (GA4/GSC data for "today" is incomplete); start is
    ``DEFAULT_LOOKBACK_DAYS`` before end, inclusive.
    """
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=DEFAULT_LOOKBACK_DAYS - 1)
    return start.isoformat(), end.isoformat()
