"""Service-account authentication for the GA4 Data API and GSC Search Console API.

Uses google-auth Application Default Credentials (ADC) by default — set
GOOGLE_APPLICATION_CREDENTIALS to your service-account JSON key — or an explicit
``--credentials path.json`` override. The same service account must be granted
read access in BOTH GA4 (Property Access Management) and GSC (Users and permissions).
"""

from __future__ import annotations

from typing import Optional

# Read-only scopes. GA4 Data API needs analytics.readonly; GSC needs webmasters.readonly.
GA4_SCOPES = ("https://www.googleapis.com/auth/analytics.readonly",)
GSC_SCOPES = ("https://www.googleapis.com/auth/webmasters.readonly",)
# Read-WRITE GSC scope — required to SUBMIT a sitemap (sitemaps.submit). The
# readonly scope can list sitemaps but not submit; a token must be minted with
# this scope for `gsc-sitemap --resubmit` to work.
GSC_WRITE_SCOPES = ("https://www.googleapis.com/auth/webmasters",)
ALL_SCOPES = tuple(set(GA4_SCOPES) | set(GSC_SCOPES))


class AuthError(Exception):
    """Raised when credentials cannot be loaded."""


GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"


def credentials_for(config, scopes: tuple[str, ...]):
    """Resolve credentials from a Config, by precedence:

    1. **Refresh token** (all-time): if client_id + client_secret + refresh_token
       are all set, build self-refreshing OAuth2 credentials. google-auth mints a
       fresh access token automatically whenever the current one expires — no
       hourly re-paste. This is the permanent path; the refresh token comes from a
       one-time consent against the user's OWN OAuth client.
    2. **Access token**: a raw ``ya29...`` bearer token (OAuth Playground default
       client). Expires ~1h; convenient but not all-time.
    3. **Service account / ADC**: key file or Application Default Credentials.
    """
    quota_project = getattr(config, "quota_project", None)

    client_id = getattr(config, "oauth_client_id", None)
    client_secret = getattr(config, "oauth_client_secret", None)
    refresh_token = getattr(config, "oauth_refresh_token", None)
    token = getattr(config, "oauth_access_token", None)

    if client_id and client_secret and refresh_token:
        try:
            from google.oauth2.credentials import Credentials as UserCredentials
        except ImportError as exc:  # pragma: no cover - dependency guard
            raise AuthError(
                "google-auth is not installed. Run: pip install -r requirements.txt"
            ) from exc
        creds = UserCredentials(
            token=token or None,  # may be None; refreshed on first use
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            token_uri=GOOGLE_TOKEN_URI,
            scopes=list(scopes),
        )
        if quota_project:
            creds = creds.with_quota_project(quota_project)
        return creds

    if token:
        try:
            from google.oauth2.credentials import Credentials as UserCredentials
        except ImportError as exc:  # pragma: no cover - dependency guard
            raise AuthError(
                "google-auth is not installed. Run: pip install -r requirements.txt"
            ) from exc
        creds = UserCredentials(token=token)
        if quota_project:
            creds = creds.with_quota_project(quota_project)
        return creds

    creds = load_credentials(config.credentials_path, scopes)
    if quota_project and hasattr(creds, "with_quota_project"):
        creds = creds.with_quota_project(quota_project)
    return creds


def load_credentials(credentials_path: Optional[str], scopes: tuple[str, ...]):
    """Load service-account credentials with the given scopes.

    Args:
        credentials_path: Explicit path to a service-account JSON key, or None to
            use ADC (GOOGLE_APPLICATION_CREDENTIALS / gcloud default).
        scopes: OAuth scopes to request.

    Returns:
        A ``google.auth.credentials.Credentials`` object.

    Raises:
        AuthError: When no credentials can be located, with setup guidance.
    """
    try:
        from google.oauth2 import service_account  # local import keeps CLI --help fast
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise AuthError(
            "google-auth is not installed. Run: pip install -r requirements.txt"
        ) from exc

    if credentials_path:
        try:
            return service_account.Credentials.from_service_account_file(
                credentials_path, scopes=list(scopes)
            )
        except Exception as exc:  # noqa: BLE001
            raise AuthError(
                f"Failed to load service-account key from {credentials_path}: {exc}"
            ) from exc

    # Fall back to ADC.
    try:
        import google.auth

        creds, _project = google.auth.default(scopes=list(scopes))
        return creds
    except Exception as exc:  # noqa: BLE001
        raise AuthError(
            "No credentials found. Set GOOGLE_APPLICATION_CREDENTIALS to a "
            "service-account JSON key, or pass --credentials path.json.\n"
            "See README.md 'Authentication setup'."
        ) from exc


def service_account_email(credentials_path: Optional[str]) -> Optional[str]:
    """Return the service-account email from the key file, if available.

    Used by error messages and ``verify`` so the user knows exactly which email to
    grant access to in GA4/GSC.
    """
    if not credentials_path:
        return None
    try:
        import json

        with open(credentials_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data.get("client_email")
    except Exception:  # noqa: BLE001 - non-fatal, only for nicer messages
        return None
